"""Context builder — sestaví system prompt + RAG kontext pro Claude.

Vstupy:
- Aktuální user query
- Kontext obrazovky (home, skill id)
- Historie turnů v session

Výstupy:
- system_prompt: kompletní prompt pro Claude (role, kontext, RAG hits)
- allowed_tools: seznam nástrojů Claude Code CLI
"""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core import memory as mem
from app.skills.registry import SkillRegistry


_CZ_DAYS = [
    "pondělí",
    "úterý",
    "středa",
    "čtvrtek",
    "pátek",
    "sobota",
    "neděle",
]
_CZ_MONTHS = [
    "",
    "ledna",
    "února",
    "března",
    "dubna",
    "května",
    "června",
    "července",
    "srpna",
    "září",
    "října",
    "listopadu",
    "prosince",
]


def _now_prompt_block() -> str:
    """Vrátí lidsky čitelný blok s aktuálním datem a časem v CZ timezone."""
    settings = get_settings()
    tz = ZoneInfo(settings.app_timezone or "Europe/Prague")
    now = datetime.now(tz)
    day_name = _CZ_DAYS[now.weekday()]
    month_name = _CZ_MONTHS[now.month]
    return (
        f"Aktuální datum a čas: **{day_name} {now.day}. {month_name} {now.year}, "
        f"{now.strftime('%H:%M')}** (timezone {tz.key}). "
        f"Data z tvého tréninku mohou být starší — vždy ber jako pravdu tento čas."
    )


BASE_SYSTEM_PROMPT = """Jsi osobní AI asistent realitního makléře Adama Hoffíka
(RE/MAX Living Česká Lípa, web reality-pittner.cz).

Pravidla:
- Odpovídej VŽDY česky, pokud výslovně nenapíše jinak
- Buď stručný a přímý — Adam nesnáší kecání okolo
- U právních témat (smlouvy, ZRZ, OZ, GDPR, AML) VYUŽIJ plugin legal
  (skills: review-contract, triage-nda, legal-risk-assessment, compliance-check,
  legal-response). Ten pokrývá české realitní právo.
- VŽDY u právních rad přidej disclaimer: "Toto není právní rada.
  Pro konkrétní případy konzultujte advokáta."
- Rodná čísla NIKDY necituj v odpovědích (ani kdyby byla v paměti).
- Když něco nevíš, řekni to. Nevymýšlej si.

Když pracuješ s kalendářem / e-mailem / Drive — využij MCP servery
nainstalované pluginem legal (gmail, google-calendar, google-drive).
"""


async def build_system_prompt(
    session: AsyncSession,
    *,
    user_message: str,
    context: str = "home",
    skill_chat_prompt: str | None = None,
    rag_limit: int = 5,
) -> str:
    """Sestaví system prompt s:
    1. Base role (kdo je AI)
    2. Aktuální kontext obrazovky (home / skill)
    3. Top-K relevantních vzpomínek z ChromaDB
    """
    parts = [BASE_SYSTEM_PROMPT, _now_prompt_block()]

    # --- Context info ---
    if context and context != "home":
        skill = SkillRegistry.get(context)
        if skill is not None:
            parts.append(
                f"\n--- AKTUÁLNÍ KONTEXT ---\n"
                f"Uživatel je v módu: {skill.manifest.name} ({skill.manifest.id})"
            )
            if skill.manifest.chat_context_prompt:
                parts.append(skill.manifest.chat_context_prompt)
    elif skill_chat_prompt:
        parts.append(skill_chat_prompt)

    # --- RAG hits ---
    try:
        hits = await mem.search(session, query=user_message, limit=rag_limit)
        if hits:
            rag_section = ["\n--- RELEVANTNÍ ZÁZNAMY Z PAMĚTI ---"]
            for note, score in hits:
                if score < 0.3:
                    continue  # příliš vzdálené
                tag_str = f" [{', '.join(note.tags)}]" if note.tags else ""
                title = note.title or "(bez titulu)"
                rag_section.append(
                    f"\n• [{note.type}] {title}{tag_str} (relevance {score:.2f}):\n  "
                    + note.content[:500].replace("\n", "\n  ")
                )
            if len(rag_section) > 1:
                parts.append("\n".join(rag_section))
    except Exception as exc:  # noqa: BLE001
        # RAG selhání nemá shodit chat
        parts.append(f"\n[RAG nedostupný: {exc}]")

    return "\n\n".join(parts)


def resolve_allowed_tools(context: str = "home") -> list[str] | None:
    """Whitelist toolů pro Claude podle kontextu.

    Default (None): plugin default tools — vše povolené včetně MCP serverů.
    Pro skill-specific kontext můžeme zúžit.
    """
    # Pro MVP: default = vše.
    return None
