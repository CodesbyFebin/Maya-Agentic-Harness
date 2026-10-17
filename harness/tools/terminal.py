"""Terminal tool wrapper for MAYA agent harness.

Restricted commands only. Expand carefully.
"""

import subprocess
from typing import Tuple

ALLOWED_PREFIXES = ("ls", "pwd", "echo", "date", "whoami", "df", "free", "uptime")

def run(command: str, timeout: int = 15) -> Tuple[str, str, int]:
    parts = command.strip().split()
    if not parts or not parts[0] in ALLOWED_PREFIXES:
        return "", "Command not allowed", 1
    try:
        result = subprocess.run(
            parts,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Timeout", 1
    except Exception as e:
        return "", str(e), 1
