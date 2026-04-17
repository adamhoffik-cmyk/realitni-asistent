---
name: vendor-check
description: Kontrola stavu existujících smluv s obchodním partnerem (dodavatelem, spolupracujícím subjektem) v připojených systémech — s analýzou mezer a blížících se termínů. Použij při onboardingu nového partnera, kontrole stávajících smluv, nebo zjištění blížících se expirací.
argument-hint: "[jméno partnera]"
---

# /vendor-check -- Stav smluv s partnerem

Kontrola stavu smluv s obchodním partnerem ve všech připojených systémech.

**Důležité**: Pomáhá s právními pracovními postupy, ale neposkytuje právní poradenství.

## Použití

```
/vendor-check [jméno partnera]
```

## Pracovní postup

### Krok 1: Identifikace partnera
Přijmi jméno partnera. Zpracuj varianty (obchodní jméno vs. IČO, zkratky). Ověř v dostupných zdrojích.

### Krok 2: Prohledání systémů
Prohledej připojené zdroje (e-mail, dokumenty, chat) pro smlouvy a komunikaci s partnerem.

### Krok 3: Sestavení přehledu smluv

Pro každou nalezenou smlouvu uveď:
- Typ smlouvy (NDA, smlouva o spolupráci, zprostředkovatelská, rámcová, zpracovatelská GDPR)
- Stav (aktivní, expirovaná, ve vyjednávání)
- Datum účinnosti a expirace
- Klíčové podmínky
- Dodatky

### Krok 4: Analýza mezer

```
## Pokrytí smlouvami

[OK] NDA / Dohoda o mlčenlivosti — [stav]
[OK/CHYBÍ] Smlouva o spolupráci — [stav]
[OK/CHYBÍ] Zpracovatelská smlouva (GDPR) — [stav]
[OK/CHYBÍ] Pojištění — [stav]
```

Upozorni na mezery, např. chybějící zpracovatelská smlouva pokud partner zpracovává osobní údaje klientů.

### Krok 5: Výstup

```
## Stav smluv s partnerem: [Jméno]

**Datum kontroly**: [datum]
**Prohledané zdroje**: [seznam]
**Nedostupné zdroje**: [seznam]

## Přehled vztahu
**Partner**: [obchodní jméno, IČO]
**Typ vztahu**: [dodavatel / spolupracovník / partner]

## Shrnutí smluv

### [Typ smlouvy] — [Stav]
- **Účinnost**: [datum]
- **Expirace**: [datum]
- **Klíčové podmínky**: [shrnutí]
- **Umístění**: [kde je uložena]

## Analýza mezer
[Co je pokryto vs. co může chybět]

## Blížící se akce
- [Blížící se expirace nebo obnovení]
- [Chybějící smlouvy k uzavření]

## Poznámky
[Relevantní kontext z e-mailu/chatu]
```

## Specifické pro realitní praxi

V kontextu realitního zprostředkování typicky kontroluj:
- **Spolupracující makléři**: Dohoda o spolupráci, dělení provize
- **Advokátní kancelář**: Smlouva o poskytování právních služeb, podmínky úschovy
- **Hypoteční poradci**: Smlouva o spolupráci, zpracovatelská smlouva GDPR
- **Fotografové/staging**: Smlouva o dílo, licence k fotografiím, GDPR
- **IT dodavatelé**: Smlouva o poskytování služeb, zpracovatelská smlouva GDPR
- **Pojišťovna**: Pojištění profesní odpovědnosti (povinné dle § 7 zákona č. 39/2020 Sb.)
