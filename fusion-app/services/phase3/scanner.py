from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from .catalog import ObjectDefinition
from .utils import canonical_column_name

SUPPORTED_EXTENSIONS = {".csv", ".xlsx"}
SKIP_DIR_NAMES = {".git", ".venv", "node_modules", "__pycache__", ".next", "dist", "build", "output", "phase3_output"}


@dataclass
class DiscoveredFile:
    path: Path
    relative_path: str
    object_name: Optional[str]
    object_match_source: str


def discover_files(root: Path, catalog: Dict[str, ObjectDefinition]) -> List[DiscoveredFile]:
    discovered: List[DiscoveredFile] = []
    root = root.resolve()

    for file_path in sorted(root.rglob("*")):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        if any(part in SKIP_DIR_NAMES for part in file_path.parts):
            continue

        object_name, match_source = resolve_object(file_path, catalog)
        discovered.append(
            DiscoveredFile(
                path=file_path,
                relative_path=str(file_path.relative_to(root)),
                object_name=object_name,
                object_match_source=match_source,
            )
        )
    return discovered


def resolve_object(file_path: Path, catalog: Dict[str, ObjectDefinition]) -> Tuple[Optional[str], str]:
    tokens = [canonical_column_name(part) for part in file_path.parts] + [canonical_column_name(file_path.stem)]

    exact_matches: List[Tuple[int, str]] = []
    fuzzy_matches: List[Tuple[int, str]] = []

    for object_name, definition in catalog.items():
        aliases = definition.normalized_aliases
        for idx, token in enumerate(tokens):
            if token in aliases:
                # exact match is strongest when found in folder path
                score = 100 if idx < len(tokens) - 1 else 95
                exact_matches.append((score, object_name))
            else:
                for alias in aliases:
                    if alias and (alias in token or token in alias):
                        score = 80 if idx < len(tokens) - 1 else 70
                        fuzzy_matches.append((score, object_name))
                        break

    if exact_matches:
        return sorted(exact_matches, key=lambda x: (-x[0], x[1]))[0][1], "exact"
    if fuzzy_matches:
        return sorted(fuzzy_matches, key=lambda x: (-x[0], x[1]))[0][1], "fuzzy"
    return None, "unmatched"
