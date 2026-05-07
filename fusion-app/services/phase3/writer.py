from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List

from .utils import ensure_dir


def write_text(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def write_dat(path: Path, header: str, rows: List[str]) -> None:
    ensure_dir(path.parent)
    lines = [header] + rows if rows else [header]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_rejected_csv(path: Path, rejected_rows: List[Dict[str, Any]]) -> None:
    ensure_dir(path.parent)
    fieldnames = [
        "validation_id",
        "row_id",
        "run_id",
        "object_name",
        "source_file",
        "relative_source_file",
        "source_row_number",
        "error_code",
        "field_name",
        "message",
        "row_values",
    ]
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        for row in rejected_rows:
            writer.writerow({
                **{key: row.get(key, "") for key in fieldnames},
                "row_values": json.dumps(row.get("row_values", {}), ensure_ascii=False),
            })


def bundle_run_directory(run_dir: Path, bundle_path: Path) -> Path:
    ensure_dir(bundle_path.parent)
    base_name = str(bundle_path.with_suffix(""))
    archive_path = shutil.make_archive(base_name, "zip", root_dir=run_dir)
    return Path(archive_path)
