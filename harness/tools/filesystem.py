"""Filesystem tool wrapper for MAYA agent harness.

Minimal safe wrappers. Expand with path allowlists as needed.
"""

from pathlib import Path
from typing import List

ALLOWED_ROOTS = [Path.home() / "Documents", Path.cwd()]

def list_dir(path: str) -> List[str]:
    p = Path(path).expanduser().resolve()
    if not any(str(p).startswith(str(root)) for root in ALLOWED_ROOTS):
        return ["Access denied"]
    if not p.exists():
        return ["Not found"]
    return [item.name for item in p.iterdir()]

def read_file(path: str, max_chars: int = 4000) -> str:
    p = Path(path).expanduser().resolve()
    if not any(str(p).startswith(str(root)) for root in ALLOWED_ROOTS):
        return "Access denied"
    if not p.is_file():
        return "Not a file"
    return p.read_text(errors="ignore")[:max_chars]

def write_file(path: str, content: str) -> str:
    p = Path(path).expanduser().resolve()
    if not any(str(p).startswith(str(root)) for root in ALLOWED_ROOTS):
        return "Access denied"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return f"Wrote {len(content)} chars to {p}"
