from __future__ import annotations

import re
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def normalize_token(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "", str(value)).lower()


def canonical_column_name(value: str) -> str:
    return normalize_token(value)


def is_empty(value: Any) -> bool:
    if pd.isna(value):
        return True
    return str(value).strip() == ""


def normalize_value(value: Any, is_date: bool = False) -> Any:
    if pd.isna(value):
        return ""

    if is_date:
        try:
            parsed = pd.to_datetime(value, errors="coerce")
            if pd.isna(parsed):
                return str(value).strip()
            return parsed.strftime("%Y-%m-%d")
        except Exception:
            return str(value).strip()

    if hasattr(value, "strftime"):
        try:
            return value.strftime("%Y-%m-%d")
        except Exception:
            pass

    if isinstance(value, float) and value.is_integer():
        return int(value)

    return str(value).strip() if isinstance(value, str) else value


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def sanitize_for_json(obj: Any) -> Any:
    """
    Reusable recursive JSON sanitizer for API responses and file writes.
    Converts all non-serializable values safely without changing business logic,
    validation details, or response structure.

    Rules (applied recursively to dicts, lists, dataclasses):
    - NaN / np.nan / pd.NA / float('nan') → None (→ null in JSON)
    - numpy scalars (int64, float64, etc.) → native Python int/float
    - pandas.Timestamp, datetime, date → ISO format string
    - pathlib.Path → str (absolute path)
    - dataclasses → dict via asdict() then recurse
    - Preserves all validation issues, row_values, summaries, strings, ints, bools, lists
    - No silent exceptions; falls back gracefully

    Used centrally before JSONResponse and json.dumps to prevent HTTP 500s.
    """
    # Handle None/empty early
    if obj is None:
        return None

    # Safe NaN check (avoids "truth value of array is ambiguous" error for pandas
    # Series/arrays/DataFrames while catching np.nan, pd.NA, float('nan'))
    if pd.api.types.is_scalar(obj) and pd.isna(obj):
        return None
    if isinstance(obj, float) and (str(obj).lower() == "nan" or (hasattr(np, "isnan") and np.isnan(obj))):
        return None

    # Numpy scalars (common in pandas DataFrames)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj) if not np.isnan(obj) else None
    if isinstance(obj, np.ndarray):
        return sanitize_for_json(obj.tolist())

    # Datetime / pandas Timestamp (from pd.to_datetime or date columns)
    if isinstance(obj, (datetime, date, pd.Timestamp)):
        try:
            return obj.isoformat()
        except Exception:
            return str(obj)

    # Path objects (everywhere in engine: source_file, run_dir, output paths)
    if isinstance(obj, Path):
        return str(obj)

    # Dataclasses (ValidationIssue, RunResult, FileSummary, etc. - used heavily in summary)
    if hasattr(obj, "__dataclass_fields__") or (hasattr(obj, "__dict__") and not isinstance(obj, type)):
        try:
            from dataclasses import asdict, is_dataclass
            if is_dataclass(obj) and not isinstance(obj, type):
                return sanitize_for_json(asdict(obj))
        except Exception:
            pass
        # Fallback for objects with __dict__
        if hasattr(obj, "__dict__"):
            return sanitize_for_json(obj.__dict__)

    # Dicts (core of the nested summary: objects, files, validation_issues, row_values)
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}

    # Lists/tuples/sets (issues lists, file_summaries, rejected payloads)
    if isinstance(obj, (list, tuple)):
        return [sanitize_for_json(item) for item in obj]
    if isinstance(obj, (set, frozenset)):
        return [sanitize_for_json(item) for item in obj]

    # All other native types (str, int, float, bool) are already JSON safe
    return obj