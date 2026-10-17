# Architecture

MAYA is split into two layers:

1. **Dashboard** (HTML/JS) — voice, multi-view UI, localStorage persistence
2. **Harness** (Python) — agent loop, tools, workflows, memory, evidence traces

## Data flow

```
User (voice or text)
   ↓
Dashboard
   ↓  /v1/chat/completions
Harness / OpenJarvis / Ollama
   ↓
Tools + Memory + Traces
```

## OpenJarvis alignment

MAYA maps to OpenJarvis primitives:
- Intelligence → model routing
- Engine → Ollama / vLLM
- Agents → orchestrator, ReAct, CodeAct
- Tools & Memory → local wrappers + SQLite
- Learning → trace review

See [OpenJarvis Integration](OpenJarvis-Integration).
