"""Read-only filesystem tools with resolved-root containment checks.

Configure one or more allowed roots with MAYA_ALLOWED_ROOTS, separated by the
platform path separator. If unset, the harness directory is the only root.
"""

from __future__ import annotations

import os
from pathlib import Path

MAX_READ_CHARS = 10_000
MAX_DIRECTORY_ENTRIES = 500


def allowed_roots() -> tuple[Path, ...]:
    configured = os.environ.get("MAYA_ALLOWED_ROOTS", "")
    values = configured.split(os.pathsep) if configured else [str(Path(__file__).resolve().parents[1])]
    roots = tuple(Path(value).expanduser().resolve() for value in values if value.strip())
    if not roots:
        raise RuntimeError("MAYA_ALLOWED_ROOTS must contain at least one directory")
    return roots


def safe_path(path: str, *, roots: tuple[Path, ...] | None = None) -> Path:
    """Resolve a candidate and reject paths outside the configured roots."""
    candidate = Path(path).expanduser().resolve()
    trusted_roots = roots if roots is not None else allowed_roots()
    resolved_roots = tuple(root.expanduser().resolve() for root in trusted_roots)
    if not any(candidate == root or candidate.is_relative_to(root) for root in resolved_roots):
        raise PermissionError("Access denied: path is outside the configured roots")
    return candidate


def list_dir(path: str, *, max_entries: int = MAX_DIRECTORY_ENTRIES) -> list[str]:
    directory = safe_path(path)
    if not directory.is_dir():
        raise NotADirectoryError("Path is not a directory")
    names = sorted(item.name for item in directory.iterdir() if not item.name.startswith("."))
    if len(names) > max_entries:
        return names[:max_entries] + [f"… truncated; showing {max_entries} of {len(names)} entries"]
    return names


def read_file(path: str, *, max_chars: int = MAX_READ_CHARS) -> str:
    if max_chars < 0 or max_chars > MAX_READ_CHARS:
        raise ValueError(f"max_chars must be between 0 and {MAX_READ_CHARS}")
    file_path = safe_path(path)
    if not file_path.is_file():
        raise FileNotFoundError("Path is not a regular file")
    with file_path.open("r", encoding="utf-8", errors="replace") as handle:
        return handle.read(max_chars)
