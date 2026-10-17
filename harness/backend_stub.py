"""Minimal OpenAI-compatible stub for MAYA dashboard testing.

Run: python backend_stub.py
Then set dashboard Settings → Backend URL = http://localhost:8000
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI(title="MAYA Backend Stub")

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str = "stub"
    messages: List[Message]

@app.post("/v1/chat/completions")
async def chat(req: ChatRequest):
    last = req.messages[-1].content if req.messages else ""
    reply = f"[MAYA stub] Received: {last[:200]}. Connect real OpenJarvis (`jarvis serve`) for full agents."
    return {
        "choices": [{
            "message": {"role": "assistant", "content": reply},
            "finish_reason": "stop"
        }]
    }

@app.get("/health")
async def health():
    return {"status": "ok", "service": "maya-stub"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
