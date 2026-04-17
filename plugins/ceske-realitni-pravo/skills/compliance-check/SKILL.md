---
name: compliance-check
description: Kontrola souladu s předpisy pro plánovanou aktivitu nebo obchodní iniciativu v českém právním prostředí. Použij při zpracování osobních údajů klientů, marketingových kampaních, nových obchodních postupech, nebo když potřebuješ vědět, které předpisy a schválení se na aktivitu vztahují.
argument-hint: "<aktivita nebo iniciativa ke kontrole>"
---

# /compliance-check -- Kontrola souladu s předpisy

Kontrola souladu plánované aktivity s českými a EU předpisy.

**Důležité**: Tento nástroj pomáhá s právními pracovními postupy, ale neposkytuje právní poradenství. Vždy ověřuj aktuální znění předpisů.

## Použití

```
/compliance-check $ARGUMENTS
```

## Co potřebuji vědět

Popiš, co plánuješ. Příklady:
- „Chci fotografovat nemovitosti klientů a zveřejňovat je na webu a sociálních sítích"
- „Plánuji zasílat hromadné e-maily potenciálním klientům s nabídkami nemovitostí"
- „Chci ukládat osobní údaje klientů v CRM systému"
- „Plánuji spolupracovat s hypotečním poradcem a sdílet údaje klientů"

## Výstup

```markdown
## Kontrola souladu: [Iniciativa]

### Shrnutí
[Rychlé posouzení: Pokračovat / Pokračovat s podmínkami / Vyžaduje další přezkum]

### Použitelné předpisy
| Předpis | Relevance | Klíčové požadavky |
|---------|-----------|-------------------|
| [předpis] | [jak se vztahuje] | [co je třeba splnit] |

### Požadavky
| # | Požadavek | Stav | Potřebná akce |
|---|-----------|------|---------------|
| 1 | [požadavek] | [Splněno / Nesplněno / Neznámo] | [co udělat] |

### Rizikové oblasti
| Riziko | Závažnost | Zmírnění |
|--------|-----------|----------|
| [riziko] | [Vysoká/Střední/Nízká] | [jak řešit] |

### Doporučené akce
1. [Nejdůležitější akce]
2. [Druhá priorita]

### Potřebná schválení
| Schvalovatel | Proč | Stav |
|-------------|------|------|
| [osoba/orgán] | [důvod] | [čekající] |
```

## Klíčové předpisy pro realitní praxi v ČR

### GDPR a zákon č. 110/2019 Sb. (Ochrana osobních údajů)

**Rozsah**: Zpracování osobních údajů klientů — jména, adresy, kontakty, finanční údaje, fotografie.

**Klíčové povinnosti realitního makléře:**
- **Právní základ zpracování**: Identifikovat zákonný důvod (souhlas, smlouva, oprávněný zájem, zákonná povinnost)
- **Informační povinnost**: Informovat klienty o zpracování jejich údajů (§ 13-14 GDPR)
- **Souhlas se zpracováním**: Získat prokazatelný souhlas, pokud je právním základem souhlas
- **Doba uchování**: Uchovávat údaje pouze po nezbytně nutnou dobu
- **Práva subjektů údajů**: Přístup, oprava, výmaz, přenositelnost, námitka, omezení zpracování
- **Ohlášení porušení**: Oznámit ÚOOÚ do 72 hodin od zjištění porušení zabezpečení
- **Zpracovatelská smlouva**: Uzavřít s externími zpracovateli (IT systémy, cloudové služby)
- **Záznam o činnostech zpracování**: Vést záznamy dle čl. 30 GDPR

**Lhůty pro odpověď na žádosti subjektů údajů:**
- Bez zbytečného odkladu, nejpozději do 1 měsíce
- Prodloužení o 2 měsíce u složitých žádostí (s oznámením)

**Dozorový orgán**: Úřad pro ochranu osobních údajů (ÚOOÚ), www.uoou.cz

### Zákon č. 39/2020 Sb. (O realitním zprostředkování)

**Klíčové povinnosti:**
- Písemná zprostředkovatelská smlouva (§ 9)
- Pojištění profesní odpovědnosti (§ 7)
- Informační povinnosti vůči zájemci (§ 11)
- Povinnost úschovy finančních prostředků (§ 4)
- Zákaz požadování odměny předem (§ 10 odst. 3)
- Bezúhonnost a odborná způsobilost (§ 5-6)

### Zákon č. 253/2008 Sb. (AML — Proti praní špinavých peněz)

**Rozsah**: Realitní zprostředkovatelé jsou povinnými osobami.

**Klíčové povinnosti:**
- **Identifikace klienta**: Ověřit totožnost klienta u transakcí nad 1 000 EUR (§ 7)
- **Kontrola klienta**: U transakcí nad 15 000 EUR provést hloubkovou kontrolu (§ 8-9)
- **Oznámení podezřelých obchodů**: Hlásit podezřelé transakce FAÚ (§ 18)
- **Uchovávání údajů**: 10 let od uskutečnění obchodu (§ 16)
- **Vnitřní systém zásad**: Zpracovat a uplatňovat vnitřní předpisy (§ 21)
- **Školení zaměstnanců**: Pravidelné školení AML (§ 23)

### Zákon č. 634/1992 Sb. (Ochrana spotřebitele)

**Relevance**: Klient-spotřebitel má zvýšenou ochranu.
- Zákaz nekalých obchodních praktik (§ 4-5)
- Povinnost informovat o ceně služby (§ 12-13)
- Právo na odstoupení u smluv uzavřených distančně — 14 dnů (§ 1829 OZ)
- Zákaz klamavé reklamy (§ 2977 OZ)

### Zákon č. 235/2004 Sb. (DPH)

**Relevance pro realitní transakce:**
- Převod nemovitostí — osvobození od DPH po 5 letech od kolaudace/prvního užívání (§ 56)
- Nájem nemovitostí — osvobozeno od DPH (s výjimkami, § 56a)
- Zprostředkovatelská provize — podléhá DPH (21 %)

### Zákon o daních z příjmů (č. 586/1992 Sb.)

**Relevance:**
- Osvobození příjmu z prodeje nemovitosti po 10 letech vlastnictví (§ 4 odst. 1 písm. b)
- Příjem z prodeje bytové potřeby — osvobozeno po 2 letech bydlení (za splnění podmínek)
- Oznamovací povinnost u osvobozených příjmů nad 5 mil. Kč

## Kontrolní seznam pro zpracování osobních údajů (GDPR)

### Povinné prvky

- [ ] **Právní základ identifikován**: Souhlas / plnění smlouvy / oprávněný zájem / zákonná povinnost
- [ ] **Informační doložka**: Klient informován o zpracování (kdo, proč, jak dlouho, práva)
- [ ] **Souhlas získán**: Pokud je základem souhlas — prokazatelný, svobodný, konkrétní
- [ ] **Zpracovatelská smlouva**: S každým externím zpracovatelem (IT, cloud, marketing)
- [ ] **Záznam o činnostech**: Veden záznam dle čl. 30 GDPR
- [ ] **Zabezpečení**: Přiměřená technická a organizační opatření
- [ ] **Doba uchování**: Definována a dodržována
- [ ] **Práva subjektů**: Proces pro vyřizování žádostí subjektů údajů
- [ ] **Oznamovací povinnost**: Proces pro oznámení porušení ÚOOÚ do 72 hodin

### Specifické pro realitní praxi

- [ ] **Fotografie nemovitostí**: Souhlas vlastníka, pozor na zachycení třetích osob
- [ ] **Prohlídky nemovitostí**: Záznam účastníků prohlídek — právní základ
- [ ] **Sdílení s hypotečními poradci**: Zpracovatelská smlouva nebo společné správcovství
- [ ] **Inzerce**: Soulad s GDPR u zveřejňování údajů o nemovitostech
- [ ] **CRM systém**: Zpracovatelská smlouva s poskytovatelem, zabezpečení přístupu
- [ ] **E-mailový marketing**: Souhlas dle zákona č. 480/2004 Sb. (obchodní sdělení)

## Tipy

1. **Buď konkrétní** — „Chci poslat newsletter klientům" je lepší než „marketingová kampaň"
2. **Uveď geografii** — U přeshraničních transakcí se požadavky liší
3. **Zmiň data** — Jaké osobní údaje jsou zapojeny? To určuje většinu compliance požadavků
4. **Mysli na AML** — U každé transakce zvažuj povinnosti identifikace klienta
