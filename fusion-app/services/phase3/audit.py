from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from .utils import ensure_dir, new_id, now_iso


class Phase3AuditLogger:
    def __init__(self, audit_log_path: Path, run_id: str):
        self.audit_log_path = audit_log_path
        self.run_id = run_id
        ensure_dir(self.audit_log_path.parent)

    def log(
        self,
        event: str,
        message: str,
        level: str = "INFO",
        object_name: Optional[str] = None,
        source_file: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        record = {
            "audit_id": new_id("AUD"),
            "run_id": self.run_id,
            "timestamp": now_iso(),
            "level": level,
            "event": event,
            "message": message,
            "object_name": object_name,
            "source_file": source_file,
            "extra": extra or {},
        }
        with self.audit_log_path.open("a", encoding="utf-8") as fp:
            fp.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record
