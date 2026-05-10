from __future__ import annotations

from pathlib import Path

import pandas as pd

from .catalog import ObjectDefinition


def write_dat(df, obj: ObjectDefinition, output_path, source_name=None):
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    if source_name:
        file_name = obj.output_filename_template.format(source=source_name, name=obj.name)
    else:
        file_name = obj.output_filename_template.format(name=obj.name)

    file_path = output_dir / file_name

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(obj.output_header + "\n")
        for _, row in df.iterrows():
            row_dict = {col: str(row.get(col, '')) if pd.notna(row.get(col)) else '' for col in obj.all_columns}
            line = obj.output_template.format(**row_dict)
            f.write(line + "\n")

    return str(file_path)