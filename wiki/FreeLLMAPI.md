# FreeLLMAPI Backend

FreeLLMAPI aggregates free LLM providers behind one OpenAI-compatible endpoint. It is an excellent backend for MAYA.

## Quick start

```bash
curl -fsSL https://freellmapi.co/install.sh | bash
# or Docker
```

Open http://localhost:3001, add provider keys, then set MAYA dashboard Settings backend to:

```
http://localhost:3001
```

## Why it fits MAYA

- Single `/v1/chat/completions` endpoint
- Automatic failover across free tiers
- Works with the evidence-trace loop in `harness/agent_loop.py`
- No changes required to the dashboard

Repo: https://github.com/tashfeenahmed/freellmapi
