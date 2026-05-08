from __future__ import annotations

from pathlib import Path

import pandas as pd

from .catalog import ObjectDefinition
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


def map_columns(df, obj: ObjectDefinition):
    mapped = df.copy()
    renamed = {}

    # Rename columns using aliases
    for expected_col, aliases in obj.column_aliases.items():
        for alias in aliases:
            if alias in mapped.columns:
                renamed[alias] = expected_col
                break

    if renamed:
        mapped.rename(columns=renamed, inplace=True)

    # Keep only relevant columns
    keep_cols = obj.all_columns
    available_keep = [col for col in keep_cols if col in mapped.columns]
    mapped = mapped[available_keep] if available_keep else pd.DataFrame(columns=keep_cols)

    # Fill missing columns with empty
    for col in keep_cols:
        if col not in mapped.columns:
            mapped[col] = ''

    return mapped


def validate(df, required_columns):
    errors = []

    for col in required_columns:
        if col not in df.columns or df[col].isna().all():
            errors.append({
                "id": new_id("ERR"),
                "message": f"Missing or empty column {col}"
            })

    return errors