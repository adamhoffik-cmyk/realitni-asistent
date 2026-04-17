# Legal Plugin — Česká republika (Realitní praxe)

AI plugin pro právní práci v českém právním prostředí, zaměřený na realitní zprostředkování. Automatizuje kontrolu smluv, posouzení NDA, compliance workflows, právní briefingy a šablonové odpovědi — vše přizpůsobeno českému právu a zákonu o realitním zprostředkování.

> **Upozornění:** Tento plugin pomáhá s právními pracovními postupy, ale neposkytuje právní poradenství. Vždy ověřte závěry s kvalifikovaným advokátem.

## Cílové osoby

- **Realitní makléř** — Zprostředkovatelské, kupní, rezervační smlouvy, compliance
- **Vedoucí kanceláře** — Přehled rizik, smluvní standardy, compliance
- **Spolupracující odborníci** — Advokáti, hypoteční poradci, notáři

## Český právní rámec

| Předpis | Oblast |
|---------|--------|
| Občanský zákoník (č. 89/2012 Sb.) | Smluvní právo, kupní smlouva, nájem, zprostředkování |
| Zákon o realitním zprostředkování (č. 39/2020 Sb.) | Povinnosti realitního makléře |
| GDPR + zákon č. 110/2019 Sb. | Ochrana osobních údajů |
| Zákon o AML (č. 253/2008 Sb.) | Identifikace klientů, podezřelé obchody |
| Katastrální zákon (č. 256/2013 Sb.) | Zápis vlastnických práv |
| Zákon o ochraně spotřebitele (č. 634/1992 Sb.) | Ochrana klientů-spotřebitelů |

## Příkazy

| Příkaz | Popis |
|--------|-------|
| `/review-contract` | Kontrola smlouvy podle českého práva |
| `/triage-nda` | Rychlé posouzení NDA |
| `/vendor-check [partner]` | Stav smluv s partnerem |
| `/brief denni` | Ranní právní přehled |
| `/brief tema [dotaz]` | Výzkum tématu |
| `/brief incident` | Briefing k incidentu |
| `/legal-response [typ]` | Generování odpovědi ze šablon |

## Skills

| Skill | Popis |
|-------|-------|
| `review-contract` | Kontrola smluv, klasifikace odchylek, návrhy úprav |
| `triage-nda` | Posouzení NDA, klasifikace, směrování |
| `compliance-check` | GDPR, AML, ochrana spotřebitele, zákon č. 39/2020 Sb. |
| `legal-response` | Šablony odpovědí (GDPR, reklamace, AML) |
| `legal-risk-assessment` | Hodnocení rizik závažnost × pravděpodobnost |
| `meeting-briefing` | Příprava na schůzky, akční body |

## MCP Integrace

Plugin se připojuje k nástrojům přes MCP. Viz [CONNECTORS.md](CONNECTORS.md).

| Kategorie | Příklady | Účel |
|-----------|---------|------|
| E-mail | Gmail | Komunikace s klienty a partnery |
| Kalendář | Google Kalendář | Schůzky, lhůty, termíny |
| Úložiště | Google Drive | Smlouvy, dokumenty, šablony |
