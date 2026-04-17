"""RSS scraper — fetch + parse + uložení do news_items tabulky."""
from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone

import feedparser
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import NewsItem
from app.scrapers.sources import NewsSource

logger = logging.getLogger(__name__)


def _url_hash(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]


def _contains_any(text: str, keywords: list[str]) -> bool:
    lower = text.lower()
    return any(k.lower() in lower for k in keywords)


def _parse_published(entry) -> datetime | None:
    """Extrahuje published datum z feedparser entry."""
    import time as t_mod

    for key in ("published_parsed", "updated_parsed"):
        tup = entry.get(key)
        if tup:
            try:
                return datetime.fromtimestamp(t_mod.mktime(tup), tz=timezone.utc)
            except Exception:  # noqa: BLE001
                continue
    return None


async def fetch_rss(source: NewsSource, session: AsyncSession) -> dict[str, int]:
    """Stáhne RSS feed, parsne, uloží nové items do DB.

    Vrátí statistiku {fetched, saved, skipped, errors}.
    """
    stats = {"fetched": 0, "saved": 0, "skipped": 0, "errors": 0}

    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(
                source.url,
                headers={"User-Agent": "Realitni-Asistent/1.0 (+https://reality-pittner.cz)"},
            )
            resp.raise_for_status()
            body = resp.text
    except Exception as exc:  # noqa: BLE001
        logger.warning("RSS fetch failed %s: %s", source.name, exc)
        stats["errors"] += 1
        return stats

    feed = feedparser.parse(body)
    if feed.bozo:
        logger.warning("Feed parse warning %s: %s", source.name, feed.bozo_exception)

    for entry in feed.entries:
        stats["fetched"] += 1
        url = entry.get("link")
        title = entry.get("title", "").strip()
        if not url or not title:
            stats["skipped"] += 1
            continue

        summary = entry.get("summary", "") or entry.get("description", "") or ""
        content = ""
        content_list = entry.get("content")
        if content_list:
            try:
                content = content_list[0].get("value", "")
            except Exception:  # noqa: BLE001
                content = ""

        # Keyword filter pro generické feedy
        combined = f"{title}\n{summary}\n{content}"
        if source.keywords and not _contains_any(combined, source.keywords):
            stats["skipped"] += 1
            continue

        # Dedup přes URL
        existing = (
            await session.execute(select(NewsItem).where(NewsItem.url == url))
        ).scalar_one_or_none()
        if existing is not None:
            stats["skipped"] += 1
            continue

        published = _parse_published(entry)

        news = NewsItem(
            url=url,
            source=source.name,
            title=title[:1000],
            summary=summary[:5000] if summary else None,
            content=content[:20000] if content else None,
            published_at=published,
            fetched_at=datetime.now(timezone.utc),
            tags=[source.tier],
        )
        session.add(news)
        stats["saved"] += 1

    await session.flush()
    logger.info(
        "RSS %s: fetched=%d saved=%d skipped=%d errors=%d",
        source.name,
        stats["fetched"],
        stats["saved"],
        stats["skipped"],
        stats["errors"],
    )
    return stats


async def fetch_all_rss(session: AsyncSession) -> dict[str, dict[str, int]]:
    """Fetch všech RSS zdrojů z SOURCES konfigurace."""
    from app.scrapers.sources import SOURCES

    results: dict[str, dict[str, int]] = {}
    for src in SOURCES:
        if src.type != "rss":
            continue
        results[src.name] = await fetch_rss(src, session)
    await session.commit()
    return results
