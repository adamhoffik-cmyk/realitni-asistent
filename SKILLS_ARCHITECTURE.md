# SKILLS ARCHITECTURE — Realitní Asistent

> Jak fungují skilly jako zásuvné moduly (pluginy) v aplikaci.
> Verze: 0.1 (draft ke schválení) | Datum: 2026-04-17

---

## 1. CO JE "SKILL"

**Skill** je samostatný modul, který:
- **Backend:** definuje business logiku (pipeline, tooly, API endpointy) jako podtřídu `BaseSkill` v `/backend/app/skills/<nazev>.py`
- **Frontend:** má vlastní stránku `/frontend/app/skills/<nazev>/page.tsx` + dlaždici na home screen
- **DB:** má záznam v tabulce `skills` (registr) — ikona, pořadí, enabled flag, usage count, config
- **Chat:** přednastavuje kontext (system prompt modifier) když je aktivní skill-specific obrazovka
- **Tooly:** může registrovat vlastní nástroje pro AI (přes decorator `@skill_tool`)

**Dva příklady z MVP:** `articles` (psaní/legalizace článků), `video_transcript` (transkripce → scénář).

---

## 2. ANATOMIE SKILLU — BACKEND

### `BaseSkill` třída (kontrakt)

```python
# backend/app/skills/base.py
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator
from pydantic import BaseModel

class SkillManifest(BaseModel):
    id: str                    # slug, např. "articles"
    name: str                  # "Články"
    description: str           # krátký popis pro dlaždici
    icon: str                  # název ikony (z marketing material 2026/ikony/)
    order_index: int = 100
    version: str = "0.1.0"
    chat_context_prompt: str | None = None   # system prompt modifier když je skill aktivní
    tile_preview: str | None = None          # co se ukáže na dlaždici (např. "12 draftů")

class BaseSkill(ABC):
    manifest: SkillManifest

    @abstractmethod
    async def on_register(self) -> None:
        """Volá se jednou při startu aplikace. Migrace, init modelu atd."""

    @abstractmethod
    def api_router(self) -> "APIRouter":
        """FastAPI router s endpointy skillu (mount pod /api/skills/{id})."""

    @abstractmethod
    def ai_tools(self) -> list["ToolDef"]:
        """Nástroje, které skill vystaví Claudovi (přes claude-agent-sdk)."""

    async def on_chat_invoke(self, message: str, ctx: "ChatContext") -> AsyncIterator[str] | None:
        """Volitelný hook — když chat detekuje skill-specific intent (slash command)."""
        return None

    async def tile_data(self) -> dict[str, Any]:
        """Vrátí live data pro dlaždici (počet draftů, poslední akce…)."""
        return {}
```

### Skill registry

```python
# backend/app/skills/registry.py
class SkillRegistry:
    _skills: dict[str, BaseSkill] = {}

    @classmethod
    def register(cls, skill: BaseSkill) -> None: ...
    @classmethod
    def get(cls, skill_id: str) -> BaseSkill: ...
    @classmethod
    def enabled(cls) -> list[BaseSkill]: ...
    @classmethod
    async def bootstrap(cls) -> None:
        """Iteruje `backend/app/skills/*.py`, importuje moduly, volá on_register(),
        synchronizuje záznamy v tabulce `skills`."""
```

Startup (`app/main.py`):
```python
from app.skills.registry import SkillRegistry
from app.skills import articles, video_transcript   # explicitní import

@app.on_event("startup")
async def startup():
    await SkillRegistry.bootstrap()
    # mount routerů
    for skill in SkillRegistry.enabled():
        app.include_router(skill.api_router(), prefix=f"/api/skills/{skill.manifest.id}")
```

---

## 3. ANATOMIE SKILLU — FRONTEND

### Struktura souborů

```
frontend/app/skills/<skill-id>/
├── page.tsx              # hlavní stránka skillu (server component)
├── components/           # skill-specific komponenty
├── actions.ts            # server actions (tenké wrappery nad /api/skills/<id>/…)
├── hooks/                # react hooks
└── icon.tsx              # inline SVG ikona (nebo odkaz na PNG z /marketing/)
```

### Home dlaždice — konvence

Jeden sdílený komponent `<SkillTile skillId="articles" />` vyvolá backend `/api/skills/articles/tile` (implementováno přes `BaseSkill.tile_data()`) a vykreslí:

```
┌──────────────────────┐
│  📝 Články           │
│  ──────────────────  │
│  12 draftů           │
│  Použito 47×         │
└──────────────────────┘
```

Klik = navigace na `/skills/articles`.

### Přepínatelná dlaždice — uspořádání

- Drag & drop (`@dnd-kit`) pro změnu pořadí → volá `POST /api/skills/reorder`
- Toggle enabled/disabled přes settings

---

## 4. CHAT ↔ SKILL INTEGRACE

### Kontextově vědomý chat

Když je uživatel na `/skills/articles`, chat panel:
1. Frontend pošle `context: "articles"` při otevření WS.
2. Backend v `core/context_builder.py` načte `articles.manifest.chat_context_prompt` a přidá ho do system promptu.
3. V hlavičce chatu se zobrazí: `🟢 Režim: Články`.

### Slash commands

Konvence: `/<skill-id>` nebo `/<alias>` (definuje `SkillManifest.chat_aliases`).

```
/clanek [téma nebo URL]
```

Chat parser (v `api/chat.py`):
1. Detekuje `/clanek` → rozpozná skill `articles`.
2. Volá `articles.on_chat_invoke(message, ctx)`.
3. Pokud skill vrátí async generátor, streamuje jeho výstup do WS místo default Claude odpovědi.
4. Pokud vrátí `None`, běží standardní chat tok (Claude s nástroji skillu).

### Skill tooly — kdy jsou dostupné?

- **Globální kontext** (chat bez skillu): tooly VŠECH enabled skillů jsou registrované u Clauda, ale s nižší prioritou v system promptu.
- **Skill-specific kontext:** tooly daného skillu jsou zvýrazněné v system promptu ("aktuálně pracuješ v režimu Články — preferuj tooly: save_article, lookup_reference_article…").

---

## 5. DB SCHÉMA — TABULKA `skills`

```sql
CREATE TABLE skills (
  id TEXT PRIMARY KEY,          -- slug
  name TEXT NOT NULL,
  description TEXT,
  icon TEXT,
  version TEXT,
  enabled BOOLEAN DEFAULT 1,
  order_index INTEGER DEFAULT 100,
  usage_count INTEGER DEFAULT 0,
  last_used_at DATETIME,
  config JSON,                   -- skill-specific config (user settings)
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Sync při startu:** pokud skill existuje v kódu, ale ne v DB → INSERT. Pokud existuje v DB, ale ne v kódu → ponechat záznam, nastavit `enabled=0` (nezmizí setting uživatele). Pokud `version` se liší → UPDATE name/description/icon.

---

## 6. DEV WORKFLOW — JAK PŘIDAT NOVÝ SKILL

### Příklad: skill `ocenovani` (oceňování nemovitostí)

**1. Backend modul** `backend/app/skills/ocenovani.py`:

```python
from app.skills.base import BaseSkill, SkillManifest
from fastapi import APIRouter

class OcenovaniSkill(BaseSkill):
    manifest = SkillManifest(
        id="ocenovani",
        name="Oceňování",
        description="Rychlý odhad ceny nemovitosti",
        icon="budget_price",          # z marketing material 2026/ikony/
        order_index=30,
    )

    async def on_register(self): pass

    def api_router(self):
        r = APIRouter()

        @r.post("/estimate")
        async def estimate(payload: EstimateRequest):
            return await self._run_pipeline(payload)

        return r

    def ai_tools(self):
        return [
            tool_def(
                name="estimate_property_price",
                description="Odhadne tržní cenu nemovitosti podle parametrů a lokálních dat",
                handler=self._tool_estimate,
                params_schema=...
            )
        ]

    async def tile_data(self):
        return {"recent_estimates": await db.count_recent_estimates()}
```

**2. Registrace** — přidat import do `backend/app/skills/__init__.py`:
```python
from . import articles, video_transcript, ocenovani   # ← nové
```

**3. Frontend stránka** `frontend/app/skills/ocenovani/page.tsx`:
```tsx
export default function OcenovaniPage() {
  return <OcenovaniClient />;
}
```

**4. Migrace (jen když skill má vlastní DB tabulky)** — `alembic revision -m "add ocenovani"`.

**5. Restart backendu** — registry detekuje nový skill, vloží do DB, mountuje router. Dlaždice se objeví na home.

**6. Otestovat** — `/skills/ocenovani` stránka funguje; chat `/ocenovani Byt 2+kk, 65 m², Česká Lípa, 2010, dobrý stav` vyvolá tooly.

---

## 7. KONVENCE

| Téma | Pravidlo |
|------|----------|
| Pojmenování ID | kebab-case, bez diakritiky (`ocenovani`, `video-transcript`) |
| Pojmenování Pythonu | snake_case modul, PascalCase třída (`ocenovani.py` → `OcenovaniSkill`) |
| Ikony | z `marketing material 2026/ikony/` — reference name bez přípony |
| Testovatelnost | skill MUSÍ být importovatelný bez side-effectů (žádné DB write v `__init__`) |
| Data | skill-specific tabulky prefixují `skill_<id>_…` (např. `skill_articles_drafts`) |
| Chat context prompt | max 300 slov, česky, imperativně |
| i18n | pouze čeština zatím |
| Dependency | skill NESMÍ importovat jiný skill přímo — přes registry (`SkillRegistry.get`) |

---

## 8. SKILL 1 — ČLÁNKY (předběžný manifest)

```python
SkillManifest(
    id="articles",
    name="Články",
    description="Generování a legalizace článků ve stylu Artema Saykina",
    icon="media-video",  # nebo 'document'
    order_index=10,
    chat_context_prompt="""
Jsi v režimu psaní článků. Preferuj nástroje:
- search_memory (hledej existující materiály a fakta)
- read_training_material (školicí materiály RE/MAX)
- fetch_url (pro režim B — legalizace)
- search_web (aktuální data pro 2026)
Stylebook: viz STYLEBOOK.md. Výstup piš v markdownu.
""",
)
```

Interní pipeline (viz `spec.md`): bootstrap scraper artem-saykin.cz → `STYLEBOOK.md` → Režim A (nové) / Režim B (legalizace) → self-review → export na Drive.

---

## 9. SKILL 2 — TRANSKRIPCE VIDEÍ (předběžný manifest)

```python
SkillManifest(
    id="video-transcript",
    name="Video → Scénář",
    description="Transkripce cizího videa a generování scénáře v mém stylu",
    icon="media-video",
    order_index=20,
    chat_context_prompt="""
Jsi v režimu práce s videem. Nástroje:
- transcribe_video (URL → transcript)
- write_article (ale v módu video_script)
Výstupem je scénář pro Instagram Reel 30–60s: hook → body → CTA,
s návrhy B-roll a textových overlayů.
""",
)
```

Interní pipeline: yt-dlp → ffmpeg (audio) → faster-whisper small (cz) → AI analýza → scénář → export.

---

## 10. BUDOUCÍ SKILLY (backlog, nevymýšlet implementaci)

Kandidáti pro Fázi 7+:
- `ocenovani` — oceňování nemovitostí
- `klienti` — CRM (kontakty, historie komunikace, follow-upy)
- `sfera-vlivu` — evidence sféry vlivu + připomínky pro 3× ročně kontakt
- `namor` — tracker náborových aktivit (dopisy, cold calls, scenes z `_____NÁBOR/`)
- `nabidka` — generátor prezentace nemovitosti (PDF z šablony)
- `bodovani-nemovitosti` — srovnávač vlastností dle kritérií klienta
- `aml-check` — interview flow z `_____NÁBOR/AML/`
- `smlouva-check` — využije plugin `ceske-realitni-pravo:review-contract`
- `nda-triage` — využije plugin `ceske-realitni-pravo:triage-nda`

Každý nový skill = nový modul podle sekce 6. **Neimplementuj preemtivně.**

---

## 11. OTÁZKY K ROZHODNUTÍ

1. **Načítání ikon** — PNG z `marketing material 2026/ikony/Dark Blue/` nebo `White/`? (Pro Matrix theme lepší White s CSS tint na zelenou.)
2. **Skill versioning** — když přijde kompatibilní breaking change v manifestu, umíme migrovat? (Pro MVP: ne, prostě `version` bump + uživateli sdělíme.)
3. **Testování skillů** — mám připravit pytest strukturu už ve Fázi 1, nebo až skilly přijdou (Fáze 3+)?

---

## ZÁVĚR

Skill systém je **lightweight plugin** s jasným kontraktem (`BaseSkill`), registrem v SQLite a sdílenou infrastrukturou (chat, tooly, Drive, Claude). Přidání nového skillu = 1 Python soubor + 1 Next.js stránka + 1 import v `__init__.py`.

Po schválení přejdeme na Fázi 1 — backend scaffold + první dummy skill pro ověření toku end-to-end (home dlaždice → stránka → chat).
