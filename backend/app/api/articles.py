"""Articles API — CRUD + generování z URL přes Claude SDK.

Fáze 3 stub — generování je implementováno, ale stylebook analýza
(analýza artem-saykin.cz) přijde ve Fázi 3-B.
"""
from __future__ import annotations

import logging
import re
import uuid
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.claude_client import ClaudeMessage, get_claude_client
from app.db import get_db
from app.models.db_models import Article, FavoriteNews
from app.models.schemas import ORMBase

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/articles", tags=["articles"])


class ArticleOut(ORMBase):
    id: str
    slug: str
    title: str
    status: str
    mode: str
    content_md: str
    meta_description: str | None
    keywords: list[str] | None
    source_url: str | None
    created_at: datetime
    updated_at: datetime


class GenerateArticleIn:  # pydantic model below (abbrev. for naming)
    pass


def _slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[áàâäã]", "a", s)
    s = re.sub(r"[éèêë]", "e", s)
    s = re.sub(r"[íìîï]", "i", s)
    s = re.sub(r"[óòôöõ]", "o", s)
    s = re.sub(r"[úùûü]", "u", s)
    s = re.sub(r"[ýÿ]", "y", s)
    s = s.replace("č", "c").replace("ď", "d").replace("ě", "e")
    s = s.replace("ň", "n").replace("ř", "r").replace("š", "s")
    s = s.replace("ť", "t").replace("ž", "z")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:80] or "clanek"


@router.get("", response_model=list[ArticleOut])
async def list_articles(
    status: str | None = None,
    session: AsyncSession = Depends(get_db),
) -> list[ArticleOut]:
    stmt = select(Article).order_by(desc(Article.updated_at))
    if status:
        stmt = stmt.where(Article.status == status)
    rows = (await session.execute(stmt)).scalars().all()
    return [ArticleOut.model_validate(r) for r in rows]


@router.get("/{article_id}", response_model=ArticleOut)
async def get_article(
    article_id: str, session: AsyncSession = Depends(get_db)
) -> ArticleOut:
    art = (
        await session.execute(select(Article).where(Article.id == article_id))
    ).scalar_one_or_none()
    if art is None:
        raise HTTPException(status_code=404, detail="Článek nenalezen")
    return ArticleOut.model_validate(art)


@router.post("/generate", response_model=ArticleOut)
async def generate_article(
    payload: dict = Body(...),
    session: AsyncSession = Depends(get_db),
) -> ArticleOut:
    """Generuj článek z URL (Režim B — legalizace) nebo z tématu (Režim A).

    payload: {
      source_url?: str,     # URL zdroje (Režim B)
      topic?: str,          # téma (Režim A)
      favorite_id?: str,    # ID oblíbené novinky (propojíme po vygenerování)
    }
    """
    source_url = payload.get("source_url")
    topic = payload.get("topic")
    favorite_id = payload.get("favorite_id")

    if not source_url and not topic:
        raise HTTPException(400, detail="Zadej source_url nebo topic")

    mode = "B_legalized" if source_url else "A_new"

    # 1. Pokud máme URL, stáhni obsah
    source_content = ""
    if source_url:
        try:
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
                resp = await client.get(
                    source_url,
                    headers={"User-Agent": "Realitni-Asistent/1.0"},
                )
                resp.raise_for_status()
                # Použij trafilatura na clean extract
                import trafilatura

                source_content = (
                    trafilatura.extract(resp.text, include_comments=False)
                    or resp.text[:10000]
                )
        except Exception as exc:
            logger.warning("Fetch source_url failed: %s", exc)
            source_content = f"(Zdroj nedostupný: {exc})"

    # 2. Připrav system prompt pro Claude — research-first
    if mode == "B_legalized":
        prompt = f"""Vygeneruj mi vlastní článek na téma tohoto zdroje, ale NECITUJ
doslovně — přepiš vlastními slovy, přidej vlastní úhel pohledu, pomoz
českému realitnímu makléři. Délka ~600-900 slov, v češtině, v markdown.

ZDROJOVÝ URL: {source_url}

ZDROJOVÝ OBSAH:
---
{source_content[:8000]}
---

DŮLEŽITÉ:
1) PŘED napsáním článku použij WebSearch a ověř všechna klíčová fakta
   pro rok 2026 — zvlášť číselné limity (Kč), novely zákonů, sazby ČNB,
   ceny nemovitostí. Autor zdroje nemusí být aktuální.
2) Speciálně si ověř: limity drobných oprav nájemníka (nařízení vlády
   308/2015 + novely), změny ZRZ 39/2020, RP daňové limity pro rok 2026.
3) Pokud je v originále nějaké číslo v Kč nebo rok, ověř ho websearchem.
4) U právních pasáží vždy cituj konkrétní zákon / nařízení a rok novely.
5) Přidej disclaimer: "Toto není právní rada. Pro konkrétní případy
   konzultujte advokáta."

Vrať POUZE markdown obsah článku (bez metadat, bez úvodních "Zde je článek:").
Začni nadpisem # a pak obsah."""
    else:
        prompt = f"""Napiš mi nový článek na téma: "{topic}"

Cílová skupina: kupující / prodávající nemovitostí v ČR 2026.
Délka: 600-900 slov, český jazyk, markdown.
Styl: profesionální ale lidský, s konkrétními příklady, checklist body
kde to dává smysl.

DŮLEŽITÉ:
1) PŘED napsáním použij WebSearch a najdi aktuální data pro 2026 —
   zákonné limity, ČNB sazby, statistiky, novely.
2) Uvažuj, co by v článku NEMĚLO chybět: konkrétní limity v Kč,
   čísla zákonů a jejich novely, odkazy na ČNB/ČSÚ pokud relevantní.
3) Pokud jsou relevantní právní aspekty (ZRZ 39/2020, OZ 89/2012,
   GDPR, AML, nařízení 308/2015), zahrň je s disclaimerem.

Vrať POUZE markdown obsah článku (# nadpis + obsah)."""

    # 3. Stream od Claude — povolit WebSearch + WebFetch
    claude = get_claude_client()
    buffer: list[str] = []
    error_msg: str | None = None

    async for event in claude.stream(
        messages=[ClaudeMessage(role="user", content=prompt)],
        system_prompt=(
            "Jsi copywriter realitního makléře. Piš česky, věcně, s přidanou "
            "hodnotou. VŽDY ověř číselné limity a právní fakta přes WebSearch "
            "před tím, než je napíšeš do článku — Claude data končí v lednu 2025."
        ),
        allowed_tools=["WebSearch", "WebFetch", "Read", "Grep", "Glob"],
    ):
        if event.type == "token":
            buffer.append(event.data)
        elif event.type == "error":
            error_msg = str(event.data)
            break
        elif event.type == "done":
            break

    if error_msg:
        raise HTTPException(502, detail=f"Claude chyba: {error_msg}")

    content_md = "".join(buffer).strip()
    if not content_md:
        raise HTTPException(502, detail="Claude vrátil prázdný obsah")

    # 3b. Self-review pass — druhý Claude call kontroluje draft
    review_prompt = f"""Jsi editor článku o realitách pro český trh 2026.

Zde je DRAFT článku:
---
{content_md}
---

ÚKOL: Projdi draft a vyhodnoť, jestli mu něco CHYBÍ, co by bylo důležité.
Konkrétně:
- Chybí konkrétní číselné limity v Kč (třeba limit drobných oprav
  nájemníka podle nařízení 308/2015, daňové limity, ČNB sazby)?
- Chybí reference na aktuální zákony a jejich novely (2026)?
- Chybí praktické příklady nebo checklist?
- Je článek správně zacílený na realitního klienta v ČR?

Pokud nic zásadního nechybí, vrať pouze text: OK
Pokud něco chybí, PŘEPIŠ celý článek s doplněnými informacemi (použij
WebSearch pro ověření faktů 2026) a vrať celý opravený markdown.
"""

    try:
        review_buffer: list[str] = []
        async for event in claude.stream(
            messages=[ClaudeMessage(role="user", content=review_prompt)],
            system_prompt="Jsi editor realitního obsahu. Přísný na fakta a úplnost.",
            allowed_tools=["WebSearch", "WebFetch"],
        ):
            if event.type == "token":
                review_buffer.append(event.data)
            elif event.type == "error":
                break
            elif event.type == "done":
                break
        review_text = "".join(review_buffer).strip()
        # Pokud editor vrátil opravu (začíná # nebo obsahuje >200 znaků), použij ji
        if review_text and not review_text.upper().startswith("OK") and len(review_text) > 300:
            logger.info("Self-review upgraded article (+%d chars)", len(review_text) - len(content_md))
            content_md = review_text
    except Exception as exc:  # noqa: BLE001
        logger.warning("Self-review selhal: %s — ponechávám původní draft", exc)

    # Extrahuj nadpis z prvního # řádku
    title = topic or "Nový článek"
    lines = content_md.split("\n")
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break
        if line.startswith("#"):
            title = line.lstrip("#").strip()
            break

    slug_base = _slugify(title)
    slug = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}_{slug_base}"

    # 4. Ulož jako draft
    article = Article(
        id=str(uuid.uuid4()),
        slug=slug,
        title=title,
        status="draft",
        mode=mode,
        content_md=content_md,
        source_url=source_url,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    session.add(article)
    await session.flush()

    # 5. Propoj s oblíbenou, pokud je
    if favorite_id:
        fav = (
            await session.execute(select(FavoriteNews).where(FavoriteNews.id == favorite_id))
        ).scalar_one_or_none()
        if fav is not None:
            fav.article_id = article.id

    await session.commit()
    return ArticleOut.model_validate(article)


@router.patch("/{article_id}", response_model=ArticleOut)
async def update_article(
    article_id: str,
    payload: dict = Body(...),
    session: AsyncSession = Depends(get_db),
) -> ArticleOut:
    art = (
        await session.execute(select(Article).where(Article.id == article_id))
    ).scalar_one_or_none()
    if art is None:
        raise HTTPException(status_code=404, detail="Článek nenalezen")

    if "title" in payload:
        art.title = payload["title"]
    if "content_md" in payload:
        art.content_md = payload["content_md"]
    if "status" in payload:
        art.status = payload["status"]
    if "meta_description" in payload:
        art.meta_description = payload["meta_description"]
    if "keywords" in payload:
        art.keywords = payload["keywords"]
    art.updated_at = datetime.now(timezone.utc)

    await session.commit()
    return ArticleOut.model_validate(art)


@router.delete("/{article_id}", status_code=204)
async def delete_article(
    article_id: str, session: AsyncSession = Depends(get_db)
) -> None:
    art = (
        await session.execute(select(Article).where(Article.id == article_id))
    ).scalar_one_or_none()
    if art is None:
        raise HTTPException(status_code=404, detail="Článek nenalezen")
    await session.delete(art)
    await session.commit()
