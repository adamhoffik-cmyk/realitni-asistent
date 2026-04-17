# Realitní Asistent

> Osobní AI aplikace pro realitního makléře RE/MAX Living Česká Lípa.
> Self-hosted na Hetzner VPS, PWA (instalovatelné na mobil/desktop).

**Status:** 🟡 Ve vývoji (Fáze 1 — MVP scaffold)

---

## Co to je

Komplexní osobní asistent, který pomáhá v každodenní práci makléře:

- 🧠 **Dlouhodobá paměť** — sémantické vyhledávání v poznámkách, klientech, nemovitostech, školicích materiálech (ChromaDB)
- 💬 **Chat** — kontextově vědomý, s přístupem ke kalendáři, Driveu, webu, paměti
- 📰 **Ranní briefing** — automaticky v 7:00 (počasí + kalendář + novinky + úkoly)
- ✍️ **Skill: Články** — generování a legalizace článků podle stylebooku
- 🎥 **Skill: Videa** — transkripce cizích videí a generování vlastních scénářů
- 📚 **Plugin: České realitní právo** — nativně přes Claude Code CLI

## Tech stack

**Backend:** Python 3.11 + FastAPI + SQLite + ChromaDB + APScheduler + Claude Agent SDK
**Frontend:** Next.js 14 + TypeScript + Tailwind + PWA (Matrix theme)
**Deploy:** Docker Compose + Caddy (auto HTTPS + BasicAuth) na Hetzner CX23
**AI:** Claude Code CLI přes Claude Max subscription (žádné per-token náklady)

Podrobnosti → [ARCHITECTURE.md](ARCHITECTURE.md) · [SKILLS_ARCHITECTURE.md](SKILLS_ARCHITECTURE.md) · [CONTEXT_INVENTORY.md](CONTEXT_INVENTORY.md)

## Struktura repa

```
realitni-asistent/
├── backend/         # FastAPI app
├── frontend/        # Next.js PWA
├── scripts/         # setup, deploy, diagnostika
├── docs/            # deploy guide, dev guide
├── docker-compose.yml
├── Caddyfile.snippet
└── .env.example
```

## Vývoj lokálně (Windows + Docker Desktop)

```bash
cp .env.example .env
# vyplnit .env (viz komentáře)

docker compose up -d --build
# frontend: http://localhost:3000
# backend API: http://localhost:8000/docs
```

## Deploy na VPS

Viz [docs/DEPLOY.md](docs/DEPLOY.md) (vznikne v pozdější fázi).

## Licence

Soukromý projekt. Všechna práva vyhrazena.
