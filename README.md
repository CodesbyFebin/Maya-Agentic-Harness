# MAYA Agentic Harness

**Local-first personal AI command center + agent runtime.**

Visual JARVIS-style dashboard that sits on top of an OpenJarvis-compatible (or any OpenAI-compatible) agent backbone. Built for operators who want systems that prove what happened.

## What this is

- **Command Center UI** — multi-view dark cyan dashboard (Command Center, Agents, Tasks, Memory, Tools, Workflows, Settings)
- **Voice** — Web Speech API for speech-to-text + TTS
- **Backend ready** — talks to `http://localhost:8000/v1/chat/completions` (OpenJarvis `jarvis serve` or any compatible server)
- **Local persistence** — tasks, memory notes, chat history, settings in localStorage
- **Agentic direction** — structured for tools, workflows, memory indexing, and verifiable execution traces

## Quick start

### Dashboard
1. Open `dashboard/maya-command-center.html` in Chrome/Edge.
2. Allow microphone if using voice.

### Backend (choose one)
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

Then in the dashboard Settings → set Backend URL → Save & Test.

## Structure

```
README.md
dashboard/
  maya-command-center.html
harness/
  README.md
  backend_stub.py
  workflows/
    morning-digest.yaml
```

## Architecture

```
[ MAYA Dashboard (HTML/JS) ]
        ↔ Web Speech + localStorage
        ↔ /v1/chat/completions
[ OpenJarvis / Ollama / stub ]
        ↔ Agents · Tools · Memory · Traces
```

OpenJarvis primitives (Intelligence, Engine, Agents, Tools & Memory, Learning) map cleanly onto the dashboard panels.

## Next

- Full dashboard HTML (large file — push in follow-up or clone locally and copy)
- Real tool calls and agent loops with evidence traces
- Memory indexing
- More workflow playbooks
- Desktop packaging (Tauri)

## Visibility

Repo is currently private. Change to public in GitHub Settings if desired.

## License

Apache-2.0 (or match your preference).

Built by CodesbyFebin · systems that prove what happened.
