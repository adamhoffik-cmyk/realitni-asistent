"""Skill Video → Scénář."""
from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import func, select

from app.db import AsyncSessionLocal
from app.models.db_models import VideoScript
from app.skills.base import BaseSkill, SkillManifest, ToolDef


class VideoTranscriptSkill(BaseSkill):
    manifest = SkillManifest(
        id="video-transcript",
        name="Video → Scénář",
        description="Transkripce cizího IG/FB/TikTok videa a generování scénáře pro tvé vlastní video ve tvém stylu.",
        icon="media-video",
        order_index=20,
        chat_context_prompt=(
            "Jsi v režimu práce s videem. Uživatel vkládá URL cizího videa, "
            "ty pomáháš s brainstormingem vlastního obsahu — scénář (hook/body/CTA), "
            "návrhy B-roll, optimalizace pro IG Reel/TikTok, testování více hook variant."
        ),
    )

    async def on_register(self) -> None:
        return None

    def api_router(self) -> APIRouter:
        router = APIRouter()

        @router.get("/info")
        async def info() -> dict:
            return {"skill": "video-transcript", "version": self.manifest.version}

        return router

    def ai_tools(self) -> list[ToolDef]:
        return []

    async def tile_data(self) -> dict[str, int]:
        async with AsyncSessionLocal() as db:
            total = (await db.execute(select(func.count(VideoScript.id)))).scalar() or 0
            return {"transkripty": total}
