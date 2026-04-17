"""Google Calendar API wrapper — list/create/update/delete events."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from googleapiclient.discovery import build
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.google_oauth import get_credentials

logger = logging.getLogger(__name__)


async def _build_service(session: AsyncSession):
    creds = await get_credentials(session)
    if creds is None:
        raise RuntimeError("Google nepřihlášený — projdi OAuth flow na /api/auth/google")
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


async def list_events(
    session: AsyncSession,
    *,
    time_min: datetime | None = None,
    time_max: datetime | None = None,
    max_results: int = 20,
) -> list[dict[str, Any]]:
    service = await _build_service(session)
    now = datetime.now(timezone.utc)
    tmin = (time_min or now).isoformat()
    tmax = (time_max or (now + timedelta(days=14))).isoformat()

    events_result = service.events().list(
        calendarId="primary",
        timeMin=tmin,
        timeMax=tmax,
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    return events_result.get("items", [])


async def create_event(
    session: AsyncSession,
    *,
    summary: str,
    start: datetime,
    end: datetime,
    description: str | None = None,
    location: str | None = None,
    attendees: list[str] | None = None,
) -> dict[str, Any]:
    service = await _build_service(session)
    body: dict[str, Any] = {
        "summary": summary,
        "start": {"dateTime": start.isoformat(), "timeZone": "Europe/Prague"},
        "end": {"dateTime": end.isoformat(), "timeZone": "Europe/Prague"},
    }
    if description:
        body["description"] = description
    if location:
        body["location"] = location
    if attendees:
        body["attendees"] = [{"email": a} for a in attendees]

    return service.events().insert(calendarId="primary", body=body).execute()


async def update_event(
    session: AsyncSession,
    event_id: str,
    updates: dict[str, Any],
) -> dict[str, Any]:
    service = await _build_service(session)
    return service.events().patch(
        calendarId="primary",
        eventId=event_id,
        body=updates,
    ).execute()


async def delete_event(session: AsyncSession, event_id: str) -> None:
    service = await _build_service(session)
    service.events().delete(calendarId="primary", eventId=event_id).execute()
