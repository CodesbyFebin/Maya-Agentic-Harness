# MAYA Agentic Harness

**Local-first personal AI command center + agent runtime.**

Visual JARVIS-style dashboard that sits on top of an OpenJarvis-compatible (or any OpenAI-compatible) agent backbone. Built for operators who want systems that prove what happened.

## What this is

- **Command Center UI** — multi-view dark cyan dashboard (Command Center, Agents, Tasks, Memory, Tools, Workflows, Settings)
- **Voice** — Web Speech API for speech-to-text + TTS
- **Backend ready** — talks to `http://localhost:8000/v1/chat/completions` (OpenJarvis `jarvis serve` or any compatible server)
- **Local persistence** — tasks, memory notes, chat history, settings in localStorage
- **Agentic direction** — structured for tools, workflows, memory indexing, and verifiable execution traces

## Quick start (dashboard)

1. Open `dashboard/maya-command-center.html` in Chrome/Edge.
2. Allow microphone if using voice.
3. (Optional) Run a local agent backend:

```bash
# OpenJarvis (recommended)
curl -fsSL https://open-jarvis.github.io/OpenJarvis/install.sh | bash
jarvis serve --port 8000
```

Then in the dashboard Settings → set Backend URL → Save & Test.

## Architecture sketch

```
[ MAYA Dashboard (HTML/JS) ]
        ↔ Web Speech + localStorage
        ↔ /v1/chat/completions
[ OpenJarvis / Ollama / any OpenAI-compatible engine ]
        ↔ Agents · Tools · Memory · Traces
```

## Next

- Wire real tool calls and agent loops
- Memory indexing (OpenJarvis memory or local vector store)
- Workflow playbooks
- Desktop packaging (Tauri)
- Evidence / proof layer for tool executions

## License

Apache-2.0 (or match your preference).

Built by CodesbyFebin · systems that prove what happened.
