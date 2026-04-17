"""Notes API — poznámky a dlouhodobá paměť (CRUD + sémantické hledání)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import memory as mem
from app.db import get_db
from app.models.schemas import (
    MemorySearchHit,
    MemorySearchQuery,
    NoteIn,
    NoteOut,
)

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteOut)
async def create_note(
    payload: NoteIn, session: AsyncSession = Depends(get_db)
) -> NoteOut:
    note = await mem.save_note(
        session,
        type_=payload.type,
        title=payload.title,
        content=payload.content,
        tags=payload.tags,
        source=payload.source,
        sensitivity=payload.sensitivity,
        metadata=payload.metadata,
    )
    return NoteOut.model_validate(note)


@router.get("", response_model=list[NoteOut])
async def list_notes(
    types: list[str] | None = Query(None),
    tags: list[str] | None = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db),
) -> list[NoteOut]:
    notes = await mem.list_notes(
        session, types=types, tags=tags, limit=limit, offset=offset
    )
    return [NoteOut.model_validate(n) for n in notes]


@router.get("/{note_id}", response_model=NoteOut)
async def get_note(
    note_id: str, session: AsyncSession = Depends(get_db)
) -> NoteOut:
    note = await mem.get_note(session, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Poznámka nenalezena")
    return NoteOut.model_validate(note)


@router.patch("/{note_id}", response_model=NoteOut)
async def update_note(
    note_id: str,
    payload: NoteIn,
    session: AsyncSession = Depends(get_db),
) -> NoteOut:
    note = await mem.save_note(
        session,
        note_id=note_id,
        type_=payload.type,
        title=payload.title,
        content=payload.content,
        tags=payload.tags,
        source=payload.source,
        sensitivity=payload.sensitivity,
        metadata=payload.metadata,
    )
    return NoteOut.model_validate(note)


@router.delete("/{note_id}", status_code=204)
async def delete_note(
    note_id: str, session: AsyncSession = Depends(get_db)
) -> None:
    ok = await mem.delete_note(session, note_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Poznámka nenalezena")


@router.post("/search", response_model=list[MemorySearchHit])
async def search_notes(
    payload: MemorySearchQuery,
    session: AsyncSession = Depends(get_db),
) -> list[MemorySearchHit]:
    hits = await mem.search(
        session,
        query=payload.query,
        types=payload.types,
        limit=payload.limit,
    )
    return [
        MemorySearchHit(note=NoteOut.model_validate(n), score=score)
        for n, score in hits
    ]
