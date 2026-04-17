"""Dlouhodobá paměť — ChromaDB + SQLite notes.

Implementace API:
- save_note: uloží poznámku do SQLite a embedding do Chroma
- search: sémantické vyhledávání (top-K), filtrování podle typu/tagu
- delete_note: smaže záznam z obou
- get_note / list_notes: načtení
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.embedding import embed_query, embed_texts
from app.models.db_models import Note

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# ChromaDB client & collection (lazy singleton)
# --------------------------------------------------------------------------- #
@lru_cache
def get_chroma_client():
    import chromadb  # lazy import

    settings = get_settings()
    persist_dir = Path(settings.chroma_persist_dir).resolve()
    persist_dir.mkdir(parents=True, exist_ok=True)
    logger.info("ChromaDB persist dir: %s", persist_dir)
    return chromadb.PersistentClient(path=str(persist_dir))


@lru_cache
def get_memory_collection():
    """Hlavní kolekce 'memory' (všechny záznamy, filtrování přes metadata)."""
    client = get_chroma_client()
    return client.get_or_create_collection(
        name="memory",
        metadata={"hnsw:space": "cosine"},
    )


# --------------------------------------------------------------------------- #
# Save / Update
# --------------------------------------------------------------------------- #
async def save_note(
    session: AsyncSession,
    *,
    note_id: str | None = None,
    type_: str = "note",
    title: str | None = None,
    content: str,
    tags: list[str] | None = None,
    source: str | None = None,
    sensitivity: str = "internal",
    metadata: dict[str, Any] | None = None,
) -> Note:
    """Uloží nebo aktualizuje poznámku.

    Vždy přepíše embedding v Chroma.
    """
    now = datetime.now(timezone.utc)
    is_new = note_id is None

    if is_new:
        note = Note(
            id=str(uuid.uuid4()),
            type=type_,
            title=title,
            content=content,
            tags=tags or [],
            source=source,
            sensitivity=sensitivity,
            meta=metadata or {},
            created_at=now,
            updated_at=now,
        )
        session.add(note)
    else:
        note = (await session.execute(select(Note).where(Note.id == note_id))).scalar_one_or_none()
        if note is None:
            raise ValueError(f"Note {note_id} nenalezen")
        note.type = type_
        note.title = title
        note.content = content
        note.tags = tags or []
        note.source = source
        note.sensitivity = sensitivity
        note.meta = metadata or {}
        note.updated_at = now

    # Embedding — text = title + content (s prefixem type pro lepší disambiguaci)
    embed_text = f"[{type_}] {title or ''}\n{content}".strip()
    embedding = embed_texts([embed_text])[0]

    # ChromaDB upsert
    collection = get_memory_collection()
    chroma_metadata = {
        "note_id": note.id,
        "type": type_,
        "sensitivity": sensitivity,
        "source": source or "",
        "tags": ",".join(tags or []),
        "created_at": now.isoformat(),
    }
    # Chroma ne-nullable metadata (odstraň None)
    chroma_metadata = {k: v for k, v in chroma_metadata.items() if v is not None}

    collection.upsert(
        ids=[note.id],
        embeddings=[embedding],
        metadatas=[chroma_metadata],
        documents=[embed_text],
    )
    note.chroma_id = note.id

    await session.flush()
    logger.info("save_note: %s %s (%s chars)", "create" if is_new else "update", note.id, len(content))
    return note


# --------------------------------------------------------------------------- #
# Delete
# --------------------------------------------------------------------------- #
async def delete_note(session: AsyncSession, note_id: str) -> bool:
    note = (await session.execute(select(Note).where(Note.id == note_id))).scalar_one_or_none()
    if note is None:
        return False
    collection = get_memory_collection()
    try:
        collection.delete(ids=[note.id])
    except Exception as exc:  # noqa: BLE001
        logger.warning("Chroma delete failed for %s: %s", note.id, exc)
    await session.delete(note)
    return True


# --------------------------------------------------------------------------- #
# Get / List
# --------------------------------------------------------------------------- #
async def get_note(session: AsyncSession, note_id: str) -> Note | None:
    return (await session.execute(select(Note).where(Note.id == note_id))).scalar_one_or_none()


async def list_notes(
    session: AsyncSession,
    *,
    types: list[str] | None = None,
    tags: list[str] | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Note]:
    stmt = select(Note).order_by(Note.updated_at.desc()).limit(limit).offset(offset)
    if types:
        stmt = stmt.where(Note.type.in_(types))
    # JSON tag filtr je SQLite-specific — použijeme LIKE na JSON
    # (Alternativa: tagy v samostatné M:N tabulce — pro MVP stačí)
    if tags:
        conditions = [Note.tags.like(f'%"{t}"%') for t in tags]
        stmt = stmt.where(or_(*conditions))
    return list((await session.execute(stmt)).scalars().all())


# --------------------------------------------------------------------------- #
# Semantic search
# --------------------------------------------------------------------------- #
async def search(
    session: AsyncSession,
    *,
    query: str,
    types: list[str] | None = None,
    sensitivity_max: str = "internal",  # public|internal|client_pii
    limit: int = 10,
) -> list[tuple[Note, float]]:
    """Sémantické vyhledávání přes Chroma. Vrátí list (Note, similarity_score)."""
    if not query.strip():
        return []

    query_embedding = embed_query(query)

    # Chroma filtr: type + sensitivity (exclude vyšší než max)
    where: dict[str, Any] = {}
    if types:
        where["type"] = {"$in": types}

    # sensitivity hierarchie: public < internal < client_pii
    # "internal" jako max → filtruj jen public + internal
    allowed = ["public"]
    if sensitivity_max in ("internal", "client_pii"):
        allowed.append("internal")
    if sensitivity_max == "client_pii":
        allowed.append("client_pii")
    where_sens: dict[str, Any] = {"sensitivity": {"$in": allowed}}

    # Merge filters (Chroma $and)
    if where:
        combined = {"$and": [where, where_sens]}
    else:
        combined = where_sens

    collection = get_memory_collection()
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=limit,
        where=combined,
        include=["metadatas", "distances", "documents"],
    )

    ids = result["ids"][0] if result["ids"] else []
    distances = result["distances"][0] if result["distances"] else []

    if not ids:
        return []

    # Načíst Notes v jednom dotazu
    notes = (
        (await session.execute(select(Note).where(Note.id.in_(ids))))
        .scalars()
        .all()
    )
    note_by_id = {n.id: n for n in notes}

    # Sestavit výstup v pořadí od Chroma (nejbližší první)
    # Cosine distance: 0 = identické, 2 = opačné → similarity = 1 - distance/2
    output: list[tuple[Note, float]] = []
    for note_id, distance in zip(ids, distances, strict=False):
        note = note_by_id.get(note_id)
        if note is None:
            continue
        similarity = max(0.0, 1.0 - distance / 2.0)
        output.append((note, similarity))
    return output
