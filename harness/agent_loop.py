"""MAYA agent loop — talks to any OpenAI-compatible endpoint and logs evidence.

Default targets FreeLLMAPI (http://localhost:3001) or OpenJarvis (8000).
"""

import json
import time
import uuid
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

TRACE_DIR = Path(__file__).parent / "traces"
TRACE_DIR.mkdir(exist_ok=True)

DEFAULT_BACKEND = "http://localhost:3001/v1/chat/completions"

def log_trace(query: str, steps: list, result: str) -> dict:
    trace = {
        "id": f"trace_{uuid.uuid4().hex[:12]}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "steps": steps,
        "result": result,
    }
    path = TRACE_DIR / f"{trace['id']}.json"
    path.write_text(json.dumps(trace, indent=2))
    return trace

def call_backend(messages, backend=DEFAULT_BACKEND, model="auto"):
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": 0.4
    }).encode()
    req = urllib.request.Request(
        backend,
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode())
    return data["choices"][0]["message"]["content"]

def agent(query: str, backend=DEFAULT_BACKEND) -> str:
    steps = []
    messages = [{"role": "user", "content": query}]
    try:
        reply = call_backend(messages, backend)
        steps.append({"tool": "llm", "status": "ok", "ts": time.time()})
        result = reply
    except Exception as e:
        steps.append({"tool": "llm", "status": "error", "error": str(e)})
        result = f"Error contacting backend: {e}"
    log_trace(query, steps, result)
    return result

if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "Hello MAYA. What is an agentic harness?"
    print(agent(q))
