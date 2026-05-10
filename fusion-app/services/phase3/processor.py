from __future__ import annotations

from pathlib import Path
from datetime import datetime
import re

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

    # Rename columns using aliases (to UPPER_SNAKE_CASE expected)
    for expected_col, aliases in obj.column_aliases.items():
        for alias in aliases:
            if alias in mapped.columns:
                renamed[alias] = expected_col
                break

    if renamed:
        mapped.rename(columns=renamed, inplace=True)

    # Handle SOURCE_SYSTEM_OWNER: add if missing, replace NaN/empty strings with default (constant for all rows)
    default_sso = obj.default_source_system_owner
    if 'SOURCE_SYSTEM_OWNER' not in mapped.columns:
        mapped['SOURCE_SYSTEM_OWNER'] = default_sso
    else:
        # Replace NaN and empty strings with default
        mapped['SOURCE_SYSTEM_OWNER'] = mapped['SOURCE_SYSTEM_OWNER'].apply(lambda x: default_sso if pd.isna(x) or str(x).strip() == '' else x)

    # Handle SOURCE_SYSTEM_ID: add/generate unique per row if missing, NaN, or empty string
    default_ssid_template = obj.default_source_system_id
    if 'SOURCE_SYSTEM_ID' not in mapped.columns or mapped['SOURCE_SYSTEM_ID'].apply(lambda x: pd.isna(x) or str(x).strip() == '').all():
        def generate_ssid(idx):
            return default_ssid_template.format(row_index=idx + 1)
        mapped['SOURCE_SYSTEM_ID'] = [generate_ssid(i) for i in range(len(mapped))]
    else:
        # Fill individual empty/NaN rows with generated unique
        def fill_ssid(idx):
            val = mapped['SOURCE_SYSTEM_ID'].iloc[idx]
            if pd.isna(val) or str(val).strip() == '':
                return default_ssid_template.format(row_index=idx + 1)
            return val
        mapped['SOURCE_SYSTEM_ID'] = [fill_ssid(i) for i in range(len(mapped))]

    # Keep only relevant columns from obj.all_columns
    keep_cols = obj.all_columns
    if keep_cols:
        available_keep = [col for col in keep_cols if col in mapped.columns]
        if available_keep:
            mapped = mapped[available_keep].copy()
        else:
            # If no matching columns, create empty DF with all columns
            mapped = pd.DataFrame(columns=keep_cols, index=mapped.index if len(mapped) > 0 else range(1))

    # Fill any remaining missing columns with empty string (should not happen for required, but safe)
    for col in keep_cols:
        if col not in mapped.columns:
            mapped[col] = ''

    # Standardize date columns to YYYY/MM/DD format
    date_formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"]
    for date_col in obj.date_columns:
        if date_col in mapped.columns:
            def parse_and_format_date(value):
                if pd.isna(value) or str(value).strip() == '':
                    return ''
                val_str = str(value).strip()
                for fmt in date_formats:
                    try:
                        parsed_date = datetime.strptime(val_str, fmt)
                        return parsed_date.strftime("%Y/%m/%d")
                    except ValueError:
                        continue
                # If no format matches, return empty (validation will catch)
                return ''
            mapped[date_col] = mapped[date_col].apply(parse_and_format_date)

    return mapped


def validate(df, obj: ObjectDefinition):
    errors = []

    # Check for missing columns (structural)
    for col in obj.required_columns:
        if col not in df.columns:
            errors.append({
                "row": None,
                "column": col,
                "message": f"Missing required column: {col}"
            })
            continue

    # Row-by-row validation using rules
    for idx, row in df.iterrows():
        for col, rules in obj.validation_rules.items():
            if col not in df.columns:
                continue

            value = row[col]
            if pd.isna(value):
                value = ''

            val_str = str(value).strip()

            # Required check
            if rules.get("required", False) and not val_str:
                errors.append({
                    "row": idx + 1,
                    "column": col,
                    "message": rules.get("error_msg", f"Required field {col} is empty")
                })
                continue

            # Skip if empty and not required
            if not val_str and not rules.get("required", False):
                continue

            # Length checks
            if "min_length" in rules and len(val_str) < rules["min_length"]:
                errors.append({
                    "row": idx + 1,
                    "column": col,
                    "message": rules.get("error_msg", f"{col} too short (min {rules['min_length']})")
                })
                continue

            if "max_length" in rules and len(val_str) > rules["max_length"]:
                errors.append({
                    "row": idx + 1,
                    "column": col,
                    "message": rules.get("error_msg", f"{col} too long (max {rules['max_length']})")
                })
                continue

            # Regex check
            if "regex" in rules:
                pattern = re.compile(rules["regex"])
                if not pattern.match(val_str):
                    errors.append({
                        "row": idx + 1,
                        "column": col,
                        "message": rules.get("error_msg", f"{col} format invalid")
                    })
                    continue

            # Data type check (e.g., date)
            if "data_type" in rules and rules["data_type"] == "date":
                date_formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"]
                parsed = False
                for fmt in date_formats:
                    try:
                        datetime.strptime(val_str, fmt)
                        parsed = True
                        break
                    except ValueError:
                        continue
                if not parsed:
                    value_msg = f" (provided value: '{val_str}')" if val_str else ""
                    errors.append({
                        "row": idx + 1,
                        "column": col,
                        "message": rules.get("error_msg", f"{col} must be valid date in YYYY-MM-DD, DD/MM/YYYY, or similar format") + value_msg
                    })

    return errors
