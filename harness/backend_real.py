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

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
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
EVENT_QUEUE_SIZE = 100
EVENT_PROTOCOL = "maya.events.v1"
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


def run_agent(
    messages: list[dict[str, Any]],
    model: str,
    temperature: float,
    emit: Callable[[dict[str, Any]], None] | None = None,
    run_id: str | None = None,
) -> tuple[str, list[dict[str, Any]]]:
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
            denied = False
            error_type = None
            try:
                result = TOOL_FUNCTIONS[name](**args)
                result_str = json.dumps(result) if not isinstance(result, str) else result
                result_str = result_str[:MAX_TOOL_RESULT_CHARS]
                status = "ok"
            except Exception as exc:
                result_str = f"Error: {exc}"
                status = "error"
                denied = isinstance(exc, PermissionError)
                error_type = type(exc).__name__
            event = {"round": round_num, "tool": name, "status": status, "args": args}
            events.append(event)
            if emit:
                # Do not broadcast tool arguments or file contents to dashboard clients.
                if denied:
                    emit({"type": "policy_denied", "task_id": run_id, "tool": name, "status": "denied", "decision": "deny", "policy_reason_code": "permission_denied"})
                emit({"type": "tool_event", "task_id": run_id, "tool": name, "status": status, "round": round_num, "error_type": error_type})
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


class EventHub:
    """Bounded in-process fan-out for live runtime events."""

    def __init__(self) -> None:
        self.clients: set[asyncio.Queue[dict[str, Any]]] = set()
        self.sequence = 0

    def subscribe(self) -> asyncio.Queue[dict[str, Any]]:
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=EVENT_QUEUE_SIZE)
        self.clients.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[dict[str, Any]]) -> None:
        self.clients.discard(queue)

    async def publish(self, event: dict[str, Any]) -> None:
        self.sequence += 1
        message = {**event, "seq": self.sequence, "timestamp": datetime.now(timezone.utc).isoformat()}
        for queue in tuple(self.clients):
            if queue.full():
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                pass


event_hub = EventHub()
active_runs: dict[str, dict[str, Any]] = {}


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


def health_snapshot() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "maya-agent-backend",
        "mode": "tool-loop",
        "model": LLM_MODEL,
        "endpoint_kind": "openai-compatible",
        "trace_schema": "execution_log_unverified",
        "websocket_protocol": EVENT_PROTOCOL,
        "tools": sorted(TOOL_FUNCTIONS),
    }


def origin_is_allowed(websocket: WebSocket) -> bool:
    origin = websocket.headers.get("origin")
    return not origin or origin in allowed_origins


@app.get("/health")
async def health() -> dict[str, Any]:
    return health_snapshot()


@app.websocket("/ws")
async def live_events(websocket: WebSocket) -> None:
    if not origin_is_allowed(websocket):
        await websocket.close(code=1008, reason="Origin not allowed")
        return

    await websocket.accept()
    queue = event_hub.subscribe()
    await websocket.send_json({
        "type": "runtime_snapshot",
        "service": "maya-agent-backend",
        "mode": "tool-loop",
        "status": "ok",
        "active_runs": list(active_runs.values()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    try:
        while True:
            event_task = asyncio.create_task(queue.get())
            receive_task = asyncio.create_task(websocket.receive_json())
            done, pending = await asyncio.wait(
                {event_task, receive_task}, return_when=asyncio.FIRST_COMPLETED
            )
            for task in pending:
                task.cancel()
            await asyncio.gather(*pending, return_exceptions=True)
            if event_task in done:
                await websocket.send_json(event_task.result())
            if receive_task in done:
                message = receive_task.result()
                if isinstance(message, dict) and message.get("type") == "ping":
                    await websocket.send_json({"type": "pong", "timestamp": datetime.now(timezone.utc).isoformat()})
    except (WebSocketDisconnect, RuntimeError, OSError):
        pass
    finally:
        event_hub.unsubscribe(queue)


def versioned_frame(event: dict[str, Any]) -> dict[str, Any] | None:
    event_type = event.get("type")
    frame_type: str | None = None
    data: dict[str, Any] = {}
    if event_type == "agent_event" and event.get("action") == "working":
        frame_type = "run_started"
        data = {"event_type": "run_started", "kind": "agent_run", "status": "running"}
    elif event_type == "tool_event":
        frame_type = "tool_event"
        data = {
            "event_type": "tool_call",
            "kind": "tool_event",
            "tool": event.get("tool"),
            "status": event.get("status"),
            "round": event.get("round"),
        }
    elif event_type == "policy_denied":
        frame_type = "policy_denied"
        data = {
            "event_type": "policy_denied",
            "kind": "policy_decision",
            "status": "denied",
            "decision": "deny",
            "tool": event.get("tool"),
            "policy_reason_code": event.get("policy_reason_code"),
        }
    elif event_type == "task_update":
        frame_type = "run_result"
        data = {
            "event_type": "run_result",
            "kind": "run_result",
            "status": "success" if event.get("status") == "done" else "failed",
            "tool_events": event.get("tool_events", 0),
            "trace_written": bool(event.get("trace_written", False)),
        }
    if frame_type is None:
        return None
    return {
        "protocol": EVENT_PROTOCOL,
        "type": frame_type,
        "run_id": event.get("task_id"),
        "seq": event.get("seq"),
        "timestamp": event.get("timestamp"),
        "data": data,
    }


@app.websocket("/v1/events")
async def versioned_live_events(websocket: WebSocket) -> None:
    if not origin_is_allowed(websocket):
        await websocket.close(code=1008, reason="Origin not allowed")
        return

    await websocket.accept()
    queue = event_hub.subscribe()
    await websocket.send_json({
        "protocol": EVENT_PROTOCOL,
        "type": "hello",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": {**health_snapshot(), "active_runs": list(active_runs.values())},
    })
    try:
        for run in tuple(active_runs.values()):
            await websocket.send_json({
                "protocol": EVENT_PROTOCOL,
                "type": "run_started",
                "run_id": run["task_id"],
                "timestamp": run["started_at"],
                "data": {"event_type": "run_started", "kind": "agent_run", "status": "running"},
            })
        while True:
            event_task = asyncio.create_task(queue.get())
            receive_task = asyncio.create_task(websocket.receive())
            done, pending = await asyncio.wait(
                {event_task, receive_task}, timeout=20, return_when=asyncio.FIRST_COMPLETED
            )
            for task in pending:
                task.cancel()
            await asyncio.gather(*pending, return_exceptions=True)
            if not done:
                await websocket.send_json({
                    "protocol": EVENT_PROTOCOL,
                    "type": "heartbeat",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "data": {},
                })
                continue
            if receive_task in done:
                message = receive_task.result()
                if message.get("type") == "websocket.disconnect":
                    break
                if message.get("text"):
                    try:
                        incoming = json.loads(message["text"])
                    except json.JSONDecodeError:
                        incoming = None
                    if isinstance(incoming, dict) and incoming.get("type") == "ping":
                        await websocket.send_json({
                            "protocol": EVENT_PROTOCOL,
                            "type": "heartbeat",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "data": {"echo": True},
                        })
            if event_task in done:
                frame = versioned_frame(event_task.result())
                if frame:
                    await websocket.send_json(frame)
    except (WebSocketDisconnect, RuntimeError, OSError):
        pass
    finally:
        event_hub.unsubscribe(queue)


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest) -> dict[str, Any]:
    messages = [message.model_dump() for message in request.messages]
    query = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
    run_id = f"run_{uuid.uuid4().hex}"
    loop = asyncio.get_running_loop()

    def emit_from_worker(event: dict[str, Any]) -> None:
        # Wait for the bounded fan-out before the worker continues so event order
        # is preserved ahead of the completion event.
        asyncio.run_coroutine_threadsafe(event_hub.publish(event), loop).result()

    active_runs[run_id] = {"task_id": run_id, "status": "running", "started_at": datetime.now(timezone.utc).isoformat()}
    await event_hub.publish({"type": "agent_event", "action": "working", "agent": "MAYA agent loop", "task_id": run_id, "task_description": "Agent request"})
    try:
        result, events = await asyncio.to_thread(
            run_agent,
            messages,
            model=request.model or LLM_MODEL,
            temperature=request.temperature,
            emit=emit_from_worker,
            run_id=run_id,
        )
    except Exception as exc:
        active_runs.pop(run_id, None)
        await event_hub.publish({"type": "task_update", "task_id": run_id, "title": "Agent request", "status": "failed", "agent": "MAYA agent loop", "trace_written": False})
        await event_hub.publish({"type": "agent_event", "action": "error", "agent": "MAYA agent loop", "task_id": run_id, "error": "Configured model request failed"})
        detail = str(exc) if isinstance(exc, RuntimeError) else "Agent request failed unexpectedly"
        raise HTTPException(status_code=502, detail=detail) from exc
    log_path = write_execution_log(query, events, result)
    active_runs.pop(run_id, None)
    await event_hub.publish({"type": "task_update", "task_id": run_id, "title": "Agent request", "status": "done", "agent": "MAYA agent loop", "tool_events": len(events), "trace_written": bool(log_path)})
    await event_hub.publish({"type": "agent_event", "action": "complete", "agent": "MAYA agent loop", "task_id": run_id})
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
        "maya": {"run_id": run_id, "status": "success", "execution_log": "unverified", "trace_written": bool(log_path), "log_path": log_path, "tool_events": events},
    }


