# MAYA Agentic Harness

**Local-first personal AI command center and agentic harness.**

MAYA is a JARVIS-style visual command center that sits on top of any OpenAI-compatible agent backbone. It is built for operators who want systems that prove what happened.

The project combines a dark cyan multi-view dashboard (voice, tasks, memory, workflows) with a Python harness that provides agent loops, tool wrappers, workflow playbooks, and evidence traces. Everything runs locally first.

## Ultimate v4.0 Status

- Fully functional dashboard with voice, chat history, and live backend status
- Wired to any OpenAI-compatible endpoint
- FreeLLMAPI recommended as the free multi-provider backend
- Agent loop writes evidence traces
- Tool wrappers and workflow playbooks ready

## Why an Agentic Harness?

Most AI agent frameworks focus on the model and the prompt. An **agentic harness** is the full operational layer around the model: the interface the human uses, the tools the agent can call, the memory it can recall, the workflows it can follow, and the evidence it leaves behind so the operator can verify what actually occurred.

MAYA treats the agent as a system that must be observable, controllable, and auditable. The dashboard is the operator console. The harness is the runtime that records tool calls, stores results, and makes the execution path inspectable.

## Core Features

- **Command Center UI** — multi-view dark interface with live feed and AI core visual
- **Voice** — Web Speech API for speech-to-text + TTS
- **OpenAI-compatible backend** — works with FreeLLMAPI, OpenJarvis, Ollama, or any `/v1/chat/completions` server
- **Local persistence** — chat history and settings in localStorage
- **Workflow playbooks** — YAML definitions for research, code, monitoring, email, files, news
- **Tool wrappers** — restricted filesystem and terminal tools
- **Memory** — schema + SQLite helper
- **Evidence traces** — every agent run writes a JSON trace

## Quick Start

### 1. Dashboard
Open `dashboard/maya-command-center.html` in Chrome or Edge.

### 2. Backend (pick one)

**FreeLLMAPI (recommended free multi-provider):**
```bash
curl -fsSL https://freellmapi.co/install.sh | bash
# then set dashboard backend to http://localhost:3001
```

**OpenJarvis:**
```bash
curl -fsSL https://open-jarvis.github.io/OpenJarvis/install.sh | bash
jarvis serve --port 8000
```

**Minimal stub:**
```bash
cd harness && pip install fastapi uvicorn && python backend_stub.py
```

In the dashboard, click Settings and confirm the Backend URL.

## Project Structure

```
README.md
site.json
dashboard/maya-command-center.html   # ultimate wired UI
harness/
  agent_loop.py                      # real backend calls + traces
  backend_stub.py
  workflows/
  tools/
  memory/
wiki/
docs/
```

## Architecture

```
[ MAYA Dashboard v4.0 ]
     ↔ Voice + localStorage
     ↔ /v1/chat/completions
[ FreeLLMAPI / OpenJarvis / Ollama / stub ]
     ↔ Tools · Workflows · Memory · Evidence Traces
```

## FreeLLMAPI Integration

FreeLLMAPI aggregates free tiers from dozens of providers behind one endpoint with automatic failover. It is the recommended free backend for MAYA. See `wiki/FreeLLMAPI.md`.

## License

Apache-2.0

Built by CodesbyFebin · systems that prove what happened.
