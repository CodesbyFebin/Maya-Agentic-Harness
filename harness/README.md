# MAYA Agent Harness

Runtime side of MAYA. Works with FreeLLMAPI, OpenJarvis, or any OpenAI-compatible endpoint.

## Current files

- `agent_loop.py` — calls real backend and writes evidence traces
- `backend_stub.py` — minimal FastAPI stub
- `workflows/` — playbook YAMLs
- `tools/` — filesystem and terminal wrappers
- `memory/` — schema + SQLite helper

## Recommended backend: FreeLLMAPI

```bash
curl -fsSL https://freellmapi.co/install.sh | bash
# dashboard backend → http://localhost:3001
```

Then test the loop:
```bash
python agent_loop.py "What is an agentic harness?"
```

Traces appear in `traces/`.
