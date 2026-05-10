from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .catalog import ObjectDefinition, get_object_catalog
from .hdl_writer import write_dat
from .processor import map_columns, normalize, read_file, validate
from .scanner import discover_files


def run_batch(root_folder: str) -> Dict[str, Any]:
    root_path = Path(root_folder).resolve()

    if not root_path.exists():
        raise FileNotFoundError(f"Input folder not found: {root_path}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder = root_path / f"output_{timestamp}"
    output_folder.mkdir(parents=True, exist_ok=True)

    catalog = get_object_catalog()
    files = discover_files(root_path, catalog)

    summary: Dict[str, Any] = {
        "input_folder": str(root_path),
        "output_folder": str(output_folder),
        "total_files": len(files),
        "processed_files": 0,
        "skipped_files": 0,
        "errors": [],
        "objects": {},
        "objects_errors": {},
    }

    for discovered in files:
        if not discovered.object_name:
            summary["skipped_files"] += 1
            summary["errors"].append(
                f"Skipped {discovered.relative_path}: No matching object type found"
            )
            continue

        obj: ObjectDefinition = catalog[discovered.object_name]

        summary["objects"].setdefault(obj.name, {"files": 0, "processed": 0, "errors": 0})
        summary["objects"][obj.name]["files"] += 1

        file_summary = {
            "file_name": str(discovered.relative_path),
            "total_rows": 0,
            "valid_rows": 0,
            "error_rows": 0,
            "status": "error",
            "validation_errors": [],
            "generation_error": None,
            "detailed_errors": [],
        }

        try:
            # Step 1: Read file
            try:
                df = read_file(discovered.path)
                file_summary["total_rows"] = len(df)
            except Exception as exc:
                error_msg = f"Failed to read file: {str(exc)}"
                file_summary["detailed_errors"].append(
                    {"row": None, "column": "File Read", "message": error_msg}
                )
                summary["objects"][obj.name]["errors"] += 1
                summary["errors"].append(f"{discovered.relative_path}: {error_msg}")
                file_summary["error_rows"] = 1
                file_summary["status"] = "error"
                summary["objects_errors"].setdefault(obj.name, []).append(file_summary)
                continue

            # Step 2: Normalize data
            try:
                df = normalize(df)
            except Exception as exc:
                error_msg = f"Failed to normalize data: {str(exc)}"
                file_summary["detailed_errors"].append(
                    {"row": None, "column": "Normalization", "message": error_msg}
                )
                summary["objects"][obj.name]["errors"] += 1
                summary["errors"].append(f"{discovered.relative_path}: {error_msg}")
                file_summary["error_rows"] = file_summary["total_rows"]
                file_summary["status"] = "error"
                summary["objects_errors"].setdefault(obj.name, []).append(file_summary)
                continue

            # Step 3: Map columns
            try:
                mapped_df = map_columns(df, obj)
            except Exception as exc:
                error_msg = f"Failed to map columns: {str(exc)}"
                file_summary["detailed_errors"].append(
                    {"row": None, "column": "Column Mapping", "message": error_msg}
                )
                summary["objects"][obj.name]["errors"] += 1
                summary["errors"].append(f"{discovered.relative_path}: {error_msg}")
                file_summary["error_rows"] = file_summary["total_rows"]
                file_summary["status"] = "error"
                summary["objects_errors"].setdefault(obj.name, []).append(file_summary)
                continue

            # Step 4: Validate data
            validation_errors = []
            try:
                validation_errors = validate(mapped_df, obj)
                file_summary["validation_errors"] = validation_errors[:]
                summary["objects"][obj.name]["errors"] += len(validation_errors)

                for err in validation_errors:
                    row_info = f"Row {err.get('row', 'N/A')}: " if err.get("row") else ""
                    col_info = f"{err['column']}: "
                    summary["errors"].append(
                        f"{discovered.relative_path}: {row_info}{col_info}{err['message']}"
                    )
            except Exception as exc:
                error_msg = f"Failed to validate data: {str(exc)}"
                file_summary["detailed_errors"].append(
                    {"row": None, "column": "Validation", "message": error_msg}
                )
                summary["objects"][obj.name]["errors"] += 1
                summary["errors"].append(f"{discovered.relative_path}: {error_msg}")
                file_summary["error_rows"] = file_summary["total_rows"]
                file_summary["status"] = "error"
                summary["objects_errors"].setdefault(obj.name, []).append(file_summary)
                continue

            file_summary["detailed_errors"] = validation_errors[:]

            if validation_errors:
                file_summary["status"] = "partial"
                file_summary["valid_rows"] = file_summary["total_rows"] - len(validation_errors)
                file_summary["error_rows"] = len(validation_errors)
            else:
                file_summary["status"] = "success"
                file_summary["valid_rows"] = file_summary["total_rows"]
                file_summary["error_rows"] = 0

            # Step 5: Write output if no errors or partial
            file_summary["generation_error"] = None
            try:
                clean_df = mapped_df if not validation_errors else pd.DataFrame(columns=mapped_df.columns)
                write_dat(
                    clean_df,
                    obj,
                    output_folder,
                    source_name=discovered.path.stem,
                )
                summary["objects"][obj.name]["processed"] += 1
                summary["processed_files"] += 1
            except Exception as exc:
                error_msg = f"Failed to generate HDL file: {str(exc)}"
                file_summary["generation_error"] = error_msg
                file_summary["detailed_errors"].append(
                    {"row": None, "column": "HDL Generation", "message": error_msg}
                )
                summary["objects"][obj.name]["errors"] += 1
                summary["errors"].append(f"{discovered.relative_path}: {error_msg}")
                file_summary["status"] = "error"

            # Finalize counts based on status
            if file_summary["status"] == "error":
                file_summary["valid_rows"] = 0
                file_summary["error_rows"] = file_summary["total_rows"] if file_summary["total_rows"] > 0 else 1
            elif file_summary["status"] == "partial":
                file_summary["valid_rows"] = file_summary["total_rows"] - len(file_summary["validation_errors"])
                file_summary["error_rows"] = len(file_summary["validation_errors"])
            else:
                file_summary["valid_rows"] = file_summary["total_rows"]
                file_summary["error_rows"] = 0

            summary["objects_errors"].setdefault(obj.name, []).append(file_summary)

        except Exception as exc:
            # Top-level catch for unexpected errors
            error_msg = f"Unexpected error processing file: {str(exc)}"
            summary["errors"].append(f"{discovered.relative_path}: {error_msg}")
            summary["objects"][obj.name]["errors"] += 1
            file_summary["status"] = "error"
            file_summary["detailed_errors"].append(
                {"row": None, "column": "Unexpected", "message": error_msg}
            )
            file_summary["valid_rows"] = 0
            file_summary["error_rows"] = file_summary["total_rows"] if file_summary["total_rows"] > 0 else 1
            summary["objects_errors"].setdefault(obj.name, []).append(file_summary)

    # Compute aggregate summaries per object
    for obj_name, file_summaries in summary["objects_errors"].items():
        obj_stats = summary["objects"][obj_name]
        obj_stats["total_rows"] = sum(fs["total_rows"] for fs in file_summaries)
        obj_stats["valid_rows"] = sum(fs["valid_rows"] for fs in file_summaries)
        obj_stats["error_rows"] = sum(fs["error_rows"] for fs in file_summaries)

        statuses = [fs["status"] for fs in file_summaries]
        if all(s == "success" for s in statuses):
            obj_stats["status"] = "success"
        elif any(s == "error" for s in statuses):
            obj_stats["status"] = "error"
        else:
            obj_stats["status"] = "partial"

        obj_stats["validation_error_count"] = sum(
            len(fs.get("validation_errors", [])) for fs in file_summaries
        )
        obj_stats["generation_error_count"] = sum(
            1 for fs in file_summaries if fs.get("generation_error")
        )

    return summary