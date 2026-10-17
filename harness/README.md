# MAYA Agent Harness

Runtime side of MAYA. Local agent loop, tools, workflows, memory, and evidence traces.

## Current files

- `agent_loop.py` — agent runtime that writes evidence traces
- `backend_stub.py` — minimal local server
- `workflows/` — playbook definitions
- `tools/` — filesystem and terminal wrappers
- `memory/` — schema and store

## Run

```bash
python backend_stub.py
python agent_loop.py "What is an agentic harness?"
```

Traces appear in `traces/`.
