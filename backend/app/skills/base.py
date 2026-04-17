"""BaseSkill — abstraktní kontrakt pro všechny skilly."""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel


class ToolDef(BaseModel):
    """Definice AI toolu poskytovaného skillem."""
    name: str
    description: str
    parameters_schema: dict[str, Any]
    # handler se registruje samostatně (nelze serializovat do Pydanticu)

    class Config:
        arbitrary_types_allowed = True


class SkillManifest(BaseModel):
    id: str
    name: str
    description: str
    icon: str | None = None
    order_index: int = 100
    version: str = "0.1.0"
    chat_context_prompt: str | None = None
    chat_aliases: list[str] = []
    tile_preview: str | None = None


class BaseSkill(ABC):
    """Abstraktní base pro skill moduly.

    Každý skill MUSÍ:
    - definovat `manifest` (SkillManifest)
    - implementovat `api_router()`
    - implementovat `ai_tools()`
    - implementovat `on_register()` (idempotentní init)
    """

    manifest: SkillManifest

    @abstractmethod
    async def on_register(self) -> None:
        """Volá se jednou při bootstrap aplikace."""
        raise NotImplementedError

    @abstractmethod
    def api_router(self) -> APIRouter:
        """FastAPI router s endpointy skillu."""
        raise NotImplementedError

    @abstractmethod
    def ai_tools(self) -> list[ToolDef]:
        """Tooly, které skill vystaví Claudovi."""
        raise NotImplementedError

    async def on_chat_invoke(
        self, message: str, context: dict[str, Any]
    ) -> AsyncIterator[str] | None:
        """Volitelný hook pro slash commands.

        Vrátí async generátor textových chunků, pokud skill zpracuje zprávu sám.
        Vrátí None pro default routing přes Claude.
        """
        return None

    async def tile_data(self) -> dict[str, Any]:
        """Live data pro dlaždici na home screen."""
        return {}
