"""FastAPI aplikace — entry point."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api import chat, health, skills, weather
from app.config import get_settings
from app.db import Base, engine, enable_sqlite_wal
from app.skills.registry import SkillRegistry

# Logging setup
settings = get_settings()
logging.basicConfig(
    level=settings.backend_log_level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown hooks."""
    logger.info("Realitní Asistent backend %s (env=%s) startuje…", __version__, settings.app_env)

    # Zajisti tabulky (v produkci přes Alembic, v dev pohodlí)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await enable_sqlite_wal()

    # Bootstrap skillů
    await SkillRegistry.bootstrap()

    # Mount skill routerů
    for skill in SkillRegistry.all():
        app.include_router(
            skill.api_router(),
            prefix=f"/api/skills/{skill.manifest.id}",
            tags=[f"skill:{skill.manifest.id}"],
        )
        logger.info("Skill %s router namountován", skill.manifest.id)

    logger.info("Startup dokončen ✓")
    yield
    logger.info("Realitní Asistent backend se zastavuje")


app = FastAPI(
    title="Realitní Asistent API",
    version=__version__,
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routery
app.include_router(health.router, prefix="/api")
app.include_router(weather.router, prefix="/api")
app.include_router(skills.router, prefix="/api")
app.include_router(chat.router, prefix="/api")


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "app": "Realitní Asistent API",
        "version": __version__,
        "docs": "/api/docs",
    }
