"""News API — seznam novinek z aggregátoru (s is_favorite flag)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.db_models import FavoriteNews, NewsItem
from app.models.schemas import NewsItemOut
from app.scrapers.rss import fetch_all_rss

router = APIRouter(prefix="/news", tags=["news"])


async def _attach_favorites(items: list[NewsItem], session: AsyncSession) -> list[dict]:
    """Vrátí list dictů s flagem is_favorite."""
    if not items:
        return []
    fav_ids = {
        r[0]
        for r in (
            await session.execute(
                select(FavoriteNews.news_item_id).where(
                    FavoriteNews.news_item_id.in_([i.id for i in items])
                )
            )
        ).all()
    }
    return [
        {
            "id": i.id,
            "url": i.url,
            "source": i.source,
            "title": i.title,
            "summary": i.summary,
            "published_at": i.published_at,
            "tags": i.tags,
            "is_favorite": i.id in fav_ids,
        }
        for i in items
    ]


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

    items = list((await session.execute(stmt)).scalars().all())
    enriched = await _attach_favorites(items, session)
    return [NewsItemOut.model_validate(e) for e in enriched]


@router.post("/refresh", response_model=dict)
async def refresh_news(session: AsyncSession = Depends(get_db)) -> dict:
    """Manuální trigger — stáhne všechny RSS feeds teď."""
    stats = await fetch_all_rss(session)
    return {"sources": stats}
