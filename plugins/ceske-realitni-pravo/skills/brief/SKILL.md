---
name: brief
description: Generování kontextových briefingů pro právní práci — denní přehled, výzkum tématu, nebo reakce na incident. Použij na začátku dne pro přehled právně relevantních položek přes e-mail, kalendář a smlouvy, při výzkumu konkrétní právní otázky, nebo při vývoji situace vyžadující rychlý kontext.
argument-hint: "[denni | tema <dotaz> | incident]"
---

# /brief -- Právní briefing

Generuj kontextové briefingy pro právní práci v realitní praxi.

**Důležité**: Pomáhá s právními pracovními postupy, ale neposkytuje právní poradenství.

## Použití

```
/brief denni              # Ranní přehled právně relevantních položek
/brief tema [dotaz]       # Výzkumný briefing na konkrétní téma
/brief incident [tema]    # Rychlý briefing k vyvíjející se situaci
```

## Režimy

### Denní briefing

Ranní shrnutí všeho, co realitní makléř potřebuje vědět.

#### Zdroje ke kontrole

**E-mail (pokud připojen):**
- Nové požadavky na smlouvy nebo jejich kontrolu
- Odpovědi protistran na probíhající jednání
- Dotazy klientů vyžadující právní posouzení
- Komunikace s advokáty
- Oznámení od regulátorů (ÚOOÚ, ČOI)

**Kalendář (pokud připojen):**
- Dnešní schůzky vyžadující právní přípravu (prohlídky, podpisy, jednání)
- Blížící se lhůty tento týden (expirace smluv, lhůty pro odpovědi)
- Termíny na katastru

**Chat (pokud připojen):**
- Zprávy v kanálech RE/MAX kanceláře
- Přímé zprávy vyžadující právní vstup

#### Výstup

```
## Denní právní přehled — [Datum]

### Urgentní / Vyžaduje akci
[Položky vyžadující okamžitou pozornost]

### Smlouvy v procesu
- **Čekají na kontrolu**: [počet a seznam]
- **Čekají na protistranu**: [počet a seznam]
- **Blížící se lhůty**: [tento týden]

### Nové požadavky
[Žádosti o smlouvy, NDA, compliance dotazy]

### Dnešní kalendář
[Schůzky s právní relevancí a potřebná příprava]

### Lhůty tento týden
[Blížící se termíny a lhůty]

### Nedostupné zdroje
[Zdroje, které nebyly připojeny]
```

### Tematický briefing

Výzkum na konkrétní právní téma s použitím dostupných zdrojů.

#### Výstup

```
## Tematický briefing: [Téma]

### Shrnutí
[2-3 věty]

### Kontext
[Historie a pozadí z interních zdrojů]

### Aktuální stav
[Současná pozice nebo přístup]

### Klíčové aspekty
[Důležité faktory, rizika, otevřené otázky]

### Relevantní české předpisy
[Občanský zákoník, zákon č. 39/2020 Sb., GDPR, apod.]

### Mezery
[Chybějící informace]

### Doporučené další kroky
[Co dělat s těmito informacemi]
```

### Incident briefing

Rychlý briefing pro situace vyžadující okamžitou pozornost (stížnost klienta, porušení ochrany dat, hrozba soudu).

#### Výstup

```
## Incident briefing: [Téma]
**Připraveno**: [čas]
**Závažnost**: [posouzení]

### Shrnutí situace
[Co je známo o incidentu]

### Časová osa
[Chronologické shrnutí]

### Okamžité právní aspekty
[Lhůty pro oznámení, povinnost zachování důkazů, privilegované aspekty]

### Relevantní smlouvy
[Smlouvy, pojištění, další dohody]

### Klíčové kontakty
[Interní i externí kontakty]

### Doporučené okamžité akce
1. [Nejurgentnejší akce]
2. [Druhá priorita]

### Informační mezery
[Co zatím není známo]
```

## Poznámky

- Briefingy by měly být akční — každá položka má jasný další krok
- Při zmínce o lhůtách vždy uveď konkrétní datum a právní základ
- U incidentů s porušením ochrany dat okamžitě připomeň 72hodinovou lhůtu pro oznámení ÚOOÚ
