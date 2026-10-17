"""Minimal local OpenAI-compatible agent API with a bounded read-only tool loop.

Run from this directory with:
    uvicorn backend_real:app --host 127.0.0.1 --port 8001

The configured LLM must support OpenAI-style tool calls. This example exposes
only list_dir and read_file; it never runs model-generated shell commands.
"""

from __future__ import annotations

import asyncio
import json
import os
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from .tools.filesystem import list_dir, read_file
except ImportError:
    from tools.filesystem import list_dir, read_file

LLM_URL = os.environ.get("MAYA_LLM_URL", "http://127.0.0.1:3001/v1/chat/completions")
LLM_MODEL = os.environ.get("MAYA_LLM_MODEL", "auto")
MAX_TOOL_ROUNDS = int(os.environ.get("MAYA_MAX_TOOL_ROUNDS", "5"))
MAX_QUERY_CHARS = 20_000
MAX_TOOL_RESULT_CHARS = 10_000
TRACE_DIR = Path(os.environ.get("MAYA_TRACE_DIR", str(Path(__file__).parent / "traces")))

TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List non-hidden entries in a directory under an allowed root.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Directory path"}},
                "required": ["path"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read up to 10000 characters from a file under an allowed root.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "File path"}},
                "required": ["path"],
                "additionalProperties": False,
            },
        },
    },
]

TOOL_FUNCTIONS: dict[str, Callable[..., Any]] = {"list_dir": list_dir, "read_file": read_file}


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(max_length=MAX_QUERY_CHARS)


class ChatRequest(BaseModel):
    model: str | None = None
    messages: list[ChatMessage]
    temperature: float = 0.2


def call_llm(messages: list[dict[str, Any]], model: str, temperature: float) -> dict[str, Any]:
    payload = json.dumps({"model": model, "messages": messages, "tools": TOOLS, "temperature": temperature}).encode()
    req = urllib.request.Request(LLM_URL, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except Exception as exc:
        raise RuntimeError(f"LLM call failed: {exc}") from exc


def run_agent(messages: list[dict[str, Any]], model: str, temperature: float) -> tuple[str, list[dict[str, Any]]]:
    events: list[dict[str, Any]] = []
    for round_num in range(MAX_TOOL_ROUNDS):
        response = call_llm(messages, model, temperature)
        choice = response["choices"][0]
        message = choice["message"]
        if "tool_calls" not in message or not message["tool_calls"]:
            return message.get("content", ""), events
        messages.append(message)
        for call in message["tool_calls"]:
            name = call["function"]["name"]
            args = json.loads(call["function"]["arguments"] or "{}")
            call_id = call["id"]
            try:
                result = TOOL_FUNCTIONS[name](**args)
                result_str = json.dumps(result) if not isinstance(result, str) else result
                result_str = result_str[:MAX_TOOL_RESULT_CHARS]
                status = "ok"
            except Exception as exc:
                result_str = f"Error: {exc}"
                status = "error"
            events.append({"round": round_num, "tool": name, "status": status, "args": args})
            messages.append({"role": "tool", "tool_call_id": call_id, "name": name, "content": result_str})
    return "Stopped: no final answer was produced.", events


def write_execution_log(query: str, events: list[dict[str, Any]], result: str) -> str | None:
    record = {
        "id": f"run_{uuid.uuid4().hex}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "kind": "execution_log_unverified",
        "query": query[:MAX_QUERY_CHARS],
        "events": events,
        "result": result[:MAX_TOOL_RESULT_CHARS],
    }
    try:
        TRACE_DIR.mkdir(parents=True, exist_ok=True)
        path = TRACE_DIR / f"{record['id']}.json"
        path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
        return str(path)
    except OSError:
        return None


app = FastAPI(title="MAYA Agent Backend", version="0.1.0")
allowed_origins = [
    origin.strip() for origin in os.environ.get(
        "MAYA_ALLOWED_ORIGINS", "http://127.0.0.1:5500,http://localhost:5500"
    ).split(",") if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "maya-agent-backend", "mode": "tool-loop"}


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest) -> dict[str, Any]:
    messages = [message.model_dump() for message in request.messages]
    query = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
    try:
        result, events = await asyncio.to_thread(
            run_agent,
            messages,
            model=request.model or LLM_MODEL,
            temperature=request.temperature,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    log_path = write_execution_log(query, events, result)
    return {
        "id": f"chatcmpl_{uuid.uuid4().hex}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.model or LLM_MODEL,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": result},
            "finish_reason": "stop",
        }],
        "maya": {"execution_log": "unverified", "log_path": log_path, "tool_events": events},
    }
