from __future__ import annotations

from pathlib import Path

import pandas as pd

from .utils import new_id


def read_file(file_path):
    path = Path(file_path)

    if path.suffix.lower() == ".xlsx":
        return pd.read_excel(path)
    elif path.suffix.lower() == ".csv":
        return pd.read_csv(path)

    raise ValueError(f"Unsupported file type: {path.suffix}")


def normalize(df):
    df.columns = df.columns.str.strip()
    df.columns = [c.replace(" ", "") for c in df.columns]
    return df


def validate(df, required_columns):
    errors = []

    for col in required_columns:
        if col not in df.columns:
            errors.append({
                "id": new_id("ERR"),
                "message": f"Missing column {col}"
            })

    return errors