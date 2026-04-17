"""Scrape all articles from artem-saykin.cz/blog + generate STYLEBOOK.md.

Použití (z backend venv):
    python -m scripts.scrape_saykin --output ./backend/data/reference_articles/artem_saykin/

Nebo v Dockeru (produkce):
    docker exec -it asistent-backend python -m scripts.scrape_saykin \\
        --output /app/data/reference_articles/artem_saykin/

Po sjetí pak spusť:
    docker exec -it asistent-backend python -m app.ingest.run \\
        --source /app/data/reference_articles/artem_saykin \\
        --category content_style --type context
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import httpx
from selectolax.parser import HTMLParser

BASE = "https://artem-saykin.cz"
BLOG_URL = f"{BASE}/blog/"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def slugify(s: str, max_len: int = 80) -> str:
    s = s.lower()
    for pair in [
        ("á", "a"), ("č", "c"), ("ď", "d"), ("é", "e"), ("ě", "e"),
        ("í", "i"), ("ň", "n"), ("ó", "o"), ("ř", "r"), ("š", "s"),
        ("ť", "t"), ("ú", "u"), ("ů", "u"), ("ý", "y"), ("ž", "z"),
    ]:
        s = s.replace(*pair)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:max_len] or "article"


async def fetch_page(client: httpx.AsyncClient, url: str) -> str:
    resp = await client.get(
        url,
        headers={"User-Agent": "Realitni-Asistent-Stylebook-Scraper/1.0"},
        timeout=20.0,
    )
    resp.raise_for_status()
    return resp.text


async def discover_article_urls(client: httpx.AsyncClient) -> list[str]:
    """Projde paginaci blogu a vrátí seznam všech článkových URL."""
    urls: set[str] = set()
    page = 1
    while True:
        page_url = BLOG_URL if page == 1 else f"{BLOG_URL}page/{page}/"
        try:
            html = await fetch_page(client, page_url)
        except httpx.HTTPError as exc:
            logger.info("Stránka %d: end (%s)", page, exc)
            break

        tree = HTMLParser(html)
        # Heuristika: všechny odkazy vedoucí na /blog/<slug>/ jsou články
        found_on_page = set()
        for a in tree.css("a[href]"):
            href = a.attributes.get("href", "")
            if not href:
                continue
            full = urljoin(BASE, href)
            # Pouze odkazy v rámci blogu, které nejsou index/pagination/category
            if (
                full.startswith(f"{BASE}/blog/")
                and full != BLOG_URL
                and "/page/" not in full
                and "/category/" not in full
                and "/tag/" not in full
                and full.rstrip("/") != BLOG_URL.rstrip("/")
            ):
                found_on_page.add(full.rstrip("/") + "/")

        if not found_on_page:
            logger.info("Stránka %d: žádné články, končím", page)
            break

        new_count = len(found_on_page - urls)
        urls.update(found_on_page)
        logger.info("Stránka %d: +%d článků (celkem %d)", page, new_count, len(urls))

        if new_count == 0:
            break
        page += 1
        if page > 30:  # safety
            break

    return sorted(urls)


async def parse_article(client: httpx.AsyncClient, url: str) -> dict | None:
    """Stáhne article, extrahuje title, date, content (přes trafilatura)."""
    import trafilatura

    try:
        html = await fetch_page(client, url)
    except httpx.HTTPError as exc:
        logger.warning("Skip %s: %s", url, exc)
        return None

    # trafilatura pro clean extract
    extracted = trafilatura.extract(
        html,
        include_comments=False,
        include_tables=True,
        output_format="markdown",
        with_metadata=True,
    )
    if not extracted:
        return None

    # Hrubý title z HTML <title> nebo <h1>
    tree = HTMLParser(html)
    title = ""
    t_el = tree.css_first("h1")
    if t_el:
        title = t_el.text().strip()
    elif tree.css_first("title"):
        title = tree.css_first("title").text().strip()

    # Date z meta tagů
    date_str = None
    for selector in [
        'meta[property="article:published_time"]',
        'meta[name="article:published_time"]',
        'meta[name="date"]',
    ]:
        el = tree.css_first(selector)
        if el and el.attributes.get("content"):
            date_str = el.attributes["content"]
            break

    return {
        "url": url,
        "title": title or "(bez titulu)",
        "date": date_str,
        "content_md": extracted,
    }


async def save_article(article: dict, out_dir: Path) -> Path:
    slug = slugify(article["title"])
    url_hash = hashlib.sha1(article["url"].encode()).hexdigest()[:6]
    filename = f"{slug}_{url_hash}.md"
    path = out_dir / filename

    front_matter = (
        "---\n"
        f"url: {article['url']}\n"
        f"title: \"{article['title']}\"\n"
        f"date: {article.get('date') or ''}\n"
        f"scraped_at: {datetime.now(timezone.utc).isoformat()}\n"
        "---\n\n"
    )

    path.write_text(front_matter + article["content_md"], encoding="utf-8")
    return path


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)

    async with httpx.AsyncClient(follow_redirects=True) as client:
        logger.info("Objevuji URL článků z %s", BLOG_URL)
        urls = await discover_article_urls(client)
        logger.info("Nalezeno %d článků", len(urls))

        ok, fail = 0, 0
        for i, url in enumerate(urls, 1):
            logger.info("[%d/%d] %s", i, len(urls), url)
            article = await parse_article(client, url)
            if article is None:
                fail += 1
                continue
            path = await save_article(article, args.output)
            logger.info("  → uloženo %s (%d znaků)", path.name, len(article["content_md"]))
            ok += 1

        logger.info("Hotovo. Úspěch: %d, selhání: %d", ok, fail)
        logger.info("")
        logger.info("Další krok — generuj STYLEBOOK.md:")
        logger.info("  Spusť v UI /skills/articles a požádej v chatu:")
        logger.info("  'Na základě článků v data/reference_articles/artem_saykin/")
        logger.info("   vytvoř STYLEBOOK.md s analýzou stylu.'")
        logger.info("")
        logger.info("Nebo proveď RAG ingest těch článků:")
        logger.info(f"  python -m app.ingest.run --source {args.output} --category content_style --type context")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
