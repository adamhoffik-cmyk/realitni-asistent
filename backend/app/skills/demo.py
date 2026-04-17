"""Demo skill — ověřuje, že skill systém funguje end-to-end.

Bude odstraněn v pozdější fázi, až naběhnou Skill 1 (articles) a Skill 2 (video-transcript).
"""
from __future__ import annotations

from fastapi import APIRouter

from app.skills.base import BaseSkill, SkillManifest, ToolDef


class DemoSkill(BaseSkill):
    manifest = SkillManifest(
        id="demo",
        name="Demo",
        description="Ukázkový skill pro ověření registry + dlaždice + routing.",
        icon="award",
        order_index=999,
        chat_context_prompt=(
            "Jsi v demo režimu — pokus se v odpovědích krátce zmínit, že tohle je ukázkový skill "
            "pro ověření plugin systému."
        ),
    )

    async def on_register(self) -> None:
        # zde by mohly být migrace, init modelu, atd. — v demo skillu nic.
        return None

    def api_router(self) -> APIRouter:
        router = APIRouter()

        @router.get("/ping")
        async def ping() -> dict[str, str]:
            return {"skill": "demo", "pong": "🟢"}

        return router

    def ai_tools(self) -> list[ToolDef]:
        return []

    async def tile_data(self) -> dict[str, str]:
        return {"status": "ready"}
