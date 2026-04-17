"""Wrapper okolo `claude-agent-sdk` — volá Claude Code CLI nainstalovaný na hostovi.

Tento modul je zatím STUB — konkrétní implementace přijde ve Fázi 1C/1D,
kdy bude hotové reálné volání SDK. Teď stačí, aby existoval interface.

Claude Code CLI musí být:
1. Nainstalovaný na hostovi (`/usr/bin/claude` nebo obdobně)
2. Přihlášený do Claude Max (`claude login`)
3. (Volitelně) mít nainstalovaný plugin `ceske-realitni-pravo`
"""
from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class ClaudeMessage:
    role: str  # user | assistant | system | tool
    content: str


@dataclass
class ClaudeStreamEvent:
    """Jedna událost ze streamu — text token, tool call, tool result, done, error."""
    type: str  # "token" | "tool_call" | "tool_result" | "done" | "error"
    data: Any


class ClaudeClient:
    """Wrapper nad claude-agent-sdk.

    Zatím STUB — skutečné volání bude implementováno, až budeme mít hotový
    context builder + definované tooly.
    """

    def __init__(self) -> None:
        self.cli_path = settings.claude_cli_path
        self.timeout = settings.claude_session_timeout
        self.max_tokens = settings.claude_max_tokens
        self._available: bool | None = None

    async def is_available(self) -> bool:
        """Ověří, zda je Claude Code CLI dostupný."""
        if self._available is not None:
            return self._available
        try:
            import shutil
            self._available = shutil.which(self.cli_path) is not None or bool(
                shutil.which("claude")
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Claude CLI check failed: %s", exc)
            self._available = False
        return self._available

    async def stream(
        self,
        messages: list[ClaudeMessage],
        system_prompt: str | None = None,
        tools: list[dict] | None = None,
    ) -> AsyncIterator[ClaudeStreamEvent]:
        """Streamuje odpověď z Clauda.

        STUB: Dočasná implementace, která vrátí fake tokenizovanou odpověď.
        Bude nahrazeno reálným voláním claude-agent-sdk ve Fázi 1D.
        """
        if not await self.is_available():
            yield ClaudeStreamEvent(
                type="error",
                data="Claude Code CLI není dostupný. Nainstaluj ho a přihlaš se do Claude Max.",
            )
            return

        # STUB odpověď — echo poslední uživatelské zprávy
        last_user = next(
            (m.content for m in reversed(messages) if m.role == "user"),
            "",
        )
        stub_response = (
            f"🟢 [STUB] Claude wrapper zatím jen echuje. "
            f"Dostal jsem: {last_user!r}. "
            f"Reálné volání bude implementováno ve Fázi 1D."
        )
        for ch in stub_response:
            yield ClaudeStreamEvent(type="token", data=ch)
        yield ClaudeStreamEvent(type="done", data={"tokens": len(stub_response)})


_client: ClaudeClient | None = None


def get_claude_client() -> ClaudeClient:
    global _client
    if _client is None:
        _client = ClaudeClient()
    return _client
