# MAYA Memory Schema

Local-first memory designed for evidence and provenance.

## Entry types

- `note` — freeform user or agent note
- `fact` — short, dated, source-linked assertion
- `task` — actionable item with status
- `trace` — tool call or agent step with inputs/outputs
- `workflow_run` — completed playbook execution

## Minimal record

```json
{
  "id": "uuid",
  "type": "fact",
  "content": "...",
  "source": "user | agent | tool:web_search",
  "timestamp": "2026-10-17T23:50:00Z",
  "tags": ["project:maya", "priority:high"],
  "evidence": {
    "tool_calls": [],
    "confidence": 0.9
  }
}
```

## Storage options

1. **localStorage** (dashboard) — immediate, per-browser
2. **SQLite** (recommended next) — single-file, queryable, portable
3. **OpenJarvis memory** — if using the full framework

## Next

- Python helper to append/query a local SQLite store
- Sync path from dashboard → harness memory
- Simple retrieval for agent context
