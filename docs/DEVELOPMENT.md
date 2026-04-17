# DEVELOPMENT — lokální vývoj na Windows

## Předpoklady

- Windows 10/11 + Docker Desktop (s WSL 2 backendem)
- Git for Windows
- Node 20+ a Python 3.11+ **volitelně** (pokud chceš vyvíjet bez kontejnerů)

## Rychlý start

```powershell
# 1. Klonuj repo
git clone https://github.com/adamhoffik-cmyk/realitni-asistent.git
cd realitni-asistent

# 2. Připrav .env
cp .env.example .env
# Otevři .env a uprav aspoň:
#   BACKEND_SECRET_KEY  (libovolný náhodný string min. 32 znaků)
#   PII_ENCRYPTION_KEY  (vygeneruj — viz níže)

# 3. Vygeneruj PII klíč
python -c "import secrets,base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"
# zkopíruj výstup do PII_ENCRYPTION_KEY v .env

# 4. Start stacku (bez Caddy a SearXNG — na lokálu nejsou potřeba)
docker compose up -d --build

# 5. Otevři v prohlížeči
#    Frontend: http://localhost:3000
#    API docs: http://localhost:8000/api/docs
```

## První spuštění — co se stane

1. **Backend build** (~5-8 min poprvé): stáhne Python 3.11, nainstaluje FastAPI,
   ChromaDB, sentence-transformers, faster-whisper atd.
2. **Frontend build** (~2-3 min): npm install, Next.js build do standalone.
3. **Start:**
   - Backend naběhne na `localhost:8000`, inicializuje SQLite, bootstrap skillů.
   - Frontend naběhne na `localhost:3000`.
4. **První otevření**: embedding model se stáhne z HuggingFace (~130 MB).

## Typické operace

```powershell
# Logy backend
docker compose logs -f backend

# Restart po změně kódu (host mount NENÍ aktivní — rebuild nutný)
docker compose up -d --build backend
docker compose up -d --build frontend

# Zastavit
docker compose down

# Vyčistit všechno včetně volumes (⚠ smaže SQLite i Chroma)
docker compose down -v
```

## Vývoj bez Dockeru (rychlejší iterace)

**Backend:**
```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
python -m uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```powershell
cd frontend
npm install
npm run dev
```

## Známé problémy

### Claude wrapper je STUB
Ve Fázi 1 `claude_client.py` jen echuje zprávu. Reálné volání `claude-agent-sdk`
se zapojí ve Fázi 1I (po deploy na VPS s Claude Max loginem) nebo pro lokál
po `claude login` na Windows.

### CLI `claude` na Windows lokále
Pokud si chceš lokálně volat reálného Clauda, nainstaluj Claude Code CLI pro
Windows a přihlaš se do Claude Max. Pak v `.env` nastav:
```
CLAUDE_CLI_PATH=C:/Users/USER/AppData/Local/Programs/claude-cli/claude.exe
```

### Embedding model poprvé dlouho stahuje
První request na `/api/notes` spustí lazy-load modelu z HuggingFace.
Následné requesty jsou rychlé (cached).

### CRLF warnings při git commit
Git na Windows normalizuje LF → CRLF. `.gitattributes` to řídí — v budoucnu
přidám jednotný `text=auto eol=lf` pro všechny soubory.

## Struktura repozitáře

Viz [ARCHITECTURE.md §9](../ARCHITECTURE.md#9-adresářová-struktura-upřesněná).

## Commit konvence

Krátký imperativ česky, pak výčet změn v odrážkách:

```
Přidej skill ocenovani + ingestion PDF parseru

- backend/app/skills/ocenovani.py (BaseSkill)
- backend/app/ingest/pdf_parser.py
- frontend/app/skills/ocenovani/page.tsx
```
