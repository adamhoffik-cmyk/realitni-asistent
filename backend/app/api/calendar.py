"""Calendar API — proxy na Google Calendar, s pydantic schematy."""
from __future__ import annotations

import logging
from datetime import datetime

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.integrations import google_calendar, google_oauth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/calendar", tags=["calendar"])


class CalendarEventOut(BaseModel):
    id: str
    summary: str
    start: datetime | None
    end: datetime | None
    description: str | None
    location: str | None
    html_link: str | None


class CalendarEventIn(BaseModel):
    summary: str
    start: datetime
    end: datetime
    description: str | None = None
    location: str | None = None
    attendees: list[str] | None = None


def _parse_dt(obj: dict | None) -> datetime | None:
    if not obj:
        return None
    value = obj.get("dateTime") or obj.get("date")
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def _to_out(ev: dict) -> CalendarEventOut:
    return CalendarEventOut(
        id=ev.get("id", ""),
        summary=ev.get("summary", "(bez názvu)"),
        start=_parse_dt(ev.get("start")),
        end=_parse_dt(ev.get("end")),
        description=ev.get("description"),
        location=ev.get("location"),
        html_link=ev.get("htmlLink"),
    )


@router.get("/events", response_model=list[CalendarEventOut])
async def list_events(
    days_ahead: int = Query(14, le=90),
    session: AsyncSession = Depends(get_db),
) -> list[CalendarEventOut]:
    if not await google_oauth.is_authorized(session):
        raise HTTPException(401, detail="Google neni prihlaseny. Jdi na /api/auth/google")

    from datetime import timedelta, timezone

    now = datetime.now(timezone.utc)
    time_max = now + timedelta(days=days_ahead)

    try:
        events = await google_calendar.list_events(
            session, time_min=now, time_max=time_max, max_results=30
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Calendar list error")
        raise HTTPException(502, detail=f"Google Calendar chyba: {exc}")

    return [_to_out(e) for e in events]


@router.post("/events", response_model=CalendarEventOut, status_code=201)
async def create_event(
    payload: CalendarEventIn,
    session: AsyncSession = Depends(get_db),
) -> CalendarEventOut:
    if not await google_oauth.is_authorized(session):
        raise HTTPException(401, detail="Google neni prihlaseny")
    try:
        ev = await google_calendar.create_event(
            session,
            summary=payload.summary,
            start=payload.start,
            end=payload.end,
            description=payload.description,
            location=payload.location,
            attendees=payload.attendees,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, detail=f"Vytvoreni eventu selhalo: {exc}")
    return _to_out(ev)


@router.delete("/events/{event_id}", status_code=204)
async def delete_event(
    event_id: str,
    session: AsyncSession = Depends(get_db),
) -> None:
    if not await google_oauth.is_authorized(session):
        raise HTTPException(401, detail="Google neni prihlaseny")
    try:
        await google_calendar.delete_event(session, event_id)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, detail=f"Smazani eventu selhalo: {exc}")
