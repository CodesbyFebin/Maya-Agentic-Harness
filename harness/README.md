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

## Planned structure

```
harness/
  agents/          # agent definitions / prompts
  tools/           # custom tool wrappers
  workflows/       # playbook YAML or JSON
  memory/          # memory schema notes
  backend_stub/    # minimal FastAPI or Python example
```

## Quick local backend (OpenJarvis)

```bash
jarvis serve --port 8000 --engine ollama --model qwen3.5:4b --agent orchestrator
```

Then point the dashboard Settings at `http://localhost:8000`.

## Next steps

- Implement a thin Python agent loop that logs tool calls as evidence
- Add workflow YAML for morning-digest, deep-research, code-assistant
- Connect memory store
