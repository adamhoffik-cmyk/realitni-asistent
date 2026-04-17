# Fáze 2 — Status a další kroky

## ✅ Hotové

### 2-B · Paměť API + ChromaDB RAG

**Backend:**
- `app/core/memory.py` — skutečná implementace `save_note`, `search`, `delete_note`, `list_notes`, `get_note`
- `app/api/notes.py` — REST endpointy:
  - `POST /api/notes` — vytvoří poznámku (automaticky embedding → Chroma)
  - `GET /api/notes?types=note&tags=foo&limit=50` — list s filtry
  - `GET /api/notes/{id}` — detail
  - `PATCH /api/notes/{id}` — update (přepíše embedding)
  - `DELETE /api/notes/{id}`
  - `POST /api/notes/search` — sémantické hledání (query + filtery, vrátí score 0–1)
- Sensitivity level filtering (public / internal / client_pii)
- Multilingual-e5-small embedding model (~130 MB, CZ OK)

**Frontend:**
- `/memory` stránka — seznam poznámek, filter podle typu, sémantické hledání, smazat
- `QuickNote` widget na home teď volá reálné API (bylo stub)

### 2-C · Chat engine (Claude Agent SDK wrapper)

**Backend:**
- `app/core/claude_client.py` — `ClaudeClient.stream()` s plnou integrací `claude-agent-sdk` Python package:
  - Streaming tokenů přes `include_partial_messages=True`
  - Detekce `StreamEvent` / `AssistantMessage` / `ResultMessage`
  - Tool calls se propouštějí do UI
  - System prompt přijímá + history messages přetaví do context
- `app/core/context_builder.py` — sestaví:
  - Base system prompt (role: AI asistent Adama Hoffíka, disclaimery u právních témat)
  - Skill-specific context modifier (pokud na skill stránce)
  - Top-K RAG hits z Chroma (relevance ≥ 0.3)
- `app/api/chat.py` — WebSocket streaming plně propojený s Claude SDK a paměťí

### 2-D · RAG ingestion skript

- `app/ingest/parsers.py` — PDF (pdfplumber), DOCX (python-docx), TXT/MD
- `app/ingest/run.py` — CLI: `python -m app.ingest.run --source <dir> --category <tag>`
- Chunking s overlapem (800 znaků, 100 overlap, respektuje odstavce)

**Ingest tvých materiálů (až budeš chtít):**
```bash
# Na VPS, uvnitř backend containeru:
docker exec -it asistent-backend python -m app.ingest.run \
    --source /app/data/reference_articles/REAL_ESTATE \
    --category training_pdf \
    --type context
```
(Nejdřív ale kopíruj REAL ESTATE/ a marketing material 2026/ na VPS do `/opt/realitni-asistent/backend/data/reference_articles/`.)

---

## ⏳ Čeká na rozhodnutí

### Reálný chat vs stub

**Problém:** Backend běží v Dockeru. Claude CLI je jen na hostu (`/usr/bin/claude`). Backend kontejner ho neumí volat.

**Volby:**

**A) Nainstalovat Claude CLI do backend Dockerfile** *(~10 min práce)*
- Do `backend/Dockerfile` přidáme Node.js 22 + `npm install -g @anthropic-ai/claude-code`
- Mount `~/.claude/` z hostu → backend kontejner má přístup k loginu + pluginům
- +: minimální změna architektury
- –: backend image vzroste o ~300 MB (Node.js + CLI)
- –: Claude CLI se musí instalovat ve 2 místech (host + container)

**B) Přesunout backend z Dockeru na host** *(~30 min refactor)*
- Backend poběží jako systemd service (`/etc/systemd/system/asistent-backend.service`)
- Frontend + Caddy + SearXNG zůstanou v Dockeru
- Caddy reverse-proxuje z kontejneru na host (`host.docker.internal:8000`)
- +: Claude CLI + plugins nativně dostupné, bez mount
- +: snadnější debug (logs v journalctl)
- +: backend image úplně odpadne
- –: dva deployment patterny (Docker + systemd)

**C) Claude API místo Claude Max CLI** *(nejjednodušší, ale platí)*
- Použít `anthropic` Python SDK s API klíčem
- Per-token platby (~$3/$15 na 1M tokens Sonnet)
- Odpadá celý SDK CLI trouble
- –: platíš dvakrát (Claude Max + API)

**Moje doporučení:** A pro teď (rychlé), B dlouhodobě (čistší). C nedoporučuju kvůli dvojímu placení.

### 2-A Google OAuth

Plugin `legal` (ceske-realitni-pravo) má MCP servery pro Gmail/Calendar/Drive/DocuSign přes `gmail.mcp.claude.com` atd. Ty používají OAuth přes Anthropic proxy. Ale to znamená, že **Claude CLI** musí být schopný volat ty MCP servery — tzn. zase potřebujeme funkční chat (viz výše).

Alternativa: vlastní OAuth flow v našem backendu přes `google-auth-oauthlib`.

---

## Deploy update pro Fázi 2 (na VPS)

Po `git pull` potřebuješ:

1. **Rebuild backend image** (kvůli novým importům + ingest modulu):
```bash
cd /opt/realitni-asistent
git pull
docker compose --profile production up -d --build backend frontend
```

2. **Otestovat paměť:**
```bash
# Ze svého PC přes curl:
curl -u adam:HESLO -X POST https://asistent.46-225-58-232.nip.io/api/notes \
  -H "Content-Type: application/json" \
  -d '{"content":"Klient pan Novák chce byt 2+kk v České Lípě do 3 M","type":"note","tags":["klient","poptavka"]}'

# Nebo rovnou v UI: https://asistent.46-225-58-232.nip.io → Rychlá poznámka → Uložit
```

3. **Otestovat search** → jdi na `/memory` v UI, napiš do search "byt novák" → měla by přijít tvoje poznámka s relevance score.

4. **Chat** zatím vrátí error *"Claude Code CLI není dostupný"* — dokud nerozhodneš A/B/C.
