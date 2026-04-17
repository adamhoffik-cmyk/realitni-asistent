"""Database setup — SQLAlchemy async engine pro SQLite."""
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

# SQLite URL → aiosqlite driver
_url = settings.database_url
if _url.startswith("sqlite:///"):
    _url = _url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)

engine = create_async_engine(
    _url,
    echo=settings.backend_log_level == "DEBUG",
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in _url else {},
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Společný base pro všechny ORM modely."""


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency — yielduje session pro jeden request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@asynccontextmanager
async def session_scope() -> AsyncIterator[AsyncSession]:
    """Kontext manager pro skripty / schedulery (mimo FastAPI request)."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def enable_sqlite_wal() -> None:
    """Zapne WAL mode — lepší výkon pro single-writer SQLite."""
    if "sqlite" not in _url:
        return
    async with engine.begin() as conn:
        await conn.exec_driver_sql("PRAGMA journal_mode=WAL")
        await conn.exec_driver_sql("PRAGMA synchronous=NORMAL")
        await conn.exec_driver_sql("PRAGMA foreign_keys=ON")
