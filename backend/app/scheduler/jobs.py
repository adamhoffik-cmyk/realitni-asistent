"""APScheduler joby."""
from __future__ import annotations

import logging

from app.db import AsyncSessionLocal
from app.scrapers.rss import fetch_all_rss

logger = logging.getLogger(__name__)


async def job_fetch_news() -> None:
    """Periodický fetch všech RSS zdrojů."""
    logger.info("Scheduler: fetch_news start")
    async with AsyncSessionLocal() as session:
        try:
            stats = await fetch_all_rss(session)
            total_saved = sum(s["saved"] for s in stats.values())
            logger.info(
                "Scheduler: fetch_news DONE — %d new items from %d sources",
                total_saved,
                len(stats),
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("fetch_news failed: %s", exc)


async def job_morning_briefing() -> None:
    """Ranní briefing — 7:00.

    TODO Fáze 5: sestavit briefing přes AI (počasí + kalendář + top news + úkoly)
    a uložit do `briefings` tabulky.
    """
    logger.info("Scheduler: morning_briefing stub (implement v2-E / Fáze 5)")
