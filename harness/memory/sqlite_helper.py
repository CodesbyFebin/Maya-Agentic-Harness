"""Simple SQLite helper for MAYA memory.

Creates a local maya_memory.db and provides append / recent query.
"""

import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent / "maya_memory.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id TEXT PRIMARY KEY,
            type TEXT,
            content TEXT,
            source TEXT,
            timestamp TEXT,
            tags TEXT,
            evidence TEXT
        )
    """)
    return conn

def add_entry(entry_type: str, content: str, source: str = "agent", tags=None, evidence=None):
    conn = get_conn()
    eid = f"mem_{int(datetime.now(timezone.utc).timestamp())}"
    conn.execute(
        "INSERT INTO memory VALUES (?, ?, ?, ?, ?, ?, ?)",
        (eid, entry_type, content, source,
         datetime.now(timezone.utc).isoformat(),
         json.dumps(tags or []),
         json.dumps(evidence or {}))
    )
    conn.commit()
    conn.close()
    return eid

def recent(limit: int = 20):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM memory ORDER BY timestamp DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    print("Memory DB ready at", DB_PATH)
