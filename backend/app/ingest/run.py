"""Ingestion CLI — projdi adresář, parseuje soubory, uloží do Chroma jako Notes.

Použití (z /app uvnitř backendu nebo přes docker exec):

  python -m app.ingest.run --source /path/to/REAL\\ ESTATE --category training_pdf
  python -m app.ingest.run --source /path/to/marketing\\ material --category content_marketing --type context

Respektuje kategorizaci z CONTEXT_INVENTORY.md.
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from app.core import memory as mem
from app.db import AsyncSessionLocal, engine, Base
from app.ingest.parsers import chunk_text, parse_file

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


async def ingest_dir(
    source: Path,
    category: str,
    note_type: str = "context",
    sensitivity: str = "internal",
    dry_run: bool = False,
) -> dict[str, int]:
    """Projde adresář rekurzivně, parsne, chunkuje, uloží."""
    stats = {"files": 0, "chunks": 0, "skipped": 0, "errors": 0}

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        ext = path.suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            stats["skipped"] += 1
            continue
        # Preskoč velmi malé soubory (meno než 100 znaků textu)
        try:
            text = parse_file(path)
        except Exception as exc:  # noqa: BLE001
            logger.error("parse failed %s: %s", path, exc)
            stats["errors"] += 1
            continue

        if len(text.strip()) < 100:
            stats["skipped"] += 1
            continue

        stats["files"] += 1
        chunks = chunk_text(text)

        logger.info("ingest %s → %d chunks", path.relative_to(source), len(chunks))

        if dry_run:
            stats["chunks"] += len(chunks)
            continue

        async with AsyncSessionLocal() as db:
            for i, chunk in enumerate(chunks):
                title = f"{path.name} [{i + 1}/{len(chunks)}]"
                try:
                    await mem.save_note(
                        db,
                        type_=note_type,
                        title=title,
                        content=chunk,
                        tags=[category],
                        source=str(path.relative_to(source)),
                        sensitivity=sensitivity,
                        metadata={
                            "ingested_at": datetime.now(timezone.utc).isoformat(),
                            "category": category,
                            "file_name": path.name,
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                        },
                    )
                    stats["chunks"] += 1
                except Exception as exc:  # noqa: BLE001
                    logger.error("save_note failed for %s chunk %d: %s", path, i, exc)
                    stats["errors"] += 1
            await db.commit()

    return stats


async def main() -> int:
    parser = argparse.ArgumentParser(description="RAG ingestion pro Realitní Asistent")
    parser.add_argument("--source", required=True, type=Path, help="Zdrojový adresář")
    parser.add_argument(
        "--category",
        required=True,
        help="Kategorie (tag) — např. training_pdf, legal_templates, sales_scripts",
    )
    parser.add_argument(
        "--type", default="context", help="Note type (default: context)"
    )
    parser.add_argument(
        "--sensitivity",
        default="internal",
        choices=["public", "internal", "client_pii"],
        help="Citlivost záznamu (default: internal)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Jen zobraz, nelayout")
    args = parser.parse_args()

    if not args.source.exists():
        logger.error("Zdroj neexistuje: %s", args.source)
        return 1

    logger.info("Start ingestion: source=%s category=%s type=%s", args.source, args.category, args.type)
    stats = await ingest_dir(
        args.source,
        category=args.category,
        note_type=args.type,
        sensitivity=args.sensitivity,
        dry_run=args.dry_run,
    )
    logger.info(
        "HOTOVO ✓  files=%d  chunks=%d  skipped=%d  errors=%d  (dry_run=%s)",
        stats["files"],
        stats["chunks"],
        stats["skipped"],
        stats["errors"],
        args.dry_run,
    )
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
