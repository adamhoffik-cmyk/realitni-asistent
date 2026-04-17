# ARCHITECTURE — Realitní Asistent

> Architektonické rozhodnutí a komponentový model osobní AI aplikace.
> Verze: 0.1 (draft ke schválení) | Datum: 2026-04-17

---

## 1. VÝCHOZÍ OMEZENÍ

| Parametr | Hodnota | Dopad |
|----------|---------|-------|
| VPS | Hetzner **CX23** | 2 vCPU / 4 GB RAM / 40 GB disk — skromné |
| Sdílený s | projektem `abot` | pozor na porty, RAM, Docker |
| Síť | 46.225.58.232 + IPv6 | firewall Hetzner (spravuje Hetzner Console) |
| Jeden uživatel | Adam | žádná multi-tenancy, BasicAuth stačí |
| Budget | **0 Kč/měs** za AI | Claude Max přes CLI, SearXNG self-hosted |

Důsledek: kompromisy v AI modelech (menší Whisper, menší embedding model), důsledná kontejnerizace, obligátní swap, nechceme stejný port jako `abot`.

---

## 2. KOMPONENTOVÝ DIAGRAM

```
┌──────────────────────────────────────────────────────────────┐
│                      HETZNER CX23 (Debian/Ubuntu)            │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                CADDY (reverse proxy)                  │   │
│  │  asistent.reality-pittner.cz  →  BasicAuth → frontend │   │
│  │  /api/*  →  backend  |  /searxng  →  SearXNG          │   │
│  │  (sdílí hosta s `abot` — vlastní site block)          │   │
│  └──────────┬──────────────┬────────────────┬───────────┘   │
│             │              │                │                │
│  ┌──────────▼────┐ ┌───────▼────────┐ ┌─────▼─────────┐     │
│  │  FRONTEND      │ │  BACKEND       │ │  SearXNG      │     │
│  │  Next.js 14    │ │  FastAPI 3.11  │ │  (search)     │     │
│  │  PWA           │ │  + Uvicorn     │ │               │     │
│  │  :3000         │ │  :8000         │ │  :8888        │     │
│  └────────────────┘ └───────┬────────┘ └───────────────┘     │
│                             │                                │
│          ┌──────────────────┼────────────────────┐           │
│          │                  │                    │           │
│  ┌───────▼──────┐ ┌─────────▼─────────┐ ┌────────▼──────┐    │
│  │  Claude Code │ │  SQLite           │ │  ChromaDB     │    │
│  │  CLI (host)  │ │  data/app.db      │ │  data/chroma/ │    │
│  │  + plugin    │ │  (turns, notes,   │ │  (embeddings) │    │
│  │  `ceske-…`   │ │   skills, cache)  │ │               │    │
│  └──────────────┘ └───────────────────┘ └───────────────┘    │
│                             │                                │
│  ┌──────────────────────────▼──────────────────────────┐     │
│  │  APScheduler jobs (in backend process)              │     │
│  │   • 07:00 ranní briefing                            │     │
│  │   • každé 2 h scraping novinek                      │     │
│  │   • každých 15 min sync Google Calendar             │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                              │
│  Host-level files: data/ (volume mount — SQLite, Chroma,     │
│  články, transkripty, reference articles, scrapery output)   │
└──────────────────────────────────────────────────────────────┘

        │                                          │
        │ HTTPS (Let's Encrypt)                    │ OAuth2
        ▼                                          ▼
   Uživatel (mobil/desktop PWA)         Google APIs (Calendar/Drive)
                                         + lokální Claude Max login
```

**Claude Code CLI běží na hostovi** (ne v kontejneru) — to je záměrné:
- Už tam může být nainstalovaný (pokud ho používáš pro projekt `abot`).
- Potřebuje persistent login do Claude Max (token v `~/.claude/`).
- Pluginy (`ceske-realitni-pravo`) jsou vázané na home složku uživatele.
- Backend container na něj sahá přes mount `~/.claude/` + volání `claude` binárky přes `claude-agent-sdk`.

---

## 3. TECH STACK (finální)

### Backend (Docker image `asistent-backend`)
- **Python 3.11-slim**
- **FastAPI 0.115+** / **Uvicorn** (async)
- **claude-agent-sdk** (oficiální Python SDK od Anthropicu) — volá `claude` CLI na hostovi
- **SQLAlchemy 2.x** + **Alembic** (migrace)
- **SQLite** (file) — WAL mode, single-writer OK pro jeden uživatel
- **ChromaDB 0.5+** (in-process, persistent client)
- **sentence-transformers** s modelem `intfloat/multilingual-e5-small` (~130 MB, rozumná kvalita pro CZ, vejde se do RAM)
- **APScheduler 3.x** (jobstore v SQLite, takže přežije restart)
- **httpx** + **selectolax** / **trafilatura** (web scraping)
- **feedparser** (RSS)
- **faster-whisper** s modelem **small** (~244 MB) nebo **medium** (~769 MB) — volitelné přes env var, default `small`
- **ffmpeg-python** + **yt-dlp**
- **cryptography** (šifrování klientských polí)

### Frontend (Docker image `asistent-frontend`)
- **Next.js 14** (App Router) + **TypeScript 5**
- **Tailwind CSS 3.4**
- **shadcn/ui** (minimální komponenty) — ne MUI, ne Chakra, ne Ant. Přizpůsobitelné na Matrix theme.
- **zustand** (state management — lehký)
- **next-pwa** nebo vlastní service worker (PWA)
- **WebSocket** klient přes `useEffect` — bez Socket.IO (nativní `ws` stačí)
- **Font:** JetBrains Mono (self-hosted, ne CDN — GDPR)
- Canvas animace pro Digital Rain — samostatná komponenta s `requestAnimationFrame`, opacita max 0.15

### Infrastruktura
- **Docker Compose v2**
- **Caddy 2** jako reverse proxy + auto HTTPS
- **SearXNG** (samostatný kontejner — oficiální image `searxng/searxng`)

### Síť a porty (na hostovi)
| Služba | Port (host) | Port (container) | Veřejný |
|--------|-------------|------------------|---------|
| Caddy | 80, 443 | 80, 443 | ANO (možná sdílený s `abot`) |
| Backend | (jen internal) | 8000 | NE |
| Frontend | (jen internal) | 3000 | NE |
| SearXNG | (jen internal) | 8080 | NE |

Všechny kontejnery v jedné Docker síti `asistent-net`. Caddy ven, ostatní jen dovnitř.

---

## 4. SDÍLENÍ VPS S PROJEKTEM `ABOT`

**Tři možnosti, vyber si:**

### Varianta A — sdílený Caddy (**doporučeno**)
- Jeden systémový Caddy na hostovi obsluhuje oba projekty.
- Realitní Asistent přidá site block `asistent.reality-pittner.cz { … }` do společného Caddyfile.
- Úspora RAM (~30 MB), jeden cert manager.
- Pokud `abot` má vlastní Caddy v Composu → **přesunout ho na host-level Caddy** (jednorázová migrace).

### Varianta B — oba Caddy, Realitní na alt portu
- `abot` drží 80/443, my na 8081/8443, ale subdoména musí ven přes něco.
- Ne. Komplikace.

### Varianta C — izolace v Docker síti, `abot` Caddy reverse-proxuje na nás
- Realitní Asistent neexportuje port 80/443, jen `asistent-frontend:3000`.
- `abot` Caddy má direktivu `reverse_proxy asistent-frontend:3000`.
- Vyžaduje sdílenou Docker síť.

**Rozhodnutí odložím** na pohled do stavu VPS (viz sekce 10 — diagnostika). Výchozí = Varianta A.

---

## 5. DATOVÝ MODEL (SQLite)

Hlavní tabulky:

```sql
-- User settings (single row)
settings (key TEXT PK, value JSON)

-- Skill registry
skills (
  id TEXT PK, name TEXT, description TEXT, icon TEXT,
  enabled BOOLEAN, order_index INT, usage_count INT,
  config JSON, created_at, updated_at
)

-- Chat history (short-term)
conversation_sessions (id UUID PK, context TEXT, started_at, last_activity_at)
conversation_turns (
  id UUID PK, session_id FK, role TEXT, content TEXT,
  tokens INT, skill_id TEXT NULL, tool_calls JSON, created_at
)

-- Long-term memory (meta, vectors jsou v Chroma)
notes (
  id UUID PK, type TEXT,        -- note|fact|context|article|transcript|person|property
  title TEXT, content TEXT, metadata JSON, tags JSON,
  source TEXT, sensitivity TEXT,  -- public|internal|client_pii
  chroma_id TEXT UNIQUE,          -- pointer do ChromaDB
  created_at, updated_at
)

-- Calendar cache
calendar_events (
  id TEXT PK, google_event_id TEXT, summary TEXT, start_ts, end_ts,
  description TEXT, attendees JSON, synced_at
)

-- News aggregator
news_items (
  id UUID PK, url TEXT UNIQUE, source TEXT, title TEXT,
  summary TEXT, content TEXT, published_at, fetched_at,
  relevance_score REAL, tags JSON
)

-- Daily briefings (history)
briefings (id UUID PK, date DATE UNIQUE, content MARKDOWN, generated_at)

-- Articles (Skill 1)
articles (
  id UUID PK, slug TEXT, title TEXT, status TEXT,  -- draft|published
  mode TEXT,  -- A_new|B_legalized
  content_md TEXT, meta_description TEXT, keywords JSON,
  source_url TEXT NULL, stylebook_version TEXT,
  exported_to_drive_url TEXT, created_at, updated_at
)

-- Video scripts (Skill 2)
video_scripts (
  id UUID PK, source_url TEXT, transcript_md TEXT, script_md TEXT,
  duration_sec INT, created_at
)

-- OAuth tokens (šifrované!)
oauth_tokens (
  service TEXT PK,  -- google_calendar|google_drive
  access_token_enc BLOB, refresh_token_enc BLOB,
  expires_at, scope TEXT
)

-- APScheduler jobstore
apscheduler_jobs (id, next_run_time, job_state BLOB)
```

**ChromaDB kolekce:** `memory` (všechny `notes` embedded — one collection, filtrování přes metadata `type` a `sensitivity`).

---

## 6. BEZPEČNOSTNÍ MODEL

| Vrstva | Ochrana |
|--------|---------|
| Transport | HTTPS (Caddy + Let's Encrypt) |
| Autentizace | Caddy BasicAuth (jeden uživatel, bcrypt hash v `.env`) |
| OAuth tokeny | AES-256-GCM v SQLite (klíč v `.env`, nikdy v git) |
| Client PII | Application-level šifrování polí v `notes` se `sensitivity=client_pii` — telefon, e-mail, rodné číslo |
| Rodná čísla | Nikdy necitovat v AI odpovědích (system prompt guard + post-process regex filtr) |
| Právní obsah | Auto-disclaimer "Toto není právní rada…" u všech AI-generovaných právních textů |
| Sekrety | `.env` s `chmod 600`, `.env.example` v gitu bez hodnot |
| Logging | AI prompty/responses v SQLite **bez** PII — scrub before insert |
| Backup | (zatím neřešíme per tvé rozhodnutí) |

---

## 7. STREAMING AI ODPOVĚDÍ

Claude Agent SDK podporuje streaming. Tok:

```
Frontend ──WS──► Backend ──claude-agent-sdk stream──► Claude Code CLI
                                                      │
Frontend ◄──WS text chunks── Backend ◄───SDK events───┘
```

WebSocket endpoint `/ws/chat` akceptuje JSON `{ message, context, session_id }` a posílá události:
- `token` — jeden chunk textu (typewriter na frontendu)
- `tool_call` — AI použilo nástroj (UI: "🔍 Hledám v paměti…")
- `tool_result` — výsledek nástroje
- `done` — konec odpovědi + final metadata (tokens, latency)
- `error`

---

## 8. PAMĚŤOVÝ ROZPOČET (RAM)

Odhad běžného provozu (4 GB k dispozici):

| Proces | RAM |
|--------|-----|
| Debian/Ubuntu base | ~250 MB |
| Docker daemon | ~100 MB |
| `abot` projekt (odhad, doplní uživatel) | ~500 MB |
| Caddy | ~30 MB |
| Frontend (Next.js prod) | ~150 MB |
| Backend (FastAPI + chroma + embedding model loaded) | ~700 MB |
| SearXNG | ~150 MB |
| **Subtotal always-on** | **~1.9 GB** |
| Whisper small (lazy-load při transkripci) | ~400 MB peak |
| ChromaDB čtení/zápis peak | ~200 MB |
| **Peak při transkripci videa** | **~2.5 GB** |
| **Rezerva** | **~1.5 GB** |

➜ **Doporučený swap: 4 GB** (na 40 GB disku bezpečné). Bez swapu se to může škytnout při peaku.

---

## 9. ADRESÁŘOVÁ STRUKTURA (upřesněná)

Zůstává podle specifikace s drobnými úpravami:

```
realitni-asistent/
├── docker-compose.yml
├── Caddyfile.snippet        # pro vložení do host Caddyfile (Var. A)
├── .env.example
├── .env.local.example       # pro vývoj na Windows
├── README.md
├── ARCHITECTURE.md ✓
├── CONTEXT_INVENTORY.md ✓
├── SKILLS_ARCHITECTURE.md (připravuji)
├── STYLEBOOK.md (generováno později)
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/versions/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py              # pydantic-settings
│   │   ├── deps.py                # DI
│   │   ├── db.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py            # WebSocket + REST
│   │   │   ├── memory.py
│   │   │   ├── notes.py
│   │   │   ├── calendar.py
│   │   │   ├── news.py
│   │   │   ├── briefings.py
│   │   │   ├── skills.py
│   │   │   ├── articles.py        # Skill 1
│   │   │   ├── videos.py          # Skill 2
│   │   │   └── settings.py
│   │   ├── core/
│   │   │   ├── claude_client.py   # wrapper kolem claude-agent-sdk
│   │   │   ├── memory.py          # ChromaDB + SQLite notes
│   │   │   ├── embedding.py       # sentence-transformers loader
│   │   │   ├── context_builder.py # sestavení system promptu + RAG kontextu
│   │   │   └── tools.py           # definice nástrojů pro SDK
│   │   ├── skills/
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # BaseSkill
│   │   │   ├── registry.py
│   │   │   ├── articles.py
│   │   │   └── video_transcript.py
│   │   ├── integrations/
│   │   │   ├── google_calendar.py
│   │   │   ├── google_drive.py
│   │   │   ├── search_web.py
│   │   │   └── weather.py         # Open-Meteo
│   │   ├── scheduler/
│   │   │   ├── jobs.py
│   │   │   └── startup.py
│   │   ├── scrapers/
│   │   │   ├── base.py
│   │   │   └── news_sources.py
│   │   ├── ingest/                # NEW — pro RAG ingestion školicích materiálů
│   │   │   ├── pdf_parser.py
│   │   │   ├── docx_parser.py
│   │   │   └── run.py             # CLI: python -m app.ingest.run
│   │   ├── security/
│   │   │   ├── encryption.py
│   │   │   └── pii_filter.py
│   │   └── models/
│   │       ├── db_models.py
│   │       └── schemas.py
│   └── data/ (mount)              # viz ukázka výše
├── frontend/
│   └── … (dle spec)
├── scripts/
│   ├── setup-vps.sh               # instalace Docker, Caddy, host-level deps
│   ├── deploy.sh                  # pull + compose up
│   ├── diagnose-vps.sh            # diagnostický výpis stavu VPS
│   ├── gen-basic-auth.sh          # generátor hesla
│   └── scrape_reference.py        # artem-saykin.cz (Skill 1 bootstrap)
└── docs/
    ├── DEPLOY.md
    └── DEVELOPMENT.md             # jak vyvíjet lokálně na Windows
```

---

## 10. VÝVOJ & DEPLOY WORKFLOW

**Protože nemám SSH přístup k tvému VPS, postup bude:**

1. **Lokální vývoj (Windows + Docker Desktop)** — kompletní stack běží u tebe na PC během vývoje. Já se soustředím na kód, ty můžeš otevírat `http://localhost:3000` a zkoušet.
2. **GitHub repo** `adamhoffik-cmyk/realitni-asistent` (privátní) — postupně commitujeme.
3. **Až bude stack připravený**, dám ti **přesné copy-paste kroky pro deploy na CX23** (SSH z tvého PC). Včetně:
   - diagnóza existujícího stavu VPS
   - instalace Claude Code CLI + login do Claude Max
   - instalace pluginu `ceske-realitni-pravo`
   - rozhodnutí o variantě A/B/C pro Caddy
   - `git pull && docker compose up -d`

---

## 11. ODŮVODNĚNÍ KLÍČOVÝCH ROZHODNUTÍ

| Rozhodnutí | Zdůvodnění |
|------------|-----------|
| FastAPI + Next.js (ne full-stack Next.js) | Backend je těžký na AI/scraping/schedule, frontend je lehký. Oddělené kontejnery = snadná škálovatelnost, jednodušší mental model. |
| SQLite místo Postgresu | Jeden uživatel, žádná concurrent write, úspora RAM (~200 MB). WAL mode je v klidu rychlý. |
| ChromaDB in-process (ne samostatný kontejner) | Úspora RAM (~150 MB), jednodušší deploy. Pro tvůj rozsah (~tisíce záznamů) stačí. |
| `multilingual-e5-small` (ne large) | 130 MB místo 2 GB. Rozdíl v kvalitě pro naše úlohy malý. |
| Whisper `small` default | 244 MB místo 2.9 GB (large-v3). Pro česká videa cca 90 % kvality. Možnost přepnout přes env. |
| SearXNG (ne Brave API) | Žádné klíče, žádné limity, žádné náklady. RAM 150 MB. Plně customizovatelný. |
| Claude Code CLI na hostovi (ne v kontejneru) | Persistent Claude Max login, pluginy v `~/.claude/`. Kontejner by login ztratil při restartu. |
| Reusovat Google OAuth z pluginu `ceske-realitni-pravo` | Ušetří ~200 řádků kódu + vlastní OAuth redirect URL. Plugin už má funkční flow. |
| Caddy (ne nginx + certbot) | Auto-TLS, čitelný config, jeden binár. |
| Zustand (ne Redux) | Triviální API, minimální boilerplate pro single-user app. |
| `shadcn/ui` (ne MUI) | Kopírované komponenty = plná kontrola nad Matrix theme, žádný bundle bloat. |

---

## 11b. NEWS ZDROJE (ověřené 2026-04-17)

**Tier 1 — ověřené RSS, citovat přímo:**
| Zdroj | Feed | Poll |
|-------|------|------|
| Hypoindex.cz | `https://www.hypoindex.cz/feed/` | 1 h |
| ČNB tiskové zprávy | `https://www.cnb.cz/cs/.content/rss-feed/rss-feed_tz.rss` | 1 h |
| ČnBlog (ČNB) | `https://www.cnb.cz/cs/.content/rss-feed/rss-feed_00023.rss` | 4 h |
| HN — Reality | `https://byznys.hn.cz/?p=02R000_rss` | 1 h |
| ESTAV.cz | `https://www.estav.cz/rss.xml` | 1 h |
| TZB-info | `https://www.tzb-info.cz/rss/index.xml` + `/rss/clanky-stavba.xml` + `/rss/clanky-2.xml` | 2 h |
| Českolipský deník — region | `https://ceskolipsky.denik.cz/rss/z_regionu.html` | 2 h |
| Novinky.cz (general + filtr klíčových slov) | `https://www.novinky.cz/rss` | 2 h |

**Tier 2 — RSS existuje, verifikovat před citací:**
- iDNES Reality (`servis.idnes.cz/rss.asp?c=reality`)
- E15 (generální feed + filtr)
- epravo.cz (kategorie nemovitosti)
- Finanční správa (daňové novinky)

**Tier 3 — HTML scraper (bez RSS, poll 24 h):**
- ČKA (`cka.cz/svet-architektury/aktualne/novinky`) — stavební zákon, novely
- ČKAIT (`ckait.cz`) — technická legislativa
- Město Česká Lípa (`mucl.cz/tiskove-zpravy/ds-2581`) — územní plán, výstavba
- i-noviny.cz — lokální Českolipsko
- Golem Finance (blog) — hypotéky

**Blacklist (nescrapovat):** realit-info.cz, bydleni-tip.cz, usetreno.cz, e-news.cz, sreality.cz "blog" (= inzertní feed), Facebook/LinkedIn posty makléřů jako primární zdroj.

**Filter klíčových slov pro generické feedy** (Novinky, E15): `hypotéka`, `nemovitost`, `reality`, `bydlení`, `stavební zákon`, `ČNB sazby`, `realitní trh`.

Normalizace: `feedparser` → UTC timestamps, dedup přes `guid`+`url_hash`, uložení do `news_items` (SQLite).

---

## 12. CO ZATÍM NEŘEŠÍM (vědomé odložení)

- **Zálohy** — dle tvého rozhodnutí zatím ne. Když později, navrhnu cron na daily dump `app.db` + `chroma/` do `Realitní asistent/Zálohy` na Drive.
- **Observability** — žádný Grafana/Prometheus. Jen strukturované logy v Docker + rotating file logs.
- **Multi-device sync** — PWA + jeden server = jeden zdroj pravdy. Offline mode není MVP.
- **Rate limiting** — jeden uživatel, netřeba.
- **CI/CD pipeline** — zatím ne. Deploy manuálním `git pull && compose up`.

---

## 13. OTÁZKY OTEVŘENÉ PŘED IMPLEMENTACÍ

Po schválení této architektury potřebuju od tebe ještě:

1. **Diagnostika VPS** — spustit skript (připravím ti ho, řádek copy-paste do SSH) a vrátit mi výstup. Tím zjistím: OS, existující porty, Docker, RAM `abot`, existuje-li už Caddy.
2. **GitHub repo** — mám ti ho pomoct vytvořit (`gh repo create`)? Nebo to uděláš sám (název = `realitni-asistent`, private)?
3. **Lokální dev na Windows** — máš Docker Desktop nainstalovaný? Pokud ne, pomohu ho nastavit.

---

## ZÁVĚR

Tato architektura je:
- **Realistická pro CX23** (4 GB RAM s rezervou)
- **Rozšiřitelná** (plugin systém skillů, nové integrace jako moduly)
- **Bez cloud nákladů** (Claude Max + self-host)
- **Bezpečná pro klientská data** (šifrování, PII filter)
- **Přizpůsobená sdílení VPS** (3 varianty podle stavu abot)

Počkám na tvé připomínky, pak začnu psát `SKILLS_ARCHITECTURE.md` a Fázi 1.
