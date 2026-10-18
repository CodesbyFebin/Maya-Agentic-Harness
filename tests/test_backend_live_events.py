from __future__ import annotations

import json
from typing import Any

from fastapi.testclient import TestClient

from harness import backend_real


def test_websocket_streams_real_agent_and_tool_events(monkeypatch: Any) -> None:
    responses = iter([
        {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "tool_calls": [{
                        "id": "call-1",
                        "type": "function",
                        "function": {"name": "list_dir", "arguments": json.dumps({"path": "."})},
                    }],
                }
            }]
        },
        {"choices": [{"message": {"role": "assistant", "content": "Found the files."}}]},
    ])
    monkeypatch.setattr(backend_real, "call_llm", lambda *args, **kwargs: next(responses))
    monkeypatch.setitem(backend_real.TOOL_FUNCTIONS, "list_dir", lambda path: ["README.md"])

    with TestClient(backend_real.app) as client:
        with client.websocket_connect("/ws") as websocket:
            snapshot = websocket.receive_json()
            assert snapshot["type"] == "runtime_snapshot"
            assert snapshot["status"] == "ok"

            response = client.post(
                "/v1/chat/completions",
                json={"messages": [{"role": "user", "content": "List this directory"}]},
            )
            assert response.status_code == 200
            run_id = response.json()["maya"]["run_id"]

            events = [websocket.receive_json() for _ in range(4)]

    assert [event["type"] for event in events] == [
        "agent_event",
        "tool_event",
        "task_update",
        "agent_event",
    ]
    assert events[0]["action"] == "working"
    assert events[1]["tool"] == "list_dir"
    assert events[1]["status"] == "ok"
    assert events[2]["status"] == "done"
    assert events[3]["action"] == "complete"
    assert all(event["task_id"] == run_id for event in events)
    assert all("args" not in event and "result" not in event for event in events)


def test_websocket_rejects_unlisted_browser_origins() -> None:
    with TestClient(backend_real.app) as client:
        with client.websocket_connect(
            "/ws", headers={"origin": "https://untrusted.example"}
        ) as websocket:
            message = websocket.receive_json()
            assert message["type"] != "runtime_snapshot"
