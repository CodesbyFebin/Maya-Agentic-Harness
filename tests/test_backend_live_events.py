from __future__ import annotations

import json
from typing import Any

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from harness import backend_real


def test_v1_stream_matches_runtime_and_tool_outcomes(monkeypatch: Any, tmp_path: Any) -> None:
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
    monkeypatch.setattr(backend_real, "TRACE_DIR", tmp_path / "traces")

    with TestClient(backend_real.app) as client:
        health = client.get("/health").json()
        assert health["websocket_protocol"] == "maya.events.v1"
        assert set(health["tools"]) == {"list_dir", "read_file"}

        with client.websocket_connect("/v1/events") as websocket:
            hello = websocket.receive_json()
            assert hello["protocol"] == "maya.events.v1"
            assert hello["type"] == "hello"
            assert hello["data"]["model"] == backend_real.LLM_MODEL

            response = client.post(
                "/v1/chat/completions",
                json={"messages": [{"role": "user", "content": "List this directory"}]},
            )
            assert response.status_code == 200
            payload = response.json()["maya"]
            assert payload["trace_written"] is True
            run_id = payload["run_id"]

            frames = [websocket.receive_json() for _ in range(3)]

    assert [frame["type"] for frame in frames] == ["run_started", "tool_event", "run_result"]
    assert all(frame["protocol"] == "maya.events.v1" for frame in frames)
    assert all(frame["run_id"] == run_id for frame in frames)
    assert frames[1]["data"]["tool"] == "list_dir"
    assert frames[1]["data"]["status"] == "ok"
    assert frames[2]["data"]["status"] == "success"
    assert frames[2]["data"]["trace_written"] is True
    assert all("args" not in frame["data"] and "result" not in frame["data"] for frame in frames)


def test_versioned_websocket_rejects_unlisted_browser_origins() -> None:
    with TestClient(backend_real.app) as client:
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect(
                "/v1/events", headers={"origin": "https://untrusted.example"}
            ):
                pass

