"""News API — seznam novinek z aggregátoru."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.db_models import NewsItem
from app.models.schemas import NewsItemOut
from app.scrapers.rss import fetch_all_rss

router = APIRouter(prefix="/news", tags=["news"])


@router.get("", response_model=list[NewsItemOut])
async def list_news(
    source: str | None = Query(None),
    tier: str | None = Query(None, description="tier1 | tier2 | tier3"),
    limit: int = Query(30, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db),
) -> list[NewsItemOut]:
    stmt = (
        select(NewsItem)
        .order_by(desc(NewsItem.published_at), desc(NewsItem.fetched_at))
        .limit(limit)
        .offset(offset)
    )
    if source:
        stmt = stmt.where(NewsItem.source == source)
    if tier:
        stmt = stmt.where(NewsItem.tags.like(f'%"{tier}"%'))

    items = (await session.execute(stmt)).scalars().all()
    return [NewsItemOut.model_validate(i) for i in items]


@router.post("/refresh", response_model=dict)
async def refresh_news(session: AsyncSession = Depends(get_db)) -> dict:
    """Manuální trigger — stáhne všechny RSS feeds teď."""
    stats = await fetch_all_rss(session)
    return {"sources": stats}
