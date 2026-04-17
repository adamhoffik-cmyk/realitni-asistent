"""Konfigurace news zdrojů — Tier 1/2/3 podle ARCHITECTURE.md §11b.

Každý zdroj má:
- name: lidský název
- url: RSS feed URL (pro HTML scraper to je URL stránky s artikly)
- type: "rss" nebo "html"
- category: tier1 | tier2 | tier3
- keywords: filter klíčových slov pro generické feedy (novinky.cz, e15)
            None = nefiltruj, vzít vše
- poll_minutes: jak často fetchovat
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class NewsSource:
    name: str
    url: str
    type: str = "rss"  # rss | html
    tier: str = "tier1"
    keywords: list[str] | None = None
    poll_minutes: int = 60


# Klíčová slova pro generické feedy (novinky.cz obecné, E15 obecné)
REAL_ESTATE_KEYWORDS = [
    "hypotéka",
    "hypotéky",
    "sazby",
    "nemovitost",
    "nemovitosti",
    "reality",
    "realit",
    "bydlení",
    "bydlete",
    "stavební zákon",
    "ČNB",
    "realitní",
    "pronájem",
    "nájem",
    "kupní cena",
    "katastr",
    "developer",
    "byt",
    "dům",
    "chata",
    "chalupa",
    "pozemek",
]


SOURCES: list[NewsSource] = [
    # === TIER 1: ověřené RSS, citovat přímo ===
    NewsSource(
        name="Hypoindex",
        url="https://www.hypoindex.cz/feed/",
        tier="tier1",
        poll_minutes=60,
    ),
    NewsSource(
        name="ČNB — tiskové zprávy",
        url="https://www.cnb.cz/cs/.content/rss-feed/rss-feed_tz.rss",
        tier="tier1",
        poll_minutes=60,
    ),
    NewsSource(
        name="čnBlog",
        url="https://www.cnb.cz/cs/.content/rss-feed/rss-feed_00023.rss",
        tier="tier1",
        poll_minutes=240,
    ),
    NewsSource(
        name="HN — Reality",
        url="https://byznys.hn.cz/?p=02R000_rss",
        tier="tier1",
        poll_minutes=60,
    ),
    NewsSource(
        name="ESTAV.cz",
        url="https://www.estav.cz/rss.xml",
        tier="tier1",
        poll_minutes=60,
    ),
    NewsSource(
        name="TZB-info",
        url="https://www.tzb-info.cz/rss/index.xml",
        tier="tier1",
        poll_minutes=120,
    ),
    NewsSource(
        name="TZB-info — stavba",
        url="https://www.tzb-info.cz/rss/clanky-stavba.xml",
        tier="tier1",
        poll_minutes=120,
    ),
    NewsSource(
        name="Českolipský deník — region",
        url="https://ceskolipsky.denik.cz/rss/z_regionu.html",
        tier="tier1",
        poll_minutes=120,
    ),
    NewsSource(
        name="Novinky.cz (filtr real estate)",
        url="https://www.novinky.cz/rss",
        tier="tier1",
        poll_minutes=120,
        keywords=REAL_ESTATE_KEYWORDS,
    ),
    # === TIER 2: RSS existuje, verifikovat před citací ===
    # (zatím zakomentováno, zapneme když ověříme obsahy)
    # NewsSource(name="iDNES Reality", url="https://servis.idnes.cz/rss.asp?c=reality", tier="tier2"),
    # NewsSource(name="epravo.cz — nemovitosti", url="https://www.epravo.cz/rss/kategorie-nemovitosti/", tier="tier2"),
    # === TIER 3: HTML scraper (bez RSS) ===
    # (později — vyžaduje HTML parsing + dedup)
    # NewsSource(name="ČKA novinky", url="https://www.cka.cz/svet-architektury/aktualne/novinky", type="html", tier="tier3", poll_minutes=1440),
    # NewsSource(name="Město Česká Lípa", url="https://www.mucl.cz/tiskove-zpravy/ds-2581", type="html", tier="tier3", poll_minutes=1440),
]
