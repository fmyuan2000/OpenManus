from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.agent.manus import Manus
from app.schema import Message


STATIC_DIR = Path(__file__).parent / "static"


def _last_assistant_text(messages: list[Message]) -> str:
    # Prefer the most recent assistant message with non-empty content.
    for msg in reversed(messages):
        if msg.role == "assistant" and (msg.content or "").strip():
            return msg.content  # type: ignore[return-value]
    return ""


@dataclass
class ChatSession:
    agent: Manus
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


class NewSessionResponse(BaseModel):
    session_id: str


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    raw: Optional[str] = None


def create_app() -> FastAPI:
    app = FastAPI(title="OpenManus Web", version="0.1.0")

    sessions: Dict[str, ChatSession] = {}

    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def index() -> HTMLResponse:
        index_path = STATIC_DIR / "index.html"
        if not index_path.exists():
            raise HTTPException(status_code=500, detail="Missing static/index.html")
        return HTMLResponse(index_path.read_text(encoding="utf-8"))

    @app.post("/api/new", response_model=NewSessionResponse)
    async def new_session() -> NewSessionResponse:
        session_id = uuid.uuid4().hex
        sessions[session_id] = ChatSession(agent=await Manus.create())
        return NewSessionResponse(session_id=session_id)

    @app.post("/api/reset", response_model=NewSessionResponse)
    async def reset_session(req: NewSessionResponse) -> NewSessionResponse:
        sess = sessions.pop(req.session_id, None)
        if sess is not None:
            await sess.agent.cleanup()
        session_id = uuid.uuid4().hex
        sessions[session_id] = ChatSession(agent=await Manus.create())
        return NewSessionResponse(session_id=session_id)

    @app.post("/api/chat", response_model=ChatResponse)
    async def chat(req: ChatRequest) -> ChatResponse:
        sess = sessions.get(req.session_id)
        if sess is None:
            raise HTTPException(status_code=404, detail="Unknown session_id")

        async with sess.lock:
            # Manus/BaseAgent.run returns a step summary; for UI we expose both:
            # - reply: last assistant message text (best for chat bubble)
            # - raw: the run() summary (helpful for debugging)
            raw = await sess.agent.run(req.message)
            reply = _last_assistant_text(sess.agent.messages)
            if not reply.strip():
                reply = raw
            return ChatResponse(session_id=req.session_id, reply=reply, raw=raw)

    @app.on_event("shutdown")
    async def _shutdown() -> None:
        # Best-effort cleanup for all sessions.
        for sess in list(sessions.values()):
            try:
                await sess.agent.cleanup()
            except Exception:
                pass
        sessions.clear()

    return app


app = create_app()

