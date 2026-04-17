"""Favorites API — oblíbené novinky + workflow News → Article."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.db_models import FavoriteNews, NewsItem
from app.models.schemas import (
    FavoriteNewsIn,
    FavoriteNewsOut,
    NewsItemOut,
)

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("", response_model=list[FavoriteNewsOut])
async def list_favorites(
    session: AsyncSession = Depends(get_db),
) -> list[FavoriteNewsOut]:
    rows = (
        (
            await session.execute(
                select(FavoriteNews)
                .order_by(desc(FavoriteNews.created_at))
                .options(selectinload(FavoriteNews.news))
            )
        )
        .scalars()
        .all()
    )
    return [FavoriteNewsOut.model_validate(r) for r in rows]


@router.post("", response_model=FavoriteNewsOut, status_code=201)
async def add_favorite(
    payload: FavoriteNewsIn,
    session: AsyncSession = Depends(get_db),
) -> FavoriteNewsOut:
    # Ověř, že novinka existuje
    news = (
        await session.execute(
            select(NewsItem).where(NewsItem.id == payload.news_item_id)
        )
    ).scalar_one_or_none()
    if news is None:
        raise HTTPException(status_code=404, detail="Novinka nenalezena")

    # Duplicitní check
    existing = (
        await session.execute(
            select(FavoriteNews).where(FavoriteNews.news_item_id == payload.news_item_id)
        )
    ).scalar_one_or_none()
    if existing is not None:
        return FavoriteNewsOut.model_validate(existing)

    fav = FavoriteNews(news_item_id=payload.news_item_id, note=payload.note)
    session.add(fav)
    await session.flush()
    await session.refresh(fav, ["news"])
    return FavoriteNewsOut.model_validate(fav)


@router.delete("/news/{news_item_id}", status_code=204)
async def remove_favorite_by_news(
    news_item_id: str,
    session: AsyncSession = Depends(get_db),
) -> None:
    fav = (
        await session.execute(
            select(FavoriteNews).where(FavoriteNews.news_item_id == news_item_id)
        )
    ).scalar_one_or_none()
    if fav is None:
        raise HTTPException(status_code=404, detail="Není v oblíbených")
    await session.delete(fav)


@router.patch("/{favorite_id}", response_model=FavoriteNewsOut)
async def update_favorite_note(
    favorite_id: str,
    payload: dict,
    session: AsyncSession = Depends(get_db),
) -> FavoriteNewsOut:
    fav = (
        await session.execute(select(FavoriteNews).where(FavoriteNews.id == favorite_id))
    ).scalar_one_or_none()
    if fav is None:
        raise HTTPException(status_code=404, detail="Oblíbené nenalezeno")
    if "note" in payload:
        fav.note = payload["note"]
    await session.flush()
    await session.refresh(fav, ["news"])
    return FavoriteNewsOut.model_validate(fav)
