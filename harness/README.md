# MAYA Agent Harness Scaffolding

This directory holds the agentic runtime side of MAYA.

## Alignment with OpenJarvis

OpenJarvis provides the five primitives:
1. Intelligence — model catalog & routing
2. Engine — Ollama / vLLM / etc.
3. Agents — simple, orchestrator, ReAct, CodeAct, etc.
4. Tools & Memory — MCP tools, local memory
5. Learning — trace-driven improvement

MAYA dashboard talks to the OpenAI-compatible `/v1/chat/completions` endpoint exposed by `jarvis serve`.

## Current files

```
harness/
  README.md
  backend_stub.py          # FastAPI OpenAI-compatible stub
  agent_loop.py            # minimal loop that writes evidence traces
  workflows/
    morning-digest.yaml
    deep-research.yaml
    code-assistant.yaml
    system-monitor.yaml
    email-triage.yaml
    file-organizer.yaml
    news-brief.yaml
  tools/
    filesystem.py          # path-restricted file ops
    terminal.py            # allowlisted commands
  memory/
    schema.md
    sqlite_helper.py       # local SQLite memory
```

## Quick local backend

**OpenJarvis (recommended):**
```bash
jarvis serve --port 8000 --engine ollama --model qwen3.5:4b --agent orchestrator
```

**Stub:**
```bash
python backend_stub.py
```

Then point the dashboard Settings at `http://localhost:8000`.

## Next steps

- Wire agent_loop.py to a real LLM endpoint + the tool wrappers
- Add more tools (web, email, calendar)
- Evidence hash + proof layer
- Sync memory between dashboard and SQLite
