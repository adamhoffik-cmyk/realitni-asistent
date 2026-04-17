"""Skills API — seznam skillů, tile data, reorder, toggle enabled."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.db_models import Skill as SkillRow
from app.models.schemas import SkillOut, SkillReorderPayload
from app.skills.registry import SkillRegistry

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=list[SkillOut])
async def list_skills(session: AsyncSession = Depends(get_db)) -> list[SkillOut]:
    rows = (
        (
            await session.execute(
                select(SkillRow).order_by(SkillRow.order_index, SkillRow.name)
            )
        )
        .scalars()
        .all()
    )
    result: list[SkillOut] = []
    for row in rows:
        skill = SkillRegistry.get(row.id)
        tile_data = await skill.tile_data() if skill else None
        result.append(
            SkillOut(
                id=row.id,
                name=row.name,
                description=row.description,
                icon=row.icon,
                version=row.version,
                enabled=row.enabled,
                order_index=row.order_index,
                usage_count=row.usage_count,
                last_used_at=row.last_used_at,
                tile_data=tile_data,
            )
        )
    return result


@router.get("/{skill_id}/tile", response_model=dict)
async def skill_tile(skill_id: str) -> dict:
    skill = SkillRegistry.get(skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill nenalezen")
    return await skill.tile_data()


@router.post("/reorder")
async def reorder_skills(
    payload: SkillReorderPayload,
    session: AsyncSession = Depends(get_db),
) -> dict:
    rows = {
        r.id: r
        for r in (await session.execute(select(SkillRow))).scalars().all()
    }
    for idx, skill_id in enumerate(payload.order):
        row = rows.get(skill_id)
        if row is None:
            continue
        row.order_index = idx
        row.updated_at = datetime.now(timezone.utc)
    return {"ok": True}


@router.post("/{skill_id}/toggle")
async def toggle_skill(
    skill_id: str, session: AsyncSession = Depends(get_db)
) -> dict:
    row = (
        await session.execute(select(SkillRow).where(SkillRow.id == skill_id))
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Skill nenalezen")
    row.enabled = not row.enabled
    row.updated_at = datetime.now(timezone.utc)
    return {"id": skill_id, "enabled": row.enabled}
