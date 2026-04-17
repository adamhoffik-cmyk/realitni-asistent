"""Skill Články — registrace v home skill tiles.

Samotná funkcionalita je v `app/api/articles.py`. Tenhle skill jen
poskytuje manifest pro UI dlaždici + chat context.
"""
from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import func, select

from app.db import AsyncSessionLocal
from app.models.db_models import Article
from app.skills.base import BaseSkill, SkillManifest, ToolDef


class ArticlesSkill(BaseSkill):
    manifest = SkillManifest(
        id="articles",
        name="Články",
        description="Generování a legalizace článků z URL nebo tématu. Režim A (nové téma), Režim B (ze zdroje).",
        icon="document",
        order_index=10,
        chat_context_prompt=(
            "Jsi v režimu psaní článků pro realitního makléře. "
            "Pomáháš s brainstormingem témat, SEO analýzou, návrhy nadpisů, "
            "kontrolou faktů, přepsáním existujícího článku vlastními slovy. "
            "Vždy dodržuj zásadu: NIKDY doslovně necituj cizí zdroj — přidej "
            "hodnotu, vlastní úhel, českou realitní praxi."
        ),
    )

    async def on_register(self) -> None:
        return None

    def api_router(self) -> APIRouter:
        # Skutečné endpointy jsou v app/api/articles.py (mountované z main.py).
        # Skill router je zde pro případné skill-specific endpointy (tile/info atd.)
        router = APIRouter()

        @router.get("/info")
        async def info() -> dict:
            return {"skill": "articles", "version": self.manifest.version}

        return router

    def ai_tools(self) -> list[ToolDef]:
        return []

    async def tile_data(self) -> dict[str, int]:
        async with AsyncSessionLocal() as db:
            total = (await db.execute(select(func.count(Article.id)))).scalar() or 0
            drafts = (
                await db.execute(
                    select(func.count(Article.id)).where(Article.status == "draft")
                )
            ).scalar() or 0
            return {"celkem": total, "drafty": drafts}
