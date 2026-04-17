"""Video transcript API — transkribuj + vygeneruj scénář pro tvé video."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.claude_client import ClaudeMessage, get_claude_client
from app.core.transcribe import transcribe_url
from app.db import get_db
from app.models.db_models import VideoScript
from app.models.schemas import ORMBase

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/videos", tags=["videos"])


class VideoScriptOut(ORMBase):
    id: str
    source_url: str
    transcript_md: str
    script_md: str | None
    duration_sec: int | None
    created_at: datetime


@router.get("", response_model=list[VideoScriptOut])
async def list_videos(
    session: AsyncSession = Depends(get_db),
) -> list[VideoScriptOut]:
    rows = (
        (
            await session.execute(
                select(VideoScript).order_by(desc(VideoScript.created_at))
            )
        )
        .scalars()
        .all()
    )
    return [VideoScriptOut.model_validate(r) for r in rows]


@router.get("/{video_id}", response_model=VideoScriptOut)
async def get_video(
    video_id: str, session: AsyncSession = Depends(get_db)
) -> VideoScriptOut:
    row = (
        await session.execute(select(VideoScript).where(VideoScript.id == video_id))
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(404, detail="Video nenalezeno")
    return VideoScriptOut.model_validate(row)


@router.post("/transcribe", response_model=VideoScriptOut)
async def create_transcript(
    payload: dict = Body(...),
    session: AsyncSession = Depends(get_db),
) -> VideoScriptOut:
    """Stáhne video z URL, transkribuje přes Whisper, uloží."""
    url = payload.get("url", "").strip()
    if not url:
        raise HTTPException(400, detail="Chybí url")

    try:
        result = await transcribe_url(url)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Transcribe failed")
        raise HTTPException(502, detail=f"Transkripce selhala: {exc}")

    transcript_md = f"""# Transkript — {result.source_title or '(bez názvu)'}

**Zdroj:** {url}
**Jazyk:** {result.language}
**Délka:** {result.duration_sec:.1f} s

---

{result.text}
"""

    video = VideoScript(
        id=str(uuid.uuid4()),
        source_url=url,
        transcript_md=transcript_md,
        duration_sec=int(result.duration_sec),
        created_at=datetime.now(timezone.utc),
    )
    session.add(video)
    await session.commit()
    return VideoScriptOut.model_validate(video)


@router.post("/{video_id}/generate-script", response_model=VideoScriptOut)
async def generate_script(
    video_id: str,
    payload: dict | None = Body(None),
    session: AsyncSession = Depends(get_db),
) -> VideoScriptOut:
    """Z transkriptu vygeneruj scénář pro mé vlastní video (Claude)."""
    row = (
        await session.execute(select(VideoScript).where(VideoScript.id == video_id))
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(404, detail="Video nenalezeno")

    target_format = (payload or {}).get("format", "reel_60s")  # reel_30s|reel_60s|fb_post|tiktok
    my_angle = (payload or {}).get("angle", "")  # volitelný vlastní úhel

    format_hint = {
        "reel_30s": "IG Reel 30 sekund (hook 3s, body 20s, CTA 7s)",
        "reel_60s": "IG Reel 60 sekund (hook 5s, body 45s, CTA 10s)",
        "fb_post": "FB post + video 90 sekund",
        "tiktok": "TikTok 30-60s, dynamický střih",
    }.get(target_format, "IG Reel 60 sekund")

    prompt = f"""Na základě tohoto transkriptu cizího videa:

---
{row.transcript_md}
---

Vytvoř scénář pro MOJE vlastní video. Format: **{format_hint}**.

Pravidla:
- V mém stylu (Adam Hoffík, realitní makléř RE/MAX Living Česká Lípa)
- Česky, krátké věty, rozhovorový tón
- HOOK musí chytnout v prvních 3 sekundách
- Přidej vlastní úhel pohledu, ne kopii cizího obsahu
- CTA na konci: "Ozvi se mi, přes reality-pittner.cz"
- Návrhy B-roll záběrů (třeba "střih na byt", "text overlay: XYZ")
- Výstup: markdown se sekcemi HOOK, BODY, CTA, B-ROLL
"""
    if my_angle:
        prompt += f"\n\nMůj vlastní úhel: {my_angle}"

    claude = get_claude_client()
    buffer: list[str] = []
    error = None
    async for event in claude.stream(
        messages=[ClaudeMessage(role="user", content=prompt)],
        system_prompt="Jsi copywriter pro social video realitního makléře. Piš česky, stručně, akčně.",
    ):
        if event.type == "token":
            buffer.append(event.data)
        elif event.type == "error":
            error = str(event.data)
            break
        elif event.type == "done":
            break

    if error:
        raise HTTPException(502, detail=f"Claude chyba: {error}")

    row.script_md = "".join(buffer).strip()
    await session.commit()
    return VideoScriptOut.model_validate(row)


@router.delete("/{video_id}", status_code=204)
async def delete_video(
    video_id: str, session: AsyncSession = Depends(get_db)
) -> None:
    row = (
        await session.execute(select(VideoScript).where(VideoScript.id == video_id))
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(404, detail="Video nenalezeno")
    await session.delete(row)
    await session.commit()
