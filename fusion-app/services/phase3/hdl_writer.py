from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_dat(df, object_name, output_path, source_name=None):
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    if source_name:
        file_name = f"{source_name}_{object_name}.dat"
    else:
        file_name = f"{object_name}.dat"

    file_path = output_dir / file_name

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"METADATA|{object_name}\n")
        for _, row in df.iterrows():
            f.write("|".join("" if pd.isna(x) else str(x) for x in row) + "\n")

    return str(file_path)