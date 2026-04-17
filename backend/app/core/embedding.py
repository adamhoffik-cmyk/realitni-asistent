"""Embedding model loader — lazy init (model se stáhne při prvním použití)."""
from __future__ import annotations

import logging
from functools import lru_cache

from app.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache
def get_embedder():
    """Vrátí inicializovaný sentence-transformers model.

    První volání stáhne model (~130 MB pro multilingual-e5-small) z HuggingFace.
    Další volání jsou free.
    """
    from sentence_transformers import SentenceTransformer  # lazy import — těžká dep

    settings = get_settings()
    logger.info("Načítám embedding model: %s (%s)", settings.embedding_model, settings.embedding_device)
    model = SentenceTransformer(settings.embedding_model, device=settings.embedding_device)
    return model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Zakóduje seznam textů na embeddingy (list floatů).

    Pro multilingual-e5 modely je doporučené prefixovat:
      - dokumenty: "passage: <text>"
      - dotazy: "query: <text>"

    Zde defaultně použijeme "passage:" prefix. Pro search query volej embed_query().
    """
    model = get_embedder()
    prefixed = [f"passage: {t}" for t in texts]
    vectors = model.encode(prefixed, normalize_embeddings=True, convert_to_numpy=True)
    return vectors.tolist()


def embed_query(query: str) -> list[float]:
    """Embedding pro vyhledávací dotaz (s query: prefix)."""
    model = get_embedder()
    vector = model.encode(f"query: {query}", normalize_embeddings=True, convert_to_numpy=True)
    return vector.tolist()
