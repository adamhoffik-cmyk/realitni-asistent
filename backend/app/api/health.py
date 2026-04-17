"""Health check endpoint."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

from app import __version__
from app.config import get_settings
from app.core.claude_client import get_claude_client
from app.models.schemas import HealthResponse

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        version=__version__,
        env=settings.app_env,
        timestamp=datetime.now(timezone.utc),
    )


@router.get("/health/deep")
async def health_deep() -> dict:
    """Hluboký health check — ověří jednotlivé komponenty."""
    settings = get_settings()
    claude = get_claude_client()

    return {
        "status": "ok",
        "version": __version__,
        "env": settings.app_env,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {
            "claude_cli_available": await claude.is_available(),
            "embedding_model": settings.embedding_model,
            "whisper_model": settings.whisper_model,
            "database_url": settings.database_url.replace(
                settings.backend_secret_key, "***"
            ) if settings.backend_secret_key in settings.database_url else settings.database_url,
        },
    }
