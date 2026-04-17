# 👋 Vítej zpět!

Za tu hodinu jsem udělal kus práce. Shrnutí + tvoje akce pro nasazení.

## ✨ Co přibylo (6 commitů: `87e16da` → `e27be2b`)

### Fáze 2-B · Paměť API + ChromaDB RAG
- **Backend:** `/api/notes` CRUD + `/api/notes/search` sémantické hledání
- **Frontend:** stránka `/memory` (seznam, filter podle typu, sémantické hledání, delete)
- **QuickNote** na home page teď ukládá reálně (bylo jen stub)

### Fáze 2-C · Reálný chat (Claude Agent SDK)
- **claude_client.py** plně integrovaný s `claude-agent-sdk` Python package (streaming tokenů, tool calls, Result usage)
- **context_builder.py** sestaví system prompt s RAG top-K (threshold 0.3)
- **Chat WS** přijímá historii, posílá reálnou odpověď tokenovým streamem

### Fáze 2-D · RAG ingestion CLI
- `python -m app.ingest.run --source <dir> --category <tag>`
- Parsuje PDF (pdfplumber), DOCX (python-docx), TXT/MD
- Chunking 800 znaků + 100 overlap, ukládá jako `Note type=context` s metadaty

### Fáze 5 partial · News scraper + APScheduler
- **9 Tier 1 RSS zdrojů**: Hypoindex, ČNB tiskovky + čnBlog, HN Reality, ESTAV, TZB-info (2 feedy), Českolipský deník, Novinky.cz (s keyword filtrem)
- **APScheduler** v backendu — auto-fetch každé 2 hodiny, joby persistují v SQLite
- **NewsWidget** na home page s auto-refresh a manual refresh button

### Backend container vybaven Claude CLI
- Node 22 + `@anthropic-ai/claude-code` v image (+300 MB)
- Mount `~/.claude` z hostu → plugins + login sdílené s hostem
- Znamená: chat v kontejneru teď může volat `claude` skutečně

---

## 🚀 Tvoje akce na VPS (cca 10 min)

**1) Pull + rebuild backend:**

```bash
cd /opt/realitni-asistent
git pull
docker compose --profile production up -d --build backend frontend
```

Build backendu bude trvat ~5 min (Claude CLI install + nové dependency vrstvy). Frontend ~1 min.

**2) Ověř status:**

```bash
docker compose --profile production ps
docker compose --profile production logs backend --tail=20
```

Backend by měl naběhnout do `healthy`. Ve startup logu bys měl vidět:
```
Scheduler: fetch_news start
Scheduler: fetch_news DONE — XX new items from 9 sources
```

**3) Otevři https://asistent.46-225-58-232.nip.io** (BasicAuth: adam + tvoje heslo)

Nové věci, které bys měl vidět:
- 📰 **Novinky widget** — reálné zprávy z 9 zdrojů (auto-refresh po 2 h, nebo klikni na ⟳)
- 📚 **Odkaz Paměť** pod widgety → otevře `/memory` stránku
- ✎ **Rychlá poznámka** — napiš cokoli, klikni Uložit → poznámka se uloží do paměti + Chromy
- Jdi na `/memory` → zkus sémantické hledání "byt novák" nebo co jsi napsal

**4) Zkus chat** (Ctrl+K nebo ikona vpravo nahoře)

Napiš "Ahoj". Měl bys dostat **reálnou** odpověď od Clauda (ne už echo stub).

Pokud Claude nereaguje nebo hodí error, logy ti řeknou proč:
```bash
docker compose --profile production logs backend | grep -i claude
```

Možné problémy:
- Claude CLI v kontejneru ještě není přihlášený. Spusť:
  ```bash
  docker exec -it asistent-backend claude login
  ```
  Což tě provede login flow (ale ten potřebuje browser — viz poznámku níže).
- Mount `~/.claude` z hostu nefunguje kvůli permissions. Zkus:
  ```bash
  docker exec -it asistent-backend ls -la /home/app/.claude/
  ```

**5) (Volitelně) Nahrání školicích materiálů do RAG**

Pokud chceš, aby AI měla přístup k tvým materiálům z `REAL ESTATE/` a `marketing material 2026/`, zkopíruj je na VPS a spusť ingestion:

```bash
# Z tvého PC:
scp -r "C:/Users/adamh/AI APLIKACE/realitni asistent/Realitní asistent/REAL ESTATE" \
    root@46.225.58.232:/opt/realitni-asistent/backend/data/reference_articles/

# Na VPS:
docker exec -it asistent-backend python -m app.ingest.run \
    --source /app/data/reference_articles/REAL\ ESTATE \
    --category training_pdf \
    --type context

# Pak to chvíli potrvá (stovky chunků), logy ukazují progress
```

Po ingestu bude AI automaticky vyhledávat v těch materiálech při chatu.

---

## ⚠ Známé problémy, co vyřešíme příště

### Claude Max login v kontejneru
`claude login` otevírá browser pro OAuth. V kontejneru přes SSH browser není. Dvě cesty:
- **A)** Na hostu se přihlásit (`claude login` v SSH session) → `~/.claude/.credentials.json` → mount do kontejneru. **Už by to mělo fungovat** díky volume mount.
- **B)** Pokud `~/.claude/.credentials.json` není ze starého loginu platný, obnovit přes browser na tvém PC → zkopírovat soubor na VPS přes `scp`.

Ověř:
```bash
ls -la /root/.claude/.credentials.json
docker exec -it asistent-backend cat /home/app/.claude/.credentials.json | head -1
```
Oba by měli ukázat JSON s access tokenem.

### Google OAuth (Gmail/Calendar/Drive) — ještě není
Plugin `legal` má MCP servery pro Google služby, ale používají Anthropic proxy s OAuth. Až budeš chtít kalendář + e-mail v aplikaci, musíme rozhodnout:
- Použít ty MCP servery (přes chat volat)
- Vlastní OAuth flow v našem backendu

Promluvíme se o tom, až bude potřeba.

---

## 📊 Co je teď v aplikaci funkční

| Funkce | Stav |
|--------|------|
| HTTPS + BasicAuth | ✅ |
| Home screen + Matrix UI | ✅ |
| Weather widget (Zahrádky) | ✅ |
| **News widget (9 RSS zdrojů)** | ✨ NOVÉ |
| **Rychlá poznámka → paměť** | ✨ NOVÉ |
| **Stránka Paměť (list + search)** | ✨ NOVÉ |
| **Chat s Claudem (po rebuildu)** | ✨ NOVÉ |
| Skill systém (demo) | ✅ |
| Kalendář | ⏳ čeká na Google OAuth |
| Ranní briefing | ⏳ stub (Fáze 5) |
| Skill Články (psaní/legalizace) | ⏳ Fáze 3 |
| Skill Video transkripce | ⏳ Fáze 4 |
| Zálohy | ❌ záměrně vyloučeno |

Tak se pusť do toho! Když cokoli vyhodí chybu, pošli mi logs + pokračujeme. 💚
