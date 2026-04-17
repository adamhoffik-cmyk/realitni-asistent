"""Wrapper okolo `claude-agent-sdk` — volá Claude Code CLI nainstalovaný na hostovi.

Využívá Claude Max subscription (žádné API klíče, žádné per-token platby).
SDK automaticky detekuje `claude` binárku na hostu.

Předpoklady:
1. `/usr/bin/claude` existuje (na VPS Ubuntu 24.04 ✓)
2. Je přihlášený `claude login` → Claude Max
3. Plugin `legal@realitni-asistent-local` nainstalovaný (user scope)
4. Backend container má mount `~/.claude` z hostu (viz docker-compose.yml)

Streaming eventy, které vrací stream():
- token      — jeden chunk textu (typewriter UI na frontendu)
- tool_call  — AI rozhoduje použít nástroj
- tool_result — výsledek nástroje
- done       — konec odpovědi + usage
- error      — chyba
"""
from __future__ import annotations

import logging
import shutil
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
    type: str  # token | tool_call | tool_result | done | error
    data: Any


class ClaudeClient:
    """Wrapper nad claude-agent-sdk."""

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
            self._available = (
                shutil.which(self.cli_path) is not None
                or shutil.which("claude") is not None
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Claude CLI check failed: %s", exc)
            self._available = False
        return self._available

    async def stream(
        self,
        messages: list[ClaudeMessage],
        system_prompt: str | None = None,
        allowed_tools: list[str] | None = None,
        cwd: str | None = None,
    ) -> AsyncIterator[ClaudeStreamEvent]:
        """Streamuje odpověď z Clauda.

        Argumenty:
            messages: historie konverzace (poslední je user).
            system_prompt: system prompt modifier (např. z skill contextu).
            allowed_tools: whitelist toolů. Default None = plugin defaults.
            cwd: working directory pro Claude (default: /app).
        """
        if not await self.is_available():
            yield ClaudeStreamEvent(
                type="error",
                data="Claude Code CLI není dostupný na hostu. Nainstaluj ho a přihlaš se do Claude Max.",
            )
            return

        # Claude Agent SDK import — lazy, aby nepadal app startup, když sdk chybí
        try:
            from claude_agent_sdk import ClaudeAgentOptions, query
        except ImportError as exc:
            yield ClaudeStreamEvent(type="error", data=f"claude-agent-sdk import failed: {exc}")
            return

        # Sestavit prompt — last user message jako vstup
        user_messages = [m for m in messages if m.role == "user"]
        if not user_messages:
            yield ClaudeStreamEvent(type="error", data="Žádná uživatelská zpráva")
            return
        prompt = user_messages[-1].content

        # History kontext (všechny předchozí turny) přidáme do system promptu
        history_text = ""
        if len(messages) > 1:
            history_lines = []
            for m in messages[:-1]:
                label = {"user": "Uživatel", "assistant": "Asistent", "system": "Systém"}.get(
                    m.role, m.role
                )
                history_lines.append(f"{label}: {m.content}")
            history_text = "\n\nPředchozí konverzace:\n" + "\n".join(history_lines)

        full_system_prompt = (system_prompt or "") + history_text
        if not full_system_prompt.strip():
            full_system_prompt = None

        options = ClaudeAgentOptions(
            include_partial_messages=True,
            system_prompt=full_system_prompt,
            cwd=cwd or "/app",
            # bypassPermissions — Claude v subprocess módu nevyžaduje
            # interactive approval pro MCP / plugin nástroje. Aplikace je
            # naše, všechny tooly jsou dopředu schválené.
            permission_mode="bypassPermissions",
        )
        if allowed_tools:
            options.allowed_tools = allowed_tools

        total_output_tokens = 0

        try:
            async for msg in query(prompt=prompt, options=options):
                # Rozlišit typ události
                msg_type = type(msg).__name__

                # StreamEvent — inkrementální token/tool updaty
                if msg_type == "StreamEvent":
                    event = getattr(msg, "event", None)
                    if not event:
                        continue
                    ev_type = event.get("type")

                    # Text delta → token event
                    if ev_type == "content_block_delta":
                        delta = event.get("delta", {})
                        if delta.get("type") == "text_delta":
                            text = delta.get("text", "")
                            if text:
                                yield ClaudeStreamEvent(type="token", data=text)
                        elif delta.get("type") == "input_json_delta":
                            # Tool input builds up — neposíláme průběžně
                            pass

                    # Tool use start
                    elif ev_type == "content_block_start":
                        block = event.get("content_block", {})
                        if block.get("type") == "tool_use":
                            yield ClaudeStreamEvent(
                                type="tool_call",
                                data={
                                    "id": block.get("id"),
                                    "name": block.get("name"),
                                },
                            )

                # AssistantMessage — hotová zpráva (po všech StreamEvents)
                elif msg_type == "AssistantMessage":
                    # Obsah už byl vyposílaný přes StreamEvents
                    pass

                # ToolResultBlock / UserMessage s tool result
                elif msg_type in ("ToolResultMessage", "UserMessage"):
                    # Nemusíme se tím teď zaobírat — tool_result může jít po SDK smyčce
                    pass

                # ResultMessage — finální status s usage + cost
                elif msg_type == "ResultMessage":
                    usage = getattr(msg, "usage", None)
                    if usage:
                        total_output_tokens = getattr(usage, "output_tokens", 0)
                    cost = getattr(msg, "total_cost_usd", None)
                    yield ClaudeStreamEvent(
                        type="done",
                        data={
                            "tokens": total_output_tokens,
                            "cost_usd": cost,
                        },
                    )
                    return

                # System / Init messages (debug)
                elif msg_type == "SystemMessage":
                    logger.debug("SystemMessage: %s", msg)

                else:
                    logger.debug("Unknown msg type %s: %s", msg_type, msg)

            # Fallback: když SDK skončí bez ResultMessage
            yield ClaudeStreamEvent(
                type="done", data={"tokens": total_output_tokens, "cost_usd": None}
            )

        except Exception as exc:  # noqa: BLE001
            logger.exception("Claude stream error")
            yield ClaudeStreamEvent(type="error", data=f"Claude SDK chyba: {exc}")


_client: ClaudeClient | None = None


def get_claude_client() -> ClaudeClient:
    global _client
    if _client is None:
        _client = ClaudeClient()
    return _client
