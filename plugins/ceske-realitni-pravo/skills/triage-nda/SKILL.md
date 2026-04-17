---
name: triage-nda
description: Rychlé posouzení příchozí dohody o mlčenlivosti (NDA) a klasifikace jako ZELENÁ (standardní schválení), ŽLUTÁ (kontrola právníkem), nebo ČERVENÁ (plný právní přezkum). Použij při příchodu nové NDA od obchodního partnera, při kontrole dohod o mlčenlivosti s klienty, nebo při posouzení dohod o ochraně důvěrných informací.
argument-hint: "<soubor NDA nebo text>"
---

# /triage-nda -- Posouzení dohody o mlčenlivosti

Posuď NDA: @$1

Rychlé posouzení příchozí dohody o mlčenlivosti podle českého práva.

**Důležité**: Tento nástroj pomáhá s právními pracovními postupy, ale neposkytuje právní poradenství.

## Právní rámec

- **Občanský zákoník (zákon č. 89/2012 Sb.)** — obecná smluvní úprava, ochrana obchodního tajemství (§ 504)
- **Zákon o ochraně obchodního tajemství (zákon č. 221/2016 Sb.)**
- **GDPR a zákon č. 110/2019 Sb.** — pokud NDA zahrnuje osobní údaje

## Pracovní postup

### Krok 1: Přijetí NDA

Přijmi NDA v libovolném formátu: soubor, URL, nebo vložený text.

### Krok 2: Načtení standardních kritérií

Hledej kritéria v `legal.local.md`. Výchozí: vzájemné povinnosti, 2-3 roky, standardní výjimky, české právo, žádné konkurenční doložky.

### Krok 3: Rychlá kontrola

#### 1. Struktura dohody
- [ ] Typ identifikován (vzájemná / jednostranná)
- [ ] Vhodnost pro kontext
- [ ] Samostatná dohoda

#### 2. Definice důvěrných informací
- [ ] Přiměřený rozsah
- [ ] Výjimky přítomny
- [ ] Bez problematických inkluzí

#### 3. Povinnosti přijímající strany
- [ ] Přiměřený standard péče
- [ ] Omezení použití na stanovený účel
- [ ] Omezení sdělování

#### 4. Standardní výjimky (musí být přítomny)
- [ ] Veřejně dostupné informace
- [ ] Předchozí znalost
- [ ] Nezávislý vývoj
- [ ] Třetí strana bez omezení
- [ ] Zákonná povinnost (s oznámením)

#### 5. Doba trvání
- [ ] Přiměřená (1-3 roky standard)
- [ ] Přežití povinností (2-5 let)
- [ ] Ne na věčnost

#### 6. Nápravné prostředky
- [ ] Smluvní pokuta přiměřená (§ 2048-2052 OZ)
- [ ] Symetrie u vzájemných NDA

#### 7. Problematická ustanovení
- [ ] Žádný zákaz přetahování zaměstnanců
- [ ] Žádná konkurenční doložka
- [ ] Žádné postoupení IP
- [ ] Přiměřená smluvní pokuta (ne v rozporu s dobrými mravy, § 580 OZ)

#### 8. Rozhodné právo
- [ ] České právo
- [ ] České soudy
- [ ] Bez povinné arbitráže

### Krok 4: Klasifikace

#### ZELENÁ — Standardní schválení
Vše v pořádku: vzájemná, výjimky přítomny, přiměřená doba, české právo, žádné problematické doložky.

#### ŽLUTÁ — Kontrola právníkem
Drobné problémy: širší definice, delší doba (5-7 let), chybí jedna výjimka, zahraniční právo v rámci EU, drobná asymetrie.

#### ČERVENÁ — Zásadní problémy
Závažné: chybějící klíčové výjimky, konkurenční doložka v NDA, nepřiměřená smluvní pokuta, neomezená doba, skryté IP ustanovení, problematická jurisdikce mimo EU.

### Krok 5: Zpráva

```
## Zpráva z posouzení NDA

**Klasifikace**: [ZELENÁ / ŽLUTÁ / ČERVENÁ]
**Strany**: [jména]
**Typ**: [Vzájemná / Jednostranná]
**Doba trvání**: [délka]
**Rozhodné právo**: [jurisdikce]

## Výsledky kontroly

| Kritérium | Stav | Poznámky |
|-----------|------|----------|
| ... | [OK/POZOR/PROBLÉM] | ... |

## Zjištěné problémy

### [Problém — ŽLUTÁ/ČERVENÁ]
**Co**: [popis]
**Riziko**: [co se může stát]
**Právní základ**: [§ OZ]
**Návrh řešení**: [znění]

## Doporučení
[Další krok]
```

## Poznámky

- Vždy ověř soulad s dobrými mravy u smluvních pokut
- U NDA v realitní praxi zvažuj specifika zákona č. 39/2020 Sb.
- Upozorni, že advokát by měl přezkoumat sporné body
