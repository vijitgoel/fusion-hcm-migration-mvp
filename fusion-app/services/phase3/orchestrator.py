from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .catalog import get_object_catalog
from .catalog import ObjectDefinition
from .hdl_writer import write_dat
from .processor import map_columns, normalize, read_file, validate
from .scanner import discover_files


def run_batch(root_folder: str) -> Dict[str, Any]:
    root_path = Path(root_folder).resolve()

    if not root_path.exists():
        raise FileNotFoundError(f"Input folder not found: {root_path}")

    output_folder = root_path.parent / f"{root_path.name}_hdl_output"
    output_folder.mkdir(parents=True, exist_ok=True)

    catalog = get_object_catalog()
    files = discover_files(root_path, catalog)

    summary = {
        "input_folder": str(root_path),
        "output_folder": str(output_folder),
        "total_files": len(files),
        "processed_files": 0,
        "skipped_files": 0,
        "errors": [],
        "objects": {},
    }

    for discovered in files:
        if not discovered.object_name:
            summary["skipped_files"] += 1
            continue

        obj: ObjectDefinition = catalog[discovered.object_name]

        try:
            df = read_file(discovered.path)
            df = normalize(df)
            mapped_df = map_columns(df, obj)

            errors = validate(mapped_df, obj.required_columns)
            clean_df = mapped_df if not errors else pd.DataFrame(columns=mapped_df.columns)

            write_dat(
                clean_df,
                obj,
                output_folder,
                source_name=discovered.path.stem,
            )

            summary["processed_files"] += 1
            summary["objects"].setdefault(obj.name, {"files": 0, "errors": 0})
            summary["objects"][obj.name]["files"] += 1
            summary["objects"][obj.name]["errors"] += len(errors)

            if errors:
                for err in errors:
                    summary["errors"].append(
                        f"{discovered.relative_path}: {err['message']}"
                    )

        except Exception as exc:
            summary["errors"].append(f"{discovered.relative_path}: {str(exc)}")

    return summary