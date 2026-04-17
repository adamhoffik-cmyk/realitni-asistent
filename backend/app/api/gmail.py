"""Gmail API — list/read/send + draft."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.integrations import gmail, google_oauth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/gmail", tags=["gmail"])


class GmailMessage(BaseModel):
    id: str
    thread_id: str | None = None
    snippet: str
    sender: str  # "from" je Python keyword → používáme sender
    to: str
    subject: str
    date: str
    body: str
    label_ids: list[str] = []
    is_unread: bool = False


class SendIn(BaseModel):
    to: EmailStr
    subject: str
    body: str
    cc: list[EmailStr] | None = None
    bcc: list[EmailStr] | None = None
    html: bool = False
    thread_id: str | None = None


class DraftIn(BaseModel):
    to: EmailStr
    subject: str
    body: str
    cc: list[EmailStr] | None = None


@router.get("/profile")
async def profile(session: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    if not await google_oauth.is_authorized(session):
        raise HTTPException(401, detail="Google nepřihlášený")
    try:
        return await gmail.get_profile(session)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, detail=f"Gmail chyba: {exc}")


@router.get("/messages")
async def list_messages(
    query: str = Query("in:inbox", description="Gmail search query"),
    max_results: int = Query(20, le=100),
    full: bool = Query(False, description="Načíst plný body (pomalejší)"),
    session: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    if not await google_oauth.is_authorized(session):
        raise HTTPException(401, detail="Google nepřihlášený")

    try:
        refs = await gmail.list_messages(
            session, query=query, max_results=max_results
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, detail=f"Gmail chyba: {exc}")

    if not full:
        # rychlá verze — vrací jen IDs
        return refs

    # plný fetch — paralelně pro první N zpráv
    import asyncio

    tasks = [gmail.get_message(session, m["id"]) for m in refs]
    try:
        results = await asyncio.gather(*tasks)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, detail=f"Gmail fetch chyba: {exc}")
    # Pydantic alias "sender" → schema returns plain dict se 'from'
    return [{**r, "sender": r.pop("from", "")} for r in results]


@router.get("/messages/{msg_id}")
async def get_message(
    msg_id: str, session: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    if not await google_oauth.is_authorized(session):
        raise HTTPException(401, detail="Google nepřihlášený")
    try:
        msg = await gmail.get_message(session, msg_id)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, detail=f"Gmail chyba: {exc}")
    # přejmenujeme "from" → "sender" (klíčové slovo v Pythonu/JS)
    return {**msg, "sender": msg.pop("from", "")}


@router.post("/send")
async def send(
    payload: SendIn, session: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    if not await google_oauth.is_authorized(session):
        raise HTTPException(401, detail="Google nepřihlášený")
    try:
        result = await gmail.send_message(
            session,
            to=payload.to,
            subject=payload.subject,
            body=payload.body,
            cc=[str(c) for c in payload.cc] if payload.cc else None,
            bcc=[str(b) for b in payload.bcc] if payload.bcc else None,
            thread_id=payload.thread_id,
            html=payload.html,
        )
        return {"ok": True, "id": result.get("id"), "thread_id": result.get("threadId")}
    except Exception as exc:  # noqa: BLE001
        logger.exception("Gmail send")
        raise HTTPException(502, detail=f"Odeslání selhalo: {exc}")


@router.post("/drafts")
async def draft(
    payload: DraftIn, session: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    if not await google_oauth.is_authorized(session):
        raise HTTPException(401, detail="Google nepřihlášený")
    try:
        result = await gmail.create_draft(
            session,
            to=payload.to,
            subject=payload.subject,
            body=payload.body,
            cc=[str(c) for c in payload.cc] if payload.cc else None,
        )
        return {"ok": True, "id": result.get("id")}
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, detail=f"Vytvoření draftu selhalo: {exc}")


@router.post("/messages/{msg_id}/mark-read")
async def mark_read(
    msg_id: str, session: AsyncSession = Depends(get_db)
) -> dict:
    if not await google_oauth.is_authorized(session):
        raise HTTPException(401, detail="Google nepřihlášený")
    await gmail.mark_read(session, msg_id)
    return {"ok": True}
