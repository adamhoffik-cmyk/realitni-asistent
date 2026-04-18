"""Chat API — WebSocket streaming + REST historie.

Fáze 2 verze — plné napojení na Claude Agent SDK:
- historie session v SQLite
- system prompt s RAG kontextem (ChromaDB) přes context_builder
- streamování tokenů do WebSocketu
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.claude_client import ClaudeMessage, get_claude_client
from app.core.context_builder import build_system_prompt, resolve_allowed_tools
from app.db import AsyncSessionLocal, get_db
from app.models.db_models import ConversationSession, ConversationTurn
from app.models.schemas import ChatMessageOut

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

# Kolik posledních turnů zahrnout do SDK historie (sliding window)
MAX_HISTORY_TURNS = 20


@router.get("/sessions/current")
async def get_current_session(
    context: str = "home",
    max_age_hours: int = 24,
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Vrátí ID aktivní konverzační session pro daný kontext.

    Cross-device sync: desktop i mobil dostanou stejnou session → vidí
    stejnou historii. Pokud žádná není (nebo je starší než max_age_hours),
    vrátí {"id": null} a frontend začne novou session automaticky při
    prvním odeslání zprávy.
    """
    from datetime import timedelta

    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    row = (
        await session.execute(
            select(ConversationSession)
            .where(ConversationSession.context == context)
            .where(ConversationSession.last_activity_at >= cutoff)
            .order_by(ConversationSession.last_activity_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()

    return {
        "id": row.id if row else None,
        "context": context,
        "last_activity_at": row.last_activity_at.isoformat() if row else None,
    }


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
      Client → {
          "message": str,
          "session_id": str | null,
          "context": "home" | "<skill_id>"
      }
      Server → {
          "type": "session|token|tool_call|tool_result|done|error",
          "data": ...
      }
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

            # ---- 1. Session management + uložení user turn
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

                await websocket.send_json(
                    {"type": "session", "data": {"id": session_id}}
                )

                # ---- 2. Load history (sliding window)
                history_turns = (
                    (
                        await db.execute(
                            select(ConversationTurn)
                            .where(ConversationTurn.session_id == session_id)
                            .order_by(ConversationTurn.created_at.desc())
                            .limit(MAX_HISTORY_TURNS)
                        )
                    )
                    .scalars()
                    .all()
                )
                history_turns = list(reversed(history_turns))

                messages = [
                    ClaudeMessage(role=t.role, content=t.content) for t in history_turns
                ]

                # ---- 3. Sestav system prompt (kontext + RAG)
                try:
                    system_prompt = await build_system_prompt(
                        db, user_message=user_message, context=context
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.exception("context_builder selhal")
                    system_prompt = (
                        "Jsi AI asistent realitního makléře. Odpovídej česky."
                    )

            allowed_tools = resolve_allowed_tools(context)

            # ---- 4. Stream from Claude
            buffer: list[str] = []
            async for event in claude.stream(
                messages,
                system_prompt=system_prompt,
                allowed_tools=allowed_tools,
            ):
                if event.type == "token":
                    buffer.append(event.data)
                    await websocket.send_json(
                        {"type": "token", "data": event.data}
                    )
                elif event.type == "tool_call":
                    await websocket.send_json(
                        {"type": "tool_call", "data": event.data}
                    )
                elif event.type == "tool_result":
                    await websocket.send_json(
                        {"type": "tool_result", "data": event.data}
                    )
                elif event.type == "done":
                    full_text = "".join(buffer)
                    async with AsyncSessionLocal() as db:
                        assistant_turn = ConversationTurn(
                            session_id=session_id,
                            role="assistant",
                            content=full_text,
                            tokens=(event.data or {}).get("tokens")
                            if isinstance(event.data, dict)
                            else None,
                        )
                        db.add(assistant_turn)
                        await db.commit()
                    await websocket.send_json({"type": "done", "data": event.data})
                elif event.type == "error":
                    await websocket.send_json({"type": "error", "data": event.data})

    except WebSocketDisconnect:
        logger.info("Chat WS disconnected")
    except Exception as exc:  # noqa: BLE001
        logger.exception("Chat WS error")
        try:
            await websocket.send_json({"type": "error", "data": str(exc)})
        except Exception:  # noqa: BLE001
            pass
