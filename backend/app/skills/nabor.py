"""Skill Nábor tracker."""
from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import func, select

from app.db import AsyncSessionLocal
from app.models.db_models import NaborActivity
from app.skills.base import BaseSkill, SkillManifest, ToolDef


class NaborSkill(BaseSkill):
    manifest = SkillManifest(
        id="nabor",
        name="Nábor",
        description="Tracker náborových aktivit — dopisy, cold cally, schůzky. Dashboard vs. týdenní cíl.",
        icon="contact",
        order_index=30,
        chat_context_prompt=(
            "Jsi v režimu náborového trackeru. Pomáháš Adamovi evidovat a analyzovat "
            "náborové aktivity (dopisy majitelům, cold cally, sféra vlivu). "
            "Cíl: 150 dopisů týdně, 20-30 cold callů denně. "
            "Reportuj progres proti cíli, navrhuj optimalizace, generuj call scripts."
        ),
    )

    async def on_register(self) -> None:
        return None

    def api_router(self) -> APIRouter:
        return APIRouter()

    def ai_tools(self) -> list[ToolDef]:
        return []

    async def tile_data(self) -> dict[str, int]:
        async with AsyncSessionLocal() as db:
            from datetime import date, timedelta

            week_ago = (date.today() - timedelta(days=7)).isoformat()
            total = (
                await db.execute(
                    select(func.sum(NaborActivity.count)).where(
                        NaborActivity.date >= week_ago
                    )
                )
            ).scalar() or 0
            return {"7 dní": int(total)}
