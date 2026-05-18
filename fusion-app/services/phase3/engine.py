from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from .audit import Phase3AuditLogger
from .catalog import OBJECT_CATALOG, ObjectDefinition
from .scanner import discover_files
from .utils import canonical_column_name, ensure_dir, is_empty, new_id, normalize_value, now_iso
from .writer import bundle_run_directory, write_dat, write_json, write_rejected_csv

from ..object_lookup import ObjectLookup


@dataclass
class CleanRecord:
    run_id: str
    object_name: str
    source_file: str
    relative_source_file: str
    source_row_number: int
    row_data: Dict[str, Any]
    row_id: str = field(default_factory=lambda: new_id("ROW"))


@dataclass
class ValidationIssue:
    validation_id: str
    run_id: str
    object_name: str
    source_file: str
    relative_source_file: str
    source_row_number: Optional[int]
    error_code: str
    field_name: Optional[str]
    message: str
    row_values: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FileSummary:
    source_file: str
    relative_source_file: str
    object_name: Optional[str]
    resolved_by: str
    status: str
    rows_read: int = 0
    valid_rows: int = 0
    rejected_rows: int = 0
    issues: List[Dict[str, Any]] = field(default_factory=list)
    valid_records: List[CleanRecord] = field(default_factory=list)
    rejected_row_payloads: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ObjectSummary:
    object_name: str
    source_files: List[str] = field(default_factory=list)
    files_processed: int = 0
    rows_read: int = 0
    valid_rows: int = 0
    rejected_rows: int = 0
    output_dat: Optional[str] = None
    rejected_csv: Optional[str] = None
    file_summaries: List[Dict[str, Any]] = field(default_factory=list)
    issues: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class RunResult:
    source_file: str
    relative_source_file: str
    object_name: Optional[str]
    resolved_by: str
    status: str
    rows_read: int = 0
    valid_rows: int = 0
    rejected_rows: int = 0
    issues: List[Dict[str, Any]] = field(default_factory=list)
    valid_records: List[CleanRecord] = field(default_factory=list)
    rejected_row_payloads: List[Dict[str, Any]] = field(default_factory=list)


def process_folder(root_folder: Path, output_mode: str = "flat") -> Dict[str, Any]:
    root_folder = root_folder.expanduser().resolve()
    if not root_folder.exists():
        raise FileNotFoundError(f"Folder not found: {root_folder}")
    if not root_folder.is_dir():
        raise NotADirectoryError(f"Path is not a folder: {root_folder}")

    run_id = new_id("RUN")
    app_root = Path(__file__).resolve().parents[2]
    run_dir = ensure_dir(app_root / "phase3_output" / run_id)

    if output_mode == "mirrored":
        dat_dir = ensure_dir(run_dir / "mirrored" / "dat")
        rejected_dir = ensure_dir(run_dir / "mirrored" / "rejected")
    else:
        dat_dir = ensure_dir(run_dir / "dat")
        rejected_dir = ensure_dir(run_dir / "rejected")

    audit_dir = ensure_dir(run_dir / "audit")
    summary_dir = ensure_dir(run_dir / "summary")

    audit_logger = Phase3AuditLogger(audit_dir / "audit.jsonl", run_id)
    audit_logger.log(
        "RUN_STARTED",
        f"Phase 3 scan started for {root_folder}",
        extra={"output_mode": output_mode},
    )

    # Initialize reusable lookup service once per run (uses central FUSION_CONFIG only)
    lookup_service = ObjectLookup()

    discovered = discover_files(root_folder, OBJECT_CATALOG)
    audit_logger.log(
        "FILES_DISCOVERED",
        f"Discovered {len(discovered)} file(s)",
        extra={"count": len(discovered)},
    )

    object_candidates: Dict[str, List[CleanRecord]] = defaultdict(list)
    object_rejected_rows: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    object_summaries: Dict[str, ObjectSummary] = {}
    file_summaries: List[Dict[str, Any]] = []
    all_issues: List[Dict[str, Any]] = []
    unknown_files: List[Dict[str, Any]] = []

    for discovered_file in discovered:
        file_result = process_single_file(
            run_id=run_id,
            discovered_file=discovered_file,
            audit_logger=audit_logger,
            lookup_service=lookup_service,
        )

        file_public = asdict(file_result)
        file_public.pop("valid_records", None)
        file_public.pop("rejected_row_payloads", None)
        file_summaries.append(file_public)
        all_issues.extend(file_result.issues)

        if file_result.object_name is None:
            unknown_files.append(file_public)
            continue

        object_name = file_result.object_name
        object_summaries.setdefault(object_name, ObjectSummary(object_name=object_name))
        obj_summary = object_summaries[object_name]
        obj_summary.source_files.append(file_result.relative_source_file)
        obj_summary.files_processed += 1
        obj_summary.rows_read += file_result.rows_read
        obj_summary.valid_rows += file_result.valid_rows
        obj_summary.rejected_rows += file_result.rejected_rows
        obj_summary.file_summaries.append(file_public)
        obj_summary.issues.extend(file_result.issues)

        object_candidates[object_name].extend(file_result.valid_records)
        object_rejected_rows[object_name].extend(file_result.rejected_row_payloads)

    # Object-level duplicate detection across all files of the same object
    for object_name, candidates in object_candidates.items():
        definition = OBJECT_CATALOG[object_name]
        duplicate_payloads, duplicate_issues = detect_object_duplicates(
            run_id=run_id,
            object_name=object_name,
            candidates=candidates,
            definition=definition,
            audit_logger=audit_logger,
        )

        if duplicate_payloads:
            object_rejected_rows[object_name].extend(duplicate_payloads)
        if duplicate_issues:
            all_issues.extend(duplicate_issues)

        duplicate_row_ids = {row["row_id"] for row in duplicate_payloads if "row_id" in row}
        clean_candidates = [row for row in candidates if row.row_id not in duplicate_row_ids]

        dat_rows = [render_dat_row(record.row_data, definition) for record in clean_candidates]
        rejected_rows = object_rejected_rows.get(object_name, [])

        if dat_rows:
            dat_path = (
                dat_dir / object_name / f"{object_name}.dat"
                if output_mode == "mirrored"
                else dat_dir / f"{object_name}.dat"
            )
            write_dat(dat_path, definition.output_header, dat_rows)
            object_summaries[object_name].output_dat = str(dat_path)
            audit_logger.log(
                "DAT_WRITTEN",
                f"Generated {dat_path.name}",
                object_name=object_name,
                extra={"path": str(dat_path), "rows": len(dat_rows)},
            )

        if rejected_rows:
            rejected_path = (
                rejected_dir / object_name / f"{object_name}_rejected.csv"
                if output_mode == "mirrored"
                else rejected_dir / f"{object_name}_rejected.csv"
            )
            write_rejected_csv(rejected_path, rejected_rows)
            object_summaries[object_name].rejected_csv = str(rejected_path)
            audit_logger.log(
                "REJECTED_WRITTEN",
                f"Generated {rejected_path.name}",
                object_name=object_name,
                extra={"path": str(rejected_path), "rows": len(rejected_rows)},
            )

        object_summaries[object_name].valid_rows = len(dat_rows)
        object_summaries[object_name].rejected_rows = len(rejected_rows)

    total_rows_read = sum(item.rows_read for item in object_summaries.values())
    total_valid_rows = sum(item.valid_rows for item in object_summaries.values())
    total_rejected_rows = sum(item.rejected_rows for item in object_summaries.values())

    run_status = "success" if total_valid_rows > 0 else ("warning" if discovered else "error")

    summary = {
        "status": run_status,
        "run_id": run_id,
        "root_folder": str(root_folder),
        "output_mode": output_mode,
        "started_at": now_iso(),
        "ended_at": now_iso(),
        "totals": {
            "files_discovered": len(discovered),
            "files_processed": len(file_summaries),
            "objects_detected": len(object_summaries),
            "rows_read": total_rows_read,
            "rows_valid": total_valid_rows,
            "rows_rejected": total_rejected_rows,
            "dat_files": len([o for o in object_summaries.values() if o.output_dat]),
            "rejected_files": len([o for o in object_summaries.values() if o.rejected_csv]),
            "unknown_files": len(unknown_files),
        },
        "objects": {name: asdict(summary_obj) for name, summary_obj in object_summaries.items()},
        "files": file_summaries,
        "unknown_files": unknown_files,
        "validation_issues": all_issues,
        "output": {
            "run_dir": str(run_dir),
            "dat_dir": str(dat_dir),
            "rejected_dir": str(rejected_dir),
            "audit_log": str(audit_dir / "audit.jsonl"),
            "summary_json": str(summary_dir / "summary.json"),
            "bundle_zip": str(run_dir / f"{run_id}_bundle.zip"),
        },
    }

    summary["download_url"] = f"/phase3/runs/{run_id}/bundle"
    summary["summary_url"] = f"/phase3/runs/{run_id}/summary"
    summary["catalog_url"] = "/phase3/catalog"

    write_json(summary_dir / "summary.json", summary)
    bundle_run_directory(run_dir, run_dir / f"{run_id}_bundle.zip")
    audit_logger.log(
        "RUN_COMPLETED",
        f"Run {run_id} completed",
        extra={"summary_path": summary["output"]["summary_json"]},
    )
    return summary


def process_single_file(
    run_id: str,
    discovered_file,
    audit_logger: Phase3AuditLogger,
    lookup_service: ObjectLookup,
) -> RunResult:
    source_path = discovered_file.path
    object_name = discovered_file.object_name
    relative_source_file = discovered_file.relative_path

    if object_name is None:
        issue = ValidationIssue(
            validation_id=new_id("VAL"),
            run_id=run_id,
            object_name="Unknown",
            source_file=str(source_path),
            relative_source_file=relative_source_file,
            source_row_number=None,
            error_code="OBJECT_NOT_RECOGNIZED",
            field_name=None,
            message="Unable to resolve target object for this file from path or file name.",
            row_values={"file": source_path.name},
        )
        audit_logger.log(
            "FILE_UNRESOLVED",
            issue.message,
            level="WARNING",
            source_file=str(source_path),
            extra=issue.to_dict(),
        )
        return RunResult(
            source_file=str(source_path),
            relative_source_file=relative_source_file,
            object_name=None,
            resolved_by=discovered_file.object_match_source,
            status="unresolved",
            issues=[issue.to_dict()],
        )

    definition = OBJECT_CATALOG[object_name]
    audit_logger.log(
        "FILE_CLASSIFIED",
        f"File mapped to {object_name}",
        object_name=object_name,
        source_file=str(source_path),
        extra={"relative_path": relative_source_file, "match_source": discovered_file.object_match_source},
    )

    try:
        if source_path.suffix.lower() == ".xlsx":
            df = pd.read_excel(source_path)
        else:
            df = pd.read_csv(source_path, encoding="utf-8")
    except UnicodeDecodeError as exc:
        issue = ValidationIssue(
            validation_id=new_id("VAL"),
            run_id=run_id,
            object_name=object_name,
            source_file=str(source_path),
            relative_source_file=relative_source_file,
            source_row_number=None,
            error_code="CSV_DECODE_ERROR",
            field_name=None,
            message="CSV file could not be decoded as UTF-8.",
            row_values={"error": str(exc)},
        )
        audit_logger.log(
            "FILE_READ_ERROR",
            issue.message,
            level="ERROR",
            object_name=object_name,
            source_file=str(source_path),
            extra=issue.to_dict(),
        )
        return RunResult(
            source_file=str(source_path),
            relative_source_file=relative_source_file,
            object_name=object_name,
            resolved_by=discovered_file.object_match_source,
            status="error",
            issues=[issue.to_dict()],
        )
    except Exception as exc:
        issue = ValidationIssue(
            validation_id=new_id("VAL"),
            run_id=run_id,
            object_name=object_name,
            source_file=str(source_path),
            relative_source_file=relative_source_file,
            source_row_number=None,
            error_code="FILE_READ_ERROR",
            field_name=None,
            message=f"Error reading file: {exc}",
            row_values={"error": str(exc)},
        )
        audit_logger.log(
            "FILE_READ_ERROR",
            issue.message,
            level="ERROR",
            object_name=object_name,
            source_file=str(source_path),
            extra=issue.to_dict(),
        )
        return RunResult(
            source_file=str(source_path),
            relative_source_file=relative_source_file,
            object_name=object_name,
            resolved_by=discovered_file.object_match_source,
            status="error",
            issues=[issue.to_dict()],
        )

    df = normalize_columns(df, definition)
    rows_read = len(df)
    audit_logger.log(
        "FILE_PARSED",
        f"Parsed {rows_read} row(s)",
        object_name=object_name,
        source_file=str(source_path),
        extra={"columns": list(df.columns)},
    )

    file_issues: List[Dict[str, Any]] = []
    valid_records: List[CleanRecord] = []
    rejected_payloads: List[Dict[str, Any]] = []

    required_missing = [col for col in definition.required_columns if col not in df.columns]
    if required_missing:
        for idx, row in df.iterrows():
            row_num = int(idx) + 2
            row_dict = row.to_dict()
            issue = ValidationIssue(
                validation_id=new_id("VAL"),
                run_id=run_id,
                object_name=object_name,
                source_file=str(source_path),
                relative_source_file=relative_source_file,
                source_row_number=row_num,
                error_code="MISSING_REQUIRED_COLUMNS",
                field_name=", ".join(required_missing),
                message=f"Row {row_num}: missing required columns: {', '.join(required_missing)}",
                row_values=row_dict,
            )
            file_issues.append(issue.to_dict())
            rejected_payloads.append(
                {
                    "validation_id": issue.validation_id,
                    "run_id": run_id,
                    "object_name": object_name,
                    "source_file": str(source_path),
                    "relative_source_file": relative_source_file,
                    "source_row_number": row_num,
                    "error_code": issue.error_code,
                    "field_name": issue.field_name,
                    "message": issue.message,
                    "row_values": row_dict,
                    "row_id": None,
                }
            )
            audit_logger.log(
                "ROW_VALIDATION_FAILED",
                issue.message,
                level="WARNING",
                object_name=object_name,
                source_file=str(source_path),
                extra=issue.to_dict(),
            )

        return RunResult(
            source_file=str(source_path),
            relative_source_file=relative_source_file,
            object_name=object_name,
            resolved_by=discovered_file.object_match_source,
            status="processed",
            rows_read=rows_read,
            valid_rows=0,
            rejected_rows=len(rejected_payloads),
            issues=file_issues,
            valid_records=[],
            rejected_row_payloads=rejected_payloads,
        )

    for idx, row in df.iterrows():
        row_num = int(idx) + 2  # header row assumed as row 1
        row_dict = row.to_dict()
        issues_for_row: List[ValidationIssue] = []
        clean_row: Dict[str, Any] = {}

        for col in definition.all_columns:
            is_date = col in definition.date_columns
            clean_row[col] = normalize_value(row_dict.get(col, ""), is_date=is_date)

        # Required field checks
        for col in definition.required_columns:
            if is_empty(row_dict.get(col, "")):
                issues_for_row.append(
                    ValidationIssue(
                        validation_id=new_id("VAL"),
                        run_id=run_id,
                        object_name=object_name,
                        source_file=str(source_path),
                        relative_source_file=relative_source_file,
                        source_row_number=row_num,
                        error_code="REQUIRED_FIELD_MISSING",
                        field_name=col,
                        message=f"Row {row_num}: {col} is missing",
                        row_values=row_dict,
                    )
                )

        # Date validation checks
        for col in definition.date_columns:
            value = row_dict.get(col, "")
            if is_empty(value):
                continue
            parsed = pd.to_datetime(value, errors="coerce")
            if pd.isna(parsed):
                issues_for_row.append(
                    ValidationIssue(
                        validation_id=new_id("VAL"),
                        run_id=run_id,
                        object_name=object_name,
                        source_file=str(source_path),
                        relative_source_file=relative_source_file,
                        source_row_number=row_num,
                        error_code="INVALID_DATE",
                        field_name=col,
                        message=f"Row {row_num}: Invalid date in {col}",
                        row_values=row_dict,
                    )
                )
            else:
                clean_row[col] = parsed.strftime("%Y-%m-%d")

        if issues_for_row:
            for issue in issues_for_row:
                file_issues.append(issue.to_dict())
                rejected_payloads.append(
                    {
                        "validation_id": issue.validation_id,
                        "run_id": run_id,
                        "object_name": object_name,
                        "source_file": str(source_path),
                        "relative_source_file": relative_source_file,
                        "source_row_number": row_num,
                        "error_code": issue.error_code,
                        "field_name": issue.field_name,
                        "message": issue.message,
                        "row_values": row_dict,
                        "row_id": None,
                    }
                )
                audit_logger.log(
                    "ROW_VALIDATION_FAILED",
                    issue.message,
                    level="WARNING",
                    object_name=object_name,
                    source_file=str(source_path),
                    extra=issue.to_dict(),
                )
        else:
            # === NEW: Additional Fusion HCM SaaS existence check (post-local validation) ===
            # This is the requested extra layer. It does NOT replace local rules, duplicate
            # detection, or HDL generation. Failures are logged as warnings (per-row, non-blocking).
            # Only records that pass local validation AND do not already exist in Fusion
            # are kept for HDL output.
            lookup_result = lookup_service.check_record_exists(object_name, clean_row)

            if lookup_result.get("fusion_exists", False):
                issue = ValidationIssue(
                    validation_id=new_id("VAL"),
                    run_id=run_id,
                    object_name=object_name,
                    source_file=str(source_path),
                    relative_source_file=relative_source_file,
                    source_row_number=row_num,
                    error_code="ALREADY_EXISTS_IN_FUSION",
                    field_name=None,
                    message=lookup_result.get(
                        "message", f"Row {row_num}: Record already exists in Fusion"
                    ),
                    row_values=row_dict,
                )
                issues_for_row.append(issue)
                file_issues.append(issue.to_dict())
                rejected_payloads.append(
                    {
                        "validation_id": issue.validation_id,
                        "run_id": run_id,
                        "object_name": object_name,
                        "source_file": str(source_path),
                        "relative_source_file": relative_source_file,
                        "source_row_number": row_num,
                        "error_code": issue.error_code,
                        "field_name": issue.field_name,
                        "message": issue.message,
                        "row_values": row_dict,
                        "row_id": None,
                        "fusion_lookup": lookup_result,
                    }
                )
                audit_logger.log(
                    "ROW_ALREADY_EXISTS_IN_FUSION",
                    issue.message,
                    level="WARNING",
                    object_name=object_name,
                    source_file=str(source_path),
                    extra={**issue.to_dict(), "fusion_lookup": lookup_result},
                )
            elif not lookup_result.get("lookup_success", True):
                # Lookup failure is a per-row warning (non-blocking, as specified)
                audit_logger.log(
                    "FUSION_LOOKUP_WARNING",
                    lookup_result.get("message", "Fusion lookup failed"),
                    level="WARNING",
                    object_name=object_name,
                    source_file=str(source_path),
                    extra={"row_num": row_num, "fusion_lookup": lookup_result},
                )
            # If lookup succeeded and record does NOT exist, or was a warning only,
            # the row remains valid for HDL generation (existing behavior preserved).

            if not issues_for_row:  # re-check after possible Fusion issue
                valid_records.append(
                    CleanRecord(
                        run_id=run_id,
                        object_name=object_name,
                        source_file=str(source_path),
                        relative_source_file=relative_source_file,
                        source_row_number=row_num,
                        row_data=clean_row,
                    )
                )

    return RunResult(
        source_file=str(source_path),
        relative_source_file=relative_source_file,
        object_name=object_name,
        resolved_by=discovered_file.object_match_source,
        status="processed",
        rows_read=rows_read,
        valid_rows=len(valid_records),
        rejected_rows=len(rejected_payloads),
        issues=file_issues,
        valid_records=valid_records,
        rejected_row_payloads=rejected_payloads,
    )


def normalize_columns(df: pd.DataFrame, definition: ObjectDefinition) -> pd.DataFrame:
    normalized_lookup: Dict[str, str] = definition.normalized_columns
    renamed: Dict[str, str] = {}
    for actual_col in df.columns:
        key = canonical_column_name(actual_col)
        if key in normalized_lookup:
            renamed[actual_col] = normalized_lookup[key]
        else:
            renamed[actual_col] = actual_col.strip().replace(" ", "_")
    return df.rename(columns=renamed)


def detect_object_duplicates(
    run_id: str,
    object_name: str,
    candidates: List[CleanRecord],
    definition: ObjectDefinition,
    audit_logger: Phase3AuditLogger,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    if not definition.unique_columns or not candidates:
        return [], []

    grouped: Dict[Tuple[Any, ...], List[CleanRecord]] = defaultdict(list)
    for record in candidates:
        key = tuple(record.row_data.get(col, "") for col in definition.unique_columns)
        grouped[key].append(record)

    rejected_payloads: List[Dict[str, Any]] = []
    issues: List[Dict[str, Any]] = []

    for _, rows in grouped.items():
        if len(rows) <= 1:
            continue

        for record in rows:
            issue = ValidationIssue(
                validation_id=new_id("VAL"),
                run_id=run_id,
                object_name=object_name,
                source_file=record.source_file,
                relative_source_file=record.relative_source_file,
                source_row_number=record.source_row_number,
                error_code="DUPLICATE_UNIQUE_KEY",
                field_name=", ".join(definition.unique_columns),
                message=f"Row {record.source_row_number}: Duplicate {', '.join(definition.unique_columns)}",
                row_values=record.row_data,
            )
            issues.append(issue.to_dict())
            rejected_payloads.append(
                {
                    "validation_id": issue.validation_id,
                    "run_id": run_id,
                    "object_name": object_name,
                    "source_file": record.source_file,
                    "relative_source_file": record.relative_source_file,
                    "source_row_number": record.source_row_number,
                    "error_code": issue.error_code,
                    "field_name": issue.field_name,
                    "message": issue.message,
                    "row_values": record.row_data,
                    "row_id": record.row_id,
                }
            )
            audit_logger.log(
                "DUPLICATE_DETECTED",
                issue.message,
                level="WARNING",
                object_name=object_name,
                source_file=record.source_file,
                extra=issue.to_dict(),
            )

    return rejected_payloads, issues


def render_dat_row(row_data: Dict[str, Any], definition: ObjectDefinition) -> str:
    values = {
        key: normalize_value(row_data.get(key, ""), is_date=(key in definition.date_columns))
        for key in definition.all_columns
    }
    for col in definition.all_columns:
        values.setdefault(col, "")
    return definition.output_template.format(**values)
