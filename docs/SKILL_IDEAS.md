# Návrh nových skillů pro realitní praxi

> Prošel jsem všechny tvé materiály (POWERSTART, HUSTLE, NÁBOR, klientské spisy, marketing, Saykin články) a navrhl 12 skillů, které odrážejí konkrétně **tvoji** denní práci makléře v Česká Lípa / RE/MAX Living.

Roztřídil jsem je do 4 skupin podle přínosu × náročnost implementace. **Top 5** jsou pro tebe nejhodnotnější podle mého pochopení.

---

## 🏆 TOP 5 — konkrétně ti pomohou hned

### 1. `nabor-tracker` — Tracker náborových aktivit
**Proč**: Tvůj plán "150 dopisů týdně, 7 500 ročně, obsluha 2 600 vybraných 3× ročně" (z `_____NÁBOR/plan.txt`) potřebuje evidenci. Teď to máš nejspíš v hlavě nebo v Excelu.

**Co dělá**:
- Denní log: kolik dopisů, cold callů, osobních setkání
- Dashboard: týdenní/měsíční progres vs. cíl
- Připomínky: "Volal jsi dnes 10×? Cíl je 20–30." (podle `call script - BEZREALITKY CC.txt`)
- Leaderboard self-reviewing: "Tento měsíc jsi na 80 % cíle"
- Exportovatelné CSV pro reportování

**Data**: `activities` tabulka (datum, typ, počet, poznámka)  
**UI**: `/skills/nabor` s grafy (recharts)  
**Implementace**: 3-4 h

---

### 2. `sfera-vlivu` — Evidence a automatické reminders
**Proč**: `DOSAVADNÍ ZÁKAZNÍCI - SFÉRA VLIVU_připomenutí.docx` říká, že máš oslovovat 3× ročně (=á 4 měsíce). Bez trackeru to nejde dělat systematicky.

**Co dělá**:
- Karta osoby: jméno, kontakt, jak se znáte (rodina/přítel/bývalý klient), poznámky
- Automatické připomínky: "Jana Nováková — naposledy kontakt před 4 měsíci, ozvi se"
- Generování zprávy: AI vytvoří osobní text (ne generický) na základě historie
- Propojení s kalendářem: klik "Naplánovat hovor" → event
- Anonymizace v RAG (rodná čísla, telefony — šifrovaně)

**Data**: `persons` tabulka (už v `Note.type="person"`, rozšíříme)  
**UI**: `/skills/sfera-vlivu` s filtrem podle "dní od posledního kontaktu"  
**Implementace**: 4-6 h

---

### 3. `aml-flow` — Průvodce AML identifikací klienta
**Proč**: AML je **povinná** u realit a je to nuda. V `_____NÁBOR/AML/AML.txt` máš detaily — tenhle skill to dělá v UI místo ručního vyplňování formuláře.

**Co dělá**:
- Průvodce krok-po-kroku: typ identifikace (fyzická / elektronická / zprostředkovaná)
- Formulář: údaje klienta (ID, trvalé bydliště, rodné číslo zašifrovaně)
- PEP check: upozornění na politicky exponované osoby
- Ověření zdroje financí (tabulka z tvého AML.txt)
- Export do PDF — podpis klient + ty
- Uloží jako `Note.type=person, sensitivity=client_pii`

**Data**: `aml_checks` tabulka + šifrované PII  
**UI**: `/skills/aml` wizard ve 4 krocích  
**Implementace**: 4 h

---

### 4. `smlouva-generator` — Generování zprostředkovatelky + rezervačky
**Proč**: Máš šablony v `__HUSTLE/___Dokumenty pnb SMLOUVY/` — teď je ručně upravuješ v Wordu. Skill naplní pole z karty klienta/nemovitosti a vygeneruje finální DOCX.

**Co dělá**:
- Zvol typ: zprostředkovatelská (prodávající/kupující), rezervační, smlouva o budoucí kupní
- Vybereš klienta (ze `persons`) a nemovitost (ze `properties`)
- Předvyplní šablonu (DOCX template s `{{jmeno}}`, `{{adresa}}` atd.)
- AI check: pluginový `legal:review-contract` najde odchylky vs. playbook
- Export DOCX + PDF na Drive

**Data**: reuse existujících šablon ze `smlouvy/`  
**UI**: `/skills/smlouva` → wizard  
**Implementace**: 4 h + je potřeba přepsat šablony do templateable formátu (`{{var}}`)

---

### 5. `ocenovani` — Rychlý odhad ceny nemovitosti
**Proč**: "Kolik by to mělo stát?" — první otázka klientů. Máš `Oceňování nemovitostí - souhrn ke zkoušce RZ.pdf` a `ceny RD v cemap.txt` jako podklad.

**Co dělá**:
- Zadáš parametry: typ (byt/dům), dispozice, m², lokalita, rok stavby, stav
- Scrape inzerátů (sreality.cz, realitymix, bezrealitky) pro porovnávací ceny v okolí
- AI souhrn: "Byt 2+kk v České Lípě, 65 m², 2010, dobrý stav → 3.2–3.8 M Kč (medián 3.5 M). Podobných v okolí 8."
- Výstup: PDF/markdown shrnutí pro klienta

**Data**: `valuations` tabulka (historie oceňování)  
**UI**: `/skills/ocenovani` — formulář + výsledek  
**Implementace**: 5 h (nejvíc práce: spolehlivý scraper realit webů)

---

## 📦 Další — využitelné, ale nižší priorita

### 6. `klienti-crm` — Karta klienta s historií komunikace
Evidence poptávky (kdo hledá co), historie schůzek, poznámky. Auto-sync s kalendářem. Integrace s Gmail MCP ("stáhni poslední e-maily od …").

### 7. `nabidka-prezentace` — Auto-prezentace nemovitosti
Z karty nemovitosti vygeneruje PDF prezentaci (foto, popis, plán, okolí). Šablony podle `__HUSTLE/_desky/`.

### 8. `home-staging` — Checklist před focením/prohlídkou
Podle typu nemovitosti (byt/dům) vygeneruje checklist (dekor, světlo, vůně, úklid). Foto checkpoint.

### 9. `nda-triage` — Využije plugin `legal:triage-nda`
Příchozí NDA (od developer/banka) → AI rozhodne ZELENÁ/ŽLUTÁ/ČERVENÁ. UI jen wrapper nad pluginem.

### 10. `vzdelavani` — Quiz z tvých materiálů
Z RAG paměti (POWERSTART PDFs) generuje otázky podle testů RM TEST 125/255. Pro revizi před zkouškou nebo jen pro udržení znalostí.

---

## 🔮 Vize — komplexní, pokud by zbyl čas

### 11. `kampan-reality` — Multi-channel kampaň na jednu nemovitost
- Generuje **tři variants**: post na FB, story na IG, inzerát pro sreality
- Zná tvůj styl (Saykin stylebook + tvé články)
- Plánuje timing (pondělí FB, středa IG story, čtvrtek inzerát)

### 12. `market-insight` — AI dashboard trhu
- Denní AI souhrn: "Co se tento týden stalo v realitním trhu (hypotéky, ČNB, ceny v Libereckém kraji)?"
- Generuje kartičky "insight pro klienty" — můžeš poslat SMSkou: "Ahoj Jano, ČNB drží sazbu, hypotéky stagnují…"

---

## Priorita podle mého doporučení

**Fáze 6:**
1. ✅ `nabor-tracker` — 3-4 h, high value, bez externích závislostí
2. ✅ `sfera-vlivu` — 4-6 h, využije kalendář + memory
3. ✅ `aml-flow` — 4 h, reguloryka

**Fáze 7:**
4. ✅ `smlouva-generator` — 4 h, ale potřebuje přepsat šablony
5. ✅ `ocenovani` — 5 h, scraping závisí na target webech

**Fáze 8+** (až budeš mít zaběhnuté core):
6-12 podle tvého zájmu.

---

## Co z toho teď?

Nemám kapacitu udělat všech 12 za hodinu. **V tomto commitu udělám jen kostry těch top 3 (nabor-tracker, sfera-vlivu jako read-only CRUD) a zbytek dodělá budoucí já :).** Tvůj input je klíčový — který ti dává nejvíc smysl?

Také: všechny využívají již hotovou infrastrukturu (SQLAlchemy modely, chat, paměť, kalendář). Takže každý další skill je rychlejší.
