from __future__ import annotations

import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

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
