# 👋 Vítej zpět (podruhé)!

Za tu hodinu jsem udělal **hodně** — shrnutí níže. Deploy krok na konci.

## ✨ Co přibylo

### 1) Google Calendar integrace (Fáze 2-A)
- Full OAuth2 flow s šifrovanými tokeny v SQLite (`oauth_tokens` tabulka)
- Backend API `/api/calendar/events` (list, create, delete)
- Frontend **CalendarWidget** na home — když nejsi přihlášen, nabídne button "Připojit Google účet"
- 📘 Návod: [docs/GOOGLE_OAUTH_SETUP.md](GOOGLE_OAUTH_SETUP.md) — 10 min setup v Google Cloud Console
- Šifrování: AES-256-GCM přes `cryptography`, klíč z env `PII_ENCRYPTION_KEY`

### 2) Skill Video → Scénář (Fáze 4)
- `core/transcribe.py`: yt-dlp (IG/FB/TikTok/YouTube) → ffmpeg 16 kHz mono → faster-whisper (CZ)
- API `/api/videos`: transcribe URL → uloží transkript → volitelně generuj scénář přes Claude
- Stránka `/skills/video-transcript`: vlož URL, sleduj progress, výstup vedle sebe (transkript ↔ scénář)
- Formáty scénáře: IG Reel 30s / 60s, TikTok, FB post 90s
- Volitelný "úhel" — uživatel může zadat vlastní nápad co zdůraznit

### 3) Saykin scraper (stylebook podklad)
- `scripts/scrape_saykin.py` — projde `artem-saykin.cz/blog` pagination, stáhne články přes trafilatura do markdown s frontmatter
- Po sjetí ingestuj přes `app.ingest.run --category content_style --type context` → RAG auto použije
- Na VPS:
  ```bash
  docker exec -it asistent-backend python -m scripts.scrape_saykin \
      --output /app/data/reference_articles/artem_saykin
  docker exec -it asistent-backend python -m app.ingest.run \
      --source /app/data/reference_articles/artem_saykin \
      --category content_style --type context
  ```

### 4) Dva nové skilly s vlastní praktickou hodnotou

#### 📯 `nabor` — Tracker náborových aktivit
- `/skills/nabor` — dashboard s 4 widgety (dopisy, cold cally, setkání, schůzky)
- Progress bary vs. týdenní cíl (150 dopisů, 140 cold callů, 3 schůzky)
- Rychlý quick-log formulář (typ, počet, poznámka)
- Chat kontext: "Jsi v režimu náborového trackeru…"

#### 👥 `sfera` — Sféra vlivu
- `/skills/sfera` — evidence osob pro 3× ročně kontakt
- Telefony a e-maily **šifrované** v DB (AES-GCM)
- Barevné zvýraznění: kdo je "overdue" (uplynul interval)
- 1-klik "Právě jsem kontaktoval" button → aktualizuje `last_contact_at`
- Filter "jen overdue"

### 5) UX / PWA
- Home screen: tlačítka **Paměť / Oblíbené / Nábor / Sféra vlivu** (rychlý přístup)
- PWA ikona v SVG (matrix-style "RA" monogram) — instalovatelné jako app na mobilu

### 6) Dokumentace (velký balík)
- 📄 [docs/GOOGLE_OAUTH_SETUP.md](GOOGLE_OAUTH_SETUP.md) — setup Google Cloud OAuth (10 min)
- 📄 [docs/SKILL_IDEAS.md](SKILL_IDEAS.md) — **návrh 12 skillů** pro tvoji realitní praxi (Top 5: nábor, sféra, AML, smlouvy, oceňování)
- 📄 [docs/WELCOME_BACK_2.md](WELCOME_BACK_2.md) — tenhle soubor

---

## 🚀 Deploy

```bash
ssh root@46.225.58.232
cd /opt/realitni-asistent && git pull
docker compose --profile production up -d --build backend frontend
```

Trvá ~3-5 min. Po startu se automaticky vytvoří nové DB tabulky: `nabor_activities`, `sfera_persons`.

### Pro Google Calendar (volitelný krok)

Postupuj podle [docs/GOOGLE_OAUTH_SETUP.md](GOOGLE_OAUTH_SETUP.md) — vytvoř si OAuth Client v Google Cloud Console (zdarma), vlož credentials do `.env`, restart backendu, klikni "Připojit Google účet" ve widgetu.

### Pro Saykin stylebook (volitelně)

```bash
docker exec -it asistent-backend python -m scripts.scrape_saykin \
    --output /app/data/reference_articles/artem_saykin
# pak:
docker exec -it asistent-backend python -m app.ingest.run \
    --source /app/data/reference_articles/artem_saykin \
    --category content_style --type context
```

Po tomto kroku Claude při generování článků automaticky vyhledává v Saykinových textech a píše ve tvém stylu.

---

## 📊 Celkový stav aplikace

| Funkce | Stav |
|--------|------|
| HTTPS + BasicAuth | ✅ |
| Matrix UI | ✅ |
| Weather widget (Zahrádky) | ✅ |
| **Calendar widget** | ✨ Fáze 2-A hotová (OAuth setup 10 min) |
| News widget (9 RSS) | ✅ |
| Oblíbené novinky | ✅ |
| Paměť API + `/memory` | ✅ |
| Chat s reálným Claude | ✅ |
| RAG ingestion PDF/DOCX | ✅ |
| **Skill Články (generování)** | ✅ |
| **Skill Video → Scénář** | ✨ NOVÉ |
| **Skill Nábor tracker** | ✨ NOVÉ |
| **Skill Sféra vlivu** | ✨ NOVÉ |
| **Saykin scraper** | ✨ (spustitelný) |
| PWA ikona | ✅ (SVG) |
| Ranní briefing | ⏳ stub (Fáze 5) |

## 📝 Co ještě doladit (ve chvíli kdy budeš chtít)

- **Ranní briefing v 7:00** — APScheduler už běží, zbývá přidat logiku generování (stub je v `scheduler/jobs.py`)
- **Drive export článků/scénářů** — až budeš mít hotový Google OAuth
- **Další skilly z [SKILL_IDEAS.md](SKILL_IDEAS.md)** — `aml-flow`, `smlouva-generator`, `ocenovani`
- **Testy** — zatím žádné (pytest kostra připravena v pyproject)

## ❤️ Co si mi přeju zkusit

1. **Chat** — napiš "Co vidíš v mojí paměti?" (po ingest testu)
2. **Rychlá poznámka** — "Klient Novák chce 2+kk v České Lípě do 3M" → jdi na `/memory` → sémantické hledání "novák byt" → musí najít
3. **News** → ❤ → `/favorites` → ✍ "Přetvořit na článek" → draft
4. **Video** — vlož URL z IG Reels, po transkripci vygeneruj IG Reel 60s scénář
5. **Nábor** — zaznamenej 10 dopisů, uvidíš progress bar

Užij si to! 💚🚀

— AI asistent (ten v Claude Code)
