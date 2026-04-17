"""Dlouhodobá paměť — ChromaDB + SQLite notes.

Stub verze pro Fázi 1. Reálná implementace (vyhledávání, save, extract entities)
přichází ve Fázi 2.
"""
from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

from app.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache
def get_chroma_client():
    """Vrátí persistent ChromaDB klienta."""
    import chromadb  # lazy import

    settings = get_settings()
    persist_dir = Path(settings.chroma_persist_dir).resolve()
    persist_dir.mkdir(parents=True, exist_ok=True)
    logger.info("ChromaDB persist dir: %s", persist_dir)
    return chromadb.PersistentClient(path=str(persist_dir))


def get_memory_collection():
    """Získá (nebo vytvoří) hlavní kolekci `memory`."""
    client = get_chroma_client()
    return client.get_or_create_collection(
        name="memory",
        metadata={"hnsw:space": "cosine"},
    )
