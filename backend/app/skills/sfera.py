"""Skill Sféra vlivu."""
from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import func, select

from app.db import AsyncSessionLocal
from app.models.db_models import SpheraPerson
from app.skills.base import BaseSkill, SkillManifest, ToolDef


class SpheraSkill(BaseSkill):
    manifest = SkillManifest(
        id="sfera",
        name="Sféra vlivu",
        description="Evidence osobní sféry vlivu + reminders 3× ročně. Generování osobního kontaktu.",
        icon="family",
        order_index=40,
        chat_context_prompt=(
            "Jsi v režimu správy sféry vlivu. Cíl: každých 4 měsíců se ozvat "
            "všem z osobní sféry. Umíš: návrh textu kontaktu (WhatsApp/SMS/e-mail) "
            "na základě toho, co o osobě víš (jen z neobčasný kontakt, ne "
            "marketingový spam). Nikdy necituj rodná čísla."
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
            total = (
                await db.execute(select(func.count(SpheraPerson.id)))
            ).scalar() or 0
            return {"osob": int(total)}
