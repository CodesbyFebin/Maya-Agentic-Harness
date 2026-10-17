# Architecture

MAYA is split into two layers:

1. **Dashboard** (HTML/JS) — voice, multi-view UI, local persistence
2. **Harness** (Python) — agent loop, tools, workflows, memory, evidence traces

## Data flow

```
User (voice or text)
   ↓
Dashboard
   ↓
MAYA Agent Runtime
   ↓
Tools + Memory + Traces
```

MAYA keeps the full execution path inspectable so the operator can verify what happened.
