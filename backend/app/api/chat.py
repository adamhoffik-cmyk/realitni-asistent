"""Chat API — WebSocket streaming + REST historie.

Fáze 1D stub: WebSocket funguje, ale claude_client je STUB (echo). Skutečné
volání claude-agent-sdk přijde po zprovoznění základního deploy (Fáze 2).
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.claude_client import ClaudeMessage, get_claude_client
from app.db import AsyncSessionLocal, get_db
from app.models.db_models import ConversationSession, ConversationTurn
from app.models.schemas import ChatMessageOut

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/sessions/{session_id}/turns", response_model=list[ChatMessageOut])
async def get_session_turns(
    session_id: str, session: AsyncSession = Depends(get_db)
) -> list[ChatMessageOut]:
    turns = (
        (
            await session.execute(
                select(ConversationTurn)
                .where(ConversationTurn.session_id == session_id)
                .order_by(ConversationTurn.created_at)
            )
        )
        .scalars()
        .all()
    )
    return [ChatMessageOut.model_validate(t) for t in turns]


@router.websocket("/ws")
async def chat_ws(websocket: WebSocket) -> None:
    """WebSocket endpoint pro streamovaný chat.

    Protokol:
      Client → { "message": str, "session_id": str | null, "context": "home" | str }
      Server → { "type": "token|tool_call|tool_result|done|error|session", "data": ... }
    """
    await websocket.accept()
    claude = get_claude_client()

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "data": "Invalid JSON"})
                continue

            user_message = payload.get("message", "").strip()
            session_id = payload.get("session_id")
            context = payload.get("context") or "home"

            if not user_message:
                await websocket.send_json({"type": "error", "data": "Prázdná zpráva"})
                continue

            # ---- 1. Získej nebo vytvoř session + ulož user turn
            async with AsyncSessionLocal() as db:
                if session_id:
                    sess = (
                        await db.execute(
                            select(ConversationSession).where(
                                ConversationSession.id == session_id
                            )
                        )
                    ).scalar_one_or_none()
                    if sess is None:
                        sess = ConversationSession(id=session_id, context=context)
                        db.add(sess)
                else:
                    sess = ConversationSession(context=context)
                    db.add(sess)
                    await db.flush()
                    session_id = sess.id

                sess.last_activity_at = datetime.now(timezone.utc)

                user_turn = ConversationTurn(
                    session_id=session_id,
                    role="user",
                    content=user_message,
                )
                db.add(user_turn)
                await db.commit()

                await websocket.send_json({"type": "session", "data": {"id": session_id}})

            # ---- 2. Sestav historii pro Clauda (stub — jen poslední user)
            messages = [ClaudeMessage(role="user", content=user_message)]

            # ---- 3. Stream odpovědi
            buffer: list[str] = []
            async for event in claude.stream(messages):
                if event.type == "token":
                    buffer.append(event.data)
                    await websocket.send_json({"type": "token", "data": event.data})
                elif event.type == "done":
                    full_text = "".join(buffer)
                    async with AsyncSessionLocal() as db:
                        assistant_turn = ConversationTurn(
                            session_id=session_id,
                            role="assistant",
                            content=full_text,
                            tokens=event.data.get("tokens") if isinstance(event.data, dict) else None,
                        )
                        db.add(assistant_turn)
                        await db.commit()
                    await websocket.send_json({"type": "done", "data": event.data})
                elif event.type == "error":
                    await websocket.send_json({"type": "error", "data": event.data})
                else:
                    await websocket.send_json({"type": event.type, "data": event.data})

    except WebSocketDisconnect:
        logger.info("Chat WS disconnected")
    except Exception as exc:  # noqa: BLE001
        logger.exception("Chat WS error")
        try:
            await websocket.send_json({"type": "error", "data": str(exc)})
        except Exception:  # noqa: BLE001
            pass
