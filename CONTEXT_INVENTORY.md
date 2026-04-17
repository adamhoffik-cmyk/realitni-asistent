# CONTEXT INVENTORY — Realitní Asistent

> Inventura obsahu školicích a pracovních materiálů uživatele (RE/MAX Living Česká Lípa).
> Zdroj: adresáře `REAL ESTATE/` a `marketing material 2026/`.
> Generováno: 2026-04-17.

Tento dokument slouží jako mapa zdrojových dat pro RAG (ChromaDB) a rozhodování o kategorizaci. Plné cesty jsou relativní ke kořeni projektu.

---

## ADRESÁŘ 1: `REAL ESTATE/`

Hlavní repository vzdělávacích a operačních materiálů makléře. ~200+ souborů, mix PDF / DOCX / TXT / XLSX / PNG.

### 1. `__HUSTLE/` — denní operační práce (~81 souborů)

Primární pracovní složka — marketing, nábor, smlouvy, klienti, porady.

#### 1.1 `příprava materiálů/` (9 souborů, edukační PDF 2018–2019)
Reprezentativní soubory:
- `2019_Prirucka maklere_FINAL_EDICE 8_květen 2019.pdf` — hlavní příručka makléře RE/MAX
- `2018-10-04_prubeh_obchodu.pdf` — průběh obchodu (klíčový procesní dokument)
- `2018-11-02_zaruka-spokojenosti.pdf`
- `2018-10-04_vyhody-a-nevyhody-exkluzivni_smlouvy.pdf`
- `Jak se chránit před nároky kupujícího z vad prodané nemovitosti.pdf`

#### 1.2 `___Dokumenty, pnb, SMLOUVY/` (19 souborů)
Podstruktura:
- `0) tisk a znát/` — AML dotazníky, obchodní podmínky, tisknutelné smlouvy
- `ZS zprostředkovatelské smlouvy/` — šablony (prodávající, kupující, družstevní podíl)
- `__aktualni smlouvy/` — nájemní, rezervační smlouvy
- `advokáti/` — komunikace s právníky, potvrzení úschovy

Klíčové šablony:
- `2025-04-29_REMAX Living_smlouva-o-vyhradnim-poskytovani-realitnich-sluzeb-prodavajici.docx`
- `2025-04-29_obchodni-podminky.pdf`
- `AML-dotaznik-remax_nový 2018.docx`

#### 1.3 `___ marketing/` (~81 souborů)
- `loga atd/` (55 souborů) — RE/MAX branding (logotypy, vodoznaky, balón) ve formátech PNG, JPG, EPS, AI (CMYK i RGB)
- `_články/` — blogerské články a copywriting
- `videa/` — scénáře, strategie
- Textové soubory: `LINKEDIN.txt`, `REMAX.txt`, `sociální sítě.txt`, `scenare tipy.txt`, `namety 2 a 3 video.txt`, `tudu.txt`
- `plachty/` — billboardy, plakáty

#### 1.4 `_____NÁBOR/` (26 souborů)
- `eBook 365 náborovych aktivit.pdf` — klíčový zdroj o metodách náboru
- `Napoveda-grafika-Nahlizeni-standard.pdf` — práce s katastrem
- `plan.txt` — „150 dopisů týdně, 7,5k/rok, obsluha 2600 vybraných 3x ročně"

Podsložky:
- `AML/` — AML procedury (identifikace, ověřování zdrojů, PEP)
- `_CC/` — cold calling scripts (`call script - BEZREALITKY CC.txt`, `best.txt`, `cizelovany.txt`, `cold call LIST.xlsx`)
- `_dopisy/` — šablony dopisů majitelům z katastru

#### 1.5 `__aktivity/` (5 souborů — osobní learning log)
- `aktivity.ods` — tracker aktivit
- `final naučit se.txt` — osobní TODO (číst smlouvy, připravit call balíčky)
- `videa tipy - při koupi nemovitosti.txt` — náměty (Ještěd s dronem, Kvítkov, Mělník) + draft textu na web (příběh přechodu z IT/Škoda Auto na reality)

#### 1.6 `_klienti/` — klientské spisy
- `dufková/`, `ometák/rz moje vs/`, `svoboda/`, `venzara/`, `_hledá se nemo/` (Drábek)

#### 1.7 `_moje nemovitosti/` — výpis z katastru (`283232008011.pdf`)

#### 1.8 `_desky/` — prezentace klientům (`Desky Pittner.ppsx`, návod na el. desky)

#### 1.9 `LV/` — `eBook LIST VLASTNICTVI.pdf`

#### 1.10 `moje fota/` — personal branding fotografie + RE/MAX Living logo

#### 1.11 `podpis/` — `podpis.html`

#### 1.12 `porady/` — záznamy porad (např. `20260305.txt`)

#### 1.13 `vasek tomanec/` — mentorský feedback (Václav Tománek)

#### 1.14 `vzdelani EDU/`
- `eBook Realitni psychologie - 54 zamysleni.pdf`
- `ceny RD v cemap.txt`

#### 1.15 `zemek dotazy porady/` — `dotazy zemek.txt` (Q&A od mentora Zemka)

#### 1.16 `časáky/` — `2025_RM_07.pdf` (časopis RE/MAX)

---

### 2. `__PŘÍPRAVA POWERSTART/` (~44 souborů) — formální školení/certifikace

#### 2.1 `0 před mentoringem ke studiu/` (24 souborů)
- `Základní pojmy v realitách.pdf`
- `Oceňování nemovitostí - souhrn ke zkoušce RZ.pdf`
- `Stavební minimum - souhrn ke zkoušce.pdf`
- `Testové otázky ke zkoušce RZ.pdf`
- `Zprostředkovatelské smlouvy.pdf`
- `Názvosloví v realitách.docx`
- `Definice ploch v realitách.pdf`
- `DOSAVADNÍ ZÁKAZNÍCI - SFÉRA VLIVU_připomenutí_SP_TF.docx`
- `Mapové značky katastrální mapy.doc`
- `Obecné pojmy (1).pdf`
- `Časová osa prodeje - Martin Březina.pdf`
- Subfolder `RX úvodní interní dokumenty/` — mise, vize, hodnoty, etický kodex, reklamační řád, záruka spokojenosti RE/MAX (7 PDF)

#### 2.2 `stav nemovite veci/` (6 souborů) — technické posuzování
- `VADY.PORUCHY.POZEMNICH.STAVEB.pdf`, `TRHLINY-BOSCARDINO.pdf`, `STAVEBNI.DOKUMENTACE-FINAL.pdf`, `ZAKLADNI_POJMY2.pdf` + BP příloha

#### 2.3 `zákon o realitním zprostředkování/` (2 PDF)
- `2020-02-28_zakon-o-realitnim-zprostredkovani.pdf`
- `2020-04-28_zorz_postupy_makler_aktualizace.pdf`

#### 2.4 `testovaci otazky/` (6 souborů) — RM TEST 125 a 255 (otázky s/bez odpovědí)

#### 2.5 `proces obchodu/` (9 souborů) — **KRITICKÝ OBSAH**
- `Proces _ Skupina 1 _21.7.2025.pdf` — bez zástavy
- `Proces _ Skupina 2_ 21.7.2025.pdf` — s úvěrem kupujícího
- `Proces _ Skupina 3 _21.7.2025.pdf` — vlastní zdroje + hypotéka
- `Proces _ Skupina 4-6.pdf`
- `průběh obchodu - ZEMEK.txt` — detailní 190řádkový zápis mentora:
  - Třída 1: vlastní zdroje bez zástavy (ZS → RS online → marketing → KS → depozita → katastr 25 dní)
  - Třída 2: vlastní zdroje + úvěr (ZS → RS → financování → KS + SoAÚ → hypotéka → úschova)
  - Třída 3: komplexní scénář se zástavou na prodávané nemovitosti (4–12 týdnů)

#### 2.6 Další: `příprava na zkoušku RZ/`, `prihl zk rz.pdf`

---

### 3. `__ REAL profesional/` (~46 souborů) — případové studie POWERSTART skupin 1–6

Každá skupina obsahuje:
- `Podkladové materiály - Případové studie.pdf`
- `Závěrečný test případové studie.pdf`
- `Námitkové kartičky.pdf` (objection handling)
- `Script na volání ze sféry vlivu.pdf`
- `RE_MAX profil makléře.pdf`, `RE_MAX Golden Ticket k podpisu.pdf`
- `Telefonní balíček _ vzor.pdf`
- `Profil makléře _ Šablona.docx`, `Karta klienta.xlsx`, `Týdenní sledování aktivit.xlsx`

---

### 4. Ostatní kořenové složky
- `smlouvy/` — 2 aktuální šablony (2025-04-29)
- `podklady zajimavosti/` — `2025-05-13_ceny-nemovitosti-v-cr.docx`
- `prodej mých/` — `lempach csa.txt` (vlastní transakce — zástava, dluh)
- `artjom STAVEBNÍ MINIMUM II.pdf`, `p. Zemek DOTAZY.txt`, `slozky.txt`, `todo fix.txt`
- `Snímek obrazovky 2026-02-21 054059.png`

---

## ADRESÁŘ 2: `marketing material 2026/`

### `ikony/` (304 souborů)
Profesionální ikonografická knihovna ve dvou barevných variantách:
- `Dark Blue/` (~150 ikon)
- `White/` (~150 ikon)

Pokrývá: obchodní pojmy (listing, agent, proposal), nemovitostní prvky (balcony, kitchen, garage, floorplan), CX témata (`CX_3month-exclusive-listing`, `CX_weekly-updates-buyers`, `CX_welcome-home-call`), obecné (calendar, contact, newsletter, search).

### Další:
- `balon.jpeg`, `blu.png`
- `living s fotkou.png`, `living s fotkou white text.png` — klíčové marketing grafiky

---

## NAVRHOVANÁ KATEGORIZACE PRO CHROMADB

| # | Kategorie | Tag | Zdroje |
|---|-----------|-----|--------|
| 1 | `legal_templates` | Smluvní šablony, právní rámec | `__HUSTLE/___Dokumenty pnb SMLOUVY/`, `smlouvy/`, `zákon o RZ/` |
| 2 | `training_pdf` | Vzdělávací PDF | `__HUSTLE/příprava materiálů/`, `0 před mentoringem/`, `stav nemovite veci/`, `__ REAL profesional/` |
| 3 | `process_procedures` | Postup obchodu, workflows | `proces obchodu/`, `porady/`, `zemek dotazy porady/` |
| 4 | `sales_scripts` | Nábor, cold calling, objection handling | `_____NÁBOR/` (celé), `_CC/`, `AML/`, námitkové kartičky |
| 5 | `content_marketing` | Social media, copywriting, video scénáře | `___ marketing/`, `__aktivity/` |
| 6 | `remax_standards` | Mise, vize, hodnoty, etický kodex | `RX úvodní interní dokumenty/` |
| 7 | `technical_knowledge` | Vady staveb, oceňování, dokumentace | `stav nemovite veci/`, `Oceňování.pdf`, `Stavební minimum.pdf` |
| 8 | `market_data` | Ceny, psychologie trhu | `podklady zajimavosti/`, `vzdelani EDU/` |
| 9 | `personal_notes` | Vlastní TODO, progress, mentorský feedback | `__aktivity/`, `porady/`, `vasek tomanec/`, `final naučit se.txt` |
| 10 | `branding_assets` | Loga, vodoznaky, ikony | `___ marketing/loga atd/`, `moje fota/`, `marketing material 2026/ikony/` |
| 11 | `client_docs` | Klientské spisy (PII — šifrovat!) | `_klienti/`, `prodej mých/` |
| 12 | `certification` | Testy, Golden Ticket | `testovaci otazky/`, `__ REAL profesional/` (testy) |

---

## DOPORUČENÝ INGESTION WORKFLOW

1. **Parsing:** PDF → `pdfplumber` / `pypdf`; DOCX → `python-docx`; TXT → přímo; ODS/XLSX → `openpyxl`/`pandas`; obrázky přeskočit (jen index filenames + metadata pro použití ve webu/článcích).
2. **Chunking:** 512–1024 tokens (procesní dokumenty větší, scripty menší). Respektovat nadpisy.
3. **Embedding:** multilingual model — `intfloat/multilingual-e5-large` nebo `BAAI/bge-m3` (lepší pro češtinu než `all-MiniLM`).
4. **Metadata per chunk:** `category` (z tabulky výše), `source_file`, `source_path`, `page/section`, `created_at`, `tags[]`, `sensitivity` (public/internal/client_pii).
5. **Sensitivity handling:** Kategorie 11 (`client_docs`) — aplikační šifrování, nikdy v odpovědích necitovat rodná čísla ani plné kontakty.

---

## VÝJIMKY / POZNÁMKY

- **Starší PDF (2018–2019)** — stále referenční, ale v právních pasážích MUSÍ být ověřeny web searchem proti aktuálnímu stavu 2026.
- **TXT soubory s osobním charakterem** — některé obsahují motivační poznámky, ne každý má RAG hodnotu. Při ingestion filtrovat podle délky (min. ~50 slov) a obsahu.
- **Obrázkové PDF** — občasné OCR scany mohou vyžadovat `tesseract` (čeština).
- **GAP:** chybí transkripty videí (budou přibývat skrze Skill 2) a měřitelné KPI (bude třeba definovat s uživatelem).
