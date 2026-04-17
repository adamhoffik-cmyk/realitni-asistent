"""APScheduler setup & lifecycle."""
from __future__ import annotations

import logging

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.config import get_settings
from app.scheduler.jobs import job_fetch_news, job_morning_briefing

logger = logging.getLogger(__name__)


_scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler | None:
    return _scheduler


def start_scheduler() -> AsyncIOScheduler:
    """Vytvoří a spustí scheduler. Joby persistují v SQLite."""
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    settings = get_settings()

    # Jobstore v hlavní app.db (separátní tabulka `apscheduler_jobs`)
    jobstores = {
        "default": SQLAlchemyJobStore(url=settings.database_url.replace(
            "sqlite+aiosqlite://", "sqlite://"
        ).replace("sqlite:///", "sqlite:///"))
    }

    _scheduler = AsyncIOScheduler(
        jobstores=jobstores,
        timezone=settings.scheduler_timezone,
    )

    # --- Joby ---
    _scheduler.add_job(
        job_fetch_news,
        IntervalTrigger(minutes=settings.news_scrape_interval_minutes),
        id="fetch_news",
        name="Fetch RSS news",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    _scheduler.add_job(
        job_morning_briefing,
        CronTrigger(
            hour=settings.briefing_cron_hour,
            minute=settings.briefing_cron_minute,
        ),
        id="morning_briefing",
        name="Ranní briefing",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    _scheduler.start()
    logger.info(
        "Scheduler started — news every %dmin, briefing %02d:%02d",
        settings.news_scrape_interval_minutes,
        settings.briefing_cron_hour,
        settings.briefing_cron_minute,
    )
    return _scheduler


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
