"""Nábor API — tracker denních náborových aktivit."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db import get_db
from app.models.db_models import NaborActivity

router = APIRouter(prefix="/nabor", tags=["nabor"])


class ActivityIn(BaseModel):
    date: str  # YYYY-MM-DD
    activity_type: str  # dopis | cold_call | setkani | schuzka | sfera_vlivu | jiny
    count: int = 1
    notes: str | None = None
    outcome: str | None = None


class ActivityOut(BaseModel):
    id: str
    date: str
    activity_type: str
    count: int
    notes: str | None
    outcome: str | None
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/activities", response_model=ActivityOut, status_code=201)
async def log_activity(
    payload: ActivityIn, session: AsyncSession = Depends(get_db)
) -> ActivityOut:
    row = NaborActivity(
        date=payload.date,
        activity_type=payload.activity_type,
        count=payload.count,
        notes=payload.notes,
        outcome=payload.outcome,
    )
    session.add(row)
    await session.commit()
    return ActivityOut.model_validate(row)


@router.get("/activities", response_model=list[ActivityOut])
async def list_activities(
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    limit: int = Query(200, le=1000),
    session: AsyncSession = Depends(get_db),
) -> list[ActivityOut]:
    stmt = select(NaborActivity).order_by(desc(NaborActivity.date), desc(NaborActivity.created_at)).limit(limit)
    if from_date:
        stmt = stmt.where(NaborActivity.date >= from_date)
    if to_date:
        stmt = stmt.where(NaborActivity.date <= to_date)
    rows = list((await session.execute(stmt)).scalars().all())
    return [ActivityOut.model_validate(r) for r in rows]


@router.delete("/activities/{activity_id}", status_code=204)
async def delete_activity(
    activity_id: str, session: AsyncSession = Depends(get_db)
) -> None:
    row = (
        await session.execute(select(NaborActivity).where(NaborActivity.id == activity_id))
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(404)
    await session.delete(row)
    await session.commit()


@router.get("/stats")
async def stats(
    days: int = Query(30, le=365),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Shrnutí za posledních N dní podle typu aktivity."""
    cutoff = (date.today() - timedelta(days=days)).isoformat()
    stmt = (
        select(
            NaborActivity.activity_type,
            func.sum(NaborActivity.count).label("total"),
        )
        .where(NaborActivity.date >= cutoff)
        .group_by(NaborActivity.activity_type)
    )
    rows = (await session.execute(stmt)).all()
    by_type = {r.activity_type: int(r.total or 0) for r in rows}

    # Denní rozpočet (podle tvého plánu: 150 dopisů týdně = ~21/den)
    targets_weekly = {
        "dopis": 150,
        "cold_call": 140,  # 20-30 denně × 7
        "schuzka": 3,  # týdně
    }
    return {
        "days": days,
        "by_type": by_type,
        "targets_weekly": targets_weekly,
    }
