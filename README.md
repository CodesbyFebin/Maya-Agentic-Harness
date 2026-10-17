# MAYA Agentic Harness

**Local-first personal AI command center and agentic harness.**

MAYA is a JARVIS-style visual command center that sits on top of an OpenJarvis-compatible or any OpenAI-compatible agent backbone. It is built for operators who want systems that prove what happened.

The project combines a dark cyan multi-view dashboard (voice, tasks, memory, workflows) with a Python harness that provides agent loops, tool wrappers, workflow playbooks, and evidence traces. Everything is designed to run locally first.

## Why an Agentic Harness?

Most AI agent frameworks focus on the model and the prompt. An **agentic harness** is the full operational layer around the model: the interface the human uses, the tools the agent can call, the memory it can recall, the workflows it can follow, and the evidence it leaves behind so the operator can verify what actually occurred.

MAYA treats the agent as a system that must be observable, controllable, and auditable. The dashboard is the operator console. The harness is the runtime that records tool calls, stores results, and makes the execution path inspectable.

## Core Features

- **Command Center UI** — multi-view dark interface (Command Center, Agents, Tasks, Memory, Tools, Workflows, Settings)
- **Voice** — Web Speech API for speech-to-text input and text-to-speech output
- **OpenAI-compatible backend** — talks to `http://localhost:8000/v1/chat/completions`
- **Local persistence** — tasks, notes, chat history, and settings in localStorage
- **Workflow playbooks** — YAML definitions for morning digest, research, code assistance, system monitoring, email triage, file organization, and news briefs
- **Tool wrappers** — restricted filesystem and terminal tools with allowlists
- **Memory** — schema plus SQLite helper for facts, notes, and traces
- **Evidence traces** — agent loop that writes JSON records of every step

## Quick Start

### 1. Dashboard

Open `dashboard/maya-command-center.html` in Chrome or Edge. Allow the microphone if you want voice.

### 2. Backend

**OpenJarvis (recommended):**
```bash
curl -fsSL https://open-jarvis.github.io/OpenJarvis/install.sh | bash
jarvis serve --port 8000
```

**Minimal stub:**
```bash
cd harness
pip install fastapi uvicorn
python backend_stub.py
```

In the dashboard go to Settings, set the Backend URL, and click Save & Test.

## Project Structure

```
README.md
site.json
package.json
app/
  layout.tsx
  globals.css
public/
  favicon.svg
docs/
  index.html          # GitHub Pages landing
wiki/
  Home.md
  Getting-Started.md
  Architecture.md
dashboard/
  maya-command-center.html
harness/
  README.md
  backend_stub.py
  agent_loop.py
  workflows/
  tools/
  memory/
```

## Architecture

The system has two main layers.

**Dashboard layer** (browser)
- Captures voice or typed input
- Renders the multi-panel interface
- Stores local state
- Sends requests to the `/v1/chat/completions` endpoint

**Harness layer** (Python)
- Receives requests
- Runs agent loops
- Calls tools under policy constraints
- Writes evidence traces
- Stores memory in SQLite or JSONL

```
[ MAYA Dashboard ]
     ↔ Web Speech + localStorage
     ↔ /v1/chat/completions
[ Harness / OpenJarvis / Ollama ]
     ↔ Tools · Workflows · Memory · Traces
```

OpenJarvis primitives map cleanly:
- Intelligence → model selection and routing
- Engine → Ollama, vLLM, or other local engines
- Agents → simple, orchestrator, ReAct, CodeAct
- Tools & Memory → the wrappers and SQLite store in this repo
- Learning → review of evidence traces for improvement

## Workflows

Playbooks live in `harness/workflows/`. Each YAML file declares an agent type, required tools, and ordered steps.

Examples:
- morning-digest — calendar, inbox, news
- deep-research — multi-source research with citations
- code-assistant — plan, implement, verify
- system-monitor — local health checks
- email-triage — classify and draft
- file-organizer — scan and move files
- news-brief — topic-based news synthesis

## Tools

Tool wrappers in `harness/tools/` enforce safety boundaries:
- `filesystem.py` restricts operations to allowed roots
- `terminal.py` only permits a short allowlist of commands

Additional tools (web search, email, calendar) can be added following the same pattern.

## Memory and Evidence

Memory entries follow the schema in `harness/memory/schema.md`. The SQLite helper creates a single-file database. The agent loop in `agent_loop.py` writes a JSON trace for every run so the operator can inspect exactly which tools were called and what they returned.

This is the practical expression of the project tagline: systems that prove what happened.

## Branding and Metadata

- `site.json` holds title, description, theme colors, Open Graph, and Twitter card data
- `public/favicon.svg` is the geometric mark
- `app/layout.tsx` and `app/globals.css` provide a Next.js starting point with the dark theme
- `docs/index.html` is ready for GitHub Pages

## GitHub Pages

Enable GitHub Pages from the `docs/` folder (or `/docs` source) in the repository Settings → Pages. The landing page includes Open Graph and Twitter meta tags.

## Wiki

Detailed guides are in the `wiki/` directory:
- Home
- Getting Started
- Architecture

These can be copied into the GitHub Wiki or served as documentation.

## Roadmap

- Full interactive dashboard HTML committed to the repo
- Real LLM wiring inside `agent_loop.py`
- Additional tool wrappers (web, email, calendar)
- Evidence hashing and proof layer
- Memory sync between dashboard and SQLite
- Tauri desktop packaging
- More workflow playbooks

## License

Apache-2.0

Built by CodesbyFebin · systems that prove what happened.

---

*This README is intentionally detailed so the project ranks for searches related to agentic harness, local AI command center, OpenJarvis dashboard, evidence traces, and self-hosted agent runtimes.*
