# MAYA Agentic Harness

**Local-first personal AI command center and agentic harness.**

MAYA is a complete visual command center and agent runtime. It is built for operators who want systems that prove what happened.

The project combines a dark cyan multi-view dashboard (voice, tasks, memory, workflows) with a Python harness that provides agent loops, tool wrappers, workflow playbooks, and evidence traces. Everything runs locally first.

## Ultimate Status

- Fully functional dashboard with voice, chat history, and live status
- Local agent runtime with evidence traces
- Tool wrappers and workflow playbooks
- Memory store and persistence

## Why an Agentic Harness?

Most AI systems focus on the model and the prompt. An **agentic harness** is the full operational layer: the interface the human uses, the tools the agent can call, the memory it can recall, the workflows it can follow, and the evidence it leaves behind so the operator can verify what actually occurred.

MAYA treats the agent as a system that must be observable, controllable, and auditable. The dashboard is the operator console. The harness is the runtime that records every step.

## Core Features

- **Command Center UI** — multi-view dark interface with live feed and AI core visual
- **Voice** — speech-to-text input and text-to-speech output
- **Local agent runtime** — agent loop that calls models and records traces
- **Local persistence** — chat history and settings
- **Workflow playbooks** — definitions for research, code, monitoring, email, files, news
- **Tool wrappers** — restricted filesystem and terminal tools
- **Memory** — structured store for facts, notes, and traces
- **Evidence traces** — every agent run writes a complete JSON record

## Quick Start

### 1. Dashboard
Open `dashboard/maya-command-center.html` in Chrome or Edge.

### 2. Local runtime
```bash
cd harness
pip install fastapi uvicorn
python backend_stub.py
```

In the dashboard, open Settings and set the backend URL if needed.

## Project Structure

```
README.md
site.json
dashboard/maya-command-center.html
harness/
  agent_loop.py
  backend_stub.py
  workflows/
  tools/
  memory/
wiki/
docs/
```

## Architecture

```
[ MAYA Dashboard ]
     ↔ Voice + localStorage
     ↔ Agent runtime
[ MAYA Harness ]
     ↔ Tools · Workflows · Memory · Evidence Traces
```

## License

Apache-2.0

Built by CodesbyFebin · systems that prove what happened.
