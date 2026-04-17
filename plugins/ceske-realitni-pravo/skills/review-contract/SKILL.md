---
name: review-contract
description: Kontrola smlouvy podle českého práva a interního playbooku — identifikace odchylek, návrh úprav, analýza obchodního dopadu. Použij při kontrole zprostředkovatelských, kupních, rezervačních smluv, smluv o budoucí smlouvě nebo jakýchkoli jiných smluv v realitní praxi.
argument-hint: "<soubor smlouvy nebo text>"
---

# /review-contract -- Kontrola smlouvy podle českého práva

> Pokud vidíš neznámé zástupné symboly nebo potřebuješ ověřit připojené nástroje, viz [CONNECTORS.md](../../CONNECTORS.md).

Kontrola smlouvy podle českého právního rámce a interního playbooku organizace. Analýza jednotlivých ustanovení, identifikace odchylek, návrh úprav a analýza obchodního dopadu.

**Důležité**: Tento nástroj pomáhá s právními pracovními postupy, ale neposkytuje právní poradenství. Veškeré analýzy by měly být přezkoumány kvalifikovaným právníkem (advokátem) před tím, než se na ně spoléháte.

## Použití

```
/review-contract <soubor smlouvy nebo URL>
```

Zkontroluj smlouvu: @$1

## Právní rámec České republiky

Kontrola smluv vychází z následujících klíčových předpisů:

| Předpis | Číslo | Oblast |
|---------|-------|--------|
| **Občanský zákoník** | zákon č. 89/2012 Sb. | Obecná smluvní úprava, kupní smlouva, nájem, zprostředkování |
| **Zákon o realitním zprostředkování** | zákon č. 39/2020 Sb. | Povinnosti realitního zprostředkovatele, smlouva o zprostředkování |
| **Katastrální zákon** | zákon č. 256/2013 Sb. | Zápis vlastnických práv, věcná břemena |
| **Zákon o ochraně spotřebitele** | zákon č. 634/1992 Sb. | Ochrana kupujících-spotřebitelů |
| **GDPR / Zákon o zpracování osobních údajů** | nařízení (EU) 2016/679, zákon č. 110/2019 Sb. | Ochrana osobních údajů klientů |
| **Zákon o DPH** | zákon č. 235/2004 Sb. | Daňové aspekty realitních transakcí |
| **Zákon o AML** | zákon č. 253/2008 Sb. | Povinnosti identifikace klientů |

## Pracovní postup

### Krok 1: Přijetí smlouvy

Přijmi smlouvu v libovolném formátu:
- **Nahrání souboru**: PDF, DOCX nebo jiný formát dokumentu
- **URL**: Odkaz na smlouvu v cloudovém úložišti (Google Drive apod.)
- **Vložený text**: Text smlouvy vložený přímo do konverzace

Pokud smlouva není poskytnuta, požádej uživatele o její dodání.

### Krok 2: Zjištění kontextu

Zeptej se uživatele na kontext před zahájením kontroly:

1. **Typ smlouvy**: Zprostředkovatelská smlouva, kupní smlouva, rezervační smlouva, smlouva o budoucí smlouvě, nájemní smlouva, jiná?
2. **Na které straně jsi?** (zprostředkovatel, prodávající, kupující, pronajímatel, nájemce)
3. **Termín**: Kdy je potřeba smlouvu finalizovat?
4. **Oblasti zájmu**: Jsou nějaké specifické obavy? (např. „chci ošetřit odpovědnost za vady", „klíčová je úschova kupní ceny")
5. **Kontext obchodu**: Relevantní obchodní kontext (hodnota transakce, strategický význam, existující vztah)

### Krok 3: Načtení playbooku

Hledej interní playbook pro kontrolu smluv v lokálních nastaveních (např. `legal.local.md`).

Playbook by měl definovat:
- **Standardní pozice**: Preferované smluvní podmínky
- **Přijatelné rozmezí**: Podmínky, které lze akceptovat bez eskalace
- **Eskalační kritéria**: Podmínky vyžadující kontrolu advokátem

**Pokud není playbook nastaven:**
- Informuj uživatele, že nebyl nalezen playbook
- Nabídni dvě možnosti:
  1. Pomoc s nastavením playbooku (definování pozic pro klíčová ustanovení)
  2. Pokračování s generickou kontrolou podle českého práva a obvyklé realitní praxe
- Při generické kontrole jasně uveď, že se jedná o kontrolu podle obecných standardů

### Krok 4: Analýza jednotlivých ustanovení

#### Typy smluv v realitní praxi

##### A. Zprostředkovatelská smlouva (§ 2445-2454 OZ, zákon č. 39/2020 Sb.)

| Ustanovení | Klíčové kontrolní body |
|-----------|----------------------|
| **Vymezení činnosti** | Jasný popis zprostředkovatelské činnosti, exkluzivita vs. neexkluzivita |
| **Provize** | Výše, splatnost, podmínky vzniku nároku na provizi |
| **Doba trvání** | Určitá/neurčitá, výpovědní lhůta, maximální doba trvání |
| **Povinnosti zprostředkovatele** | Povinnost informovat, loajalita, péče řádného odborníka |
| **Úschova finančních prostředků** | Způsob úschovy (advokátní, notářská, bankovní), podmínky uvolnění |
| **Výhradní zastoupení** | Podmínky exkluzivity, důsledky porušení, kompenzace |
| **Odpovědnost za vady** | Informační povinnost o vadách nemovitosti |
| **GDPR souhlas** | Zpracování osobních údajů klientů |
| **Odstoupení spotřebitele** | 14 dnů u smluv uzavřených distančně (§ 1829 OZ) |

**Specifické požadavky zákona č. 39/2020 Sb.:**
- Smlouva musí být v písemné formě (§ 9)
- Zprostředkovatel musí mít pojištění profesní odpovědnosti (§ 7)
- Informační povinnosti vůči zájemci před uzavřením smlouvy (§ 11)
- Povinnost provést úschovu finančních prostředků (§ 4)
- Zákaz požadování odměny předem (§ 10 odst. 3)

##### B. Rezervační smlouva

| Ustanovení | Klíčové kontrolní body |
|-----------|----------------------|
| **Předmět rezervace** | Přesná identifikace nemovitosti (list vlastnictví, parcela) |
| **Rezervační poplatek** | Výše, započitatelnost na kupní cenu, podmínky vrácení |
| **Doba rezervace** | Přiměřená lhůta pro uzavření kupní smlouvy |
| **Podmínky pro vrácení** | Kdy má kupující nárok na vrácení zálohy |
| **Sankce za neuzavření** | Smluvní pokuta, propadnutí zálohy — přiměřenost |
| **Identifikace stran** | Správné údaje prodávajícího i kupujícího |

##### C. Kupní smlouva na nemovitost (§ 2079-2183 OZ)

| Ustanovení | Klíčové kontrolní body |
|-----------|----------------------|
| **Identifikace nemovitosti** | Číslo LV, katastrální území, parcely, popis nemovitosti |
| **Kupní cena a způsob úhrady** | Výše, úschova (advokátní/notářská/bankovní), podmínky uvolnění |
| **Předání nemovitosti** | Termín předání, předávací protokol, stav nemovitosti |
| **Prohlášení prodávajícího** | Absence právních vad, absence faktických vad, žádné dluhy/zástavy |
| **Odpovědnost za vady** | Zjevné a skryté vady, lhůta pro uplatnění (§ 2129 OZ — 5 let) |
| **Návrh na vklad** | Kdo podává, kdy, podmínky pro podání |
| **Věcná břemena a zástavy** | Aktuální stav zapsaný v katastru, podmínky výmazu |
| **Daňové povinnosti** | Osvobození od daně z příjmu (§ 4 ZDP), DPH aspekty |
| **Smluvní pokuta** | Přiměřenost, jednostrannost, kumulace |
| **Odstoupení od smlouvy** | Podmínky, lhůty, důsledky |
| **Rozhodné právo** | České právo |

##### D. Smlouva o budoucí kupní smlouvě (§ 1785-1788 OZ)

| Ustanovení | Klíčové kontrolní body |
|-----------|----------------------|
| **Podstatné náležitosti budoucí smlouvy** | Musí obsahovat alespoň obecné vymezení obsahu budoucí smlouvy |
| **Lhůta pro uzavření** | Přiměřená lhůta, následky marného uplynutí |
| **Podmínky uzavření** | Odkládací podmínky (např. schválení hypotéky) |
| **Záloha / blokovací depozit** | Výše, podmínky vrácení |
| **Změna okolností** | § 1788 OZ — právo odmítnout uzavření při podstatné změně okolností |

##### E. Nájemní smlouva (§ 2201-2331 OZ)

| Ustanovení | Klíčové kontrolní body |
|-----------|----------------------|
| **Předmět nájmu** | Přesná identifikace bytu/prostoru |
| **Nájemné a služby** | Výše, splatnost, způsob úhrady, vyúčtování služeb |
| **Kauce / jistota** | Max. 3 měsíce nájemného (§ 2254 OZ), podmínky vrácení |
| **Doba nájmu** | Určitá/neurčitá, výpovědní důvody a lhůty |
| **Práva nájemce** | Ochrana nájemce bytu, zákaz zkracování práv (§ 2235 OZ) |
| **Údržba a opravy** | Drobné opravy (NV č. 308/2015 Sb.) vs. ostatní |
| **Podnájem** | Podmínky, souhlas pronajímatele |

### Krok 5: Klasifikace odchylek

#### ZELENÁ — Přijatelné

Ustanovení odpovídá standardní pozici nebo je výhodnější.

**Příklady:**
- Provize zprostředkovatele v obvyklém rozmezí 3-5 % z kupní ceny
- Úschova kupní ceny u renomovaného advokáta nebo notáře
- Odpovědnost za vady v souladu s § 2129 OZ

**Akce**: Poznamenat pro informaci. Není třeba vyjednávat.

#### ŽLUTÁ — Vyjednávat

Ustanovení je mimo standardní pozici, ale v rámci vyjednávacího rozmezí.

**Příklady:**
- Exkluzivní zastoupení na dobu delší než 3 měsíce
- Smluvní pokuta na horní hranici přiměřenosti
- Rezervační poplatek nad 5 % kupní ceny
- Omezená odpovědnost za skryté vady

**Akce**: Navrhnout konkrétní úpravy. Poskytnout záložní pozici. Odhadnout dopad.

#### ČERVENÁ — Eskalovat

Ustanovení je mimo přijatelný rozsah, porušuje právní předpisy, nebo představuje zásadní riziko.

**Příklady:**
- Nepřiměřená smluvní pokuta (rozpor s dobrými mravy, § 580 OZ)
- Chybějící úschova kupní ceny (přímá platba prodávajícímu bez zajištění)
- Zkracování práv spotřebitele v rozporu se zákonem
- Porušení povinností dle zákona č. 39/2020 Sb.
- Nepřiměřeně dlouhá exkluzivita bez možnosti ukončení
- Neplatné vzdání se práv dle kogentních ustanovení OZ

**Akce**: Vysvětlit riziko. Doporučit standardní alternativní znění. Doporučit konzultaci s advokátem.

### Krok 6: Návrhy úprav

Pro každou ŽLUTOU a ČERVENOU odchylku uveď:

```
**Ustanovení**: [odkaz na článek a název]
**Aktuální znění**: "[přesná citace ze smlouvy]"
**Navrhovaná úprava**: "[konkrétní alternativní znění]"
**Právní základ**: [odkaz na relevantní ustanovení OZ, zákona č. 39/2020 Sb. apod.]
**Odůvodnění**: [1-2 věty vysvětlující proč]
**Priorita**: [Nutnost / Silná preference / Výhoda]
**Záložní pozice**: [alternativní pozice]
```

### Krok 7: Shrnutí obchodního dopadu

- **Celkové hodnocení rizika**: Vysokoúrovňový pohled na rizikový profil smlouvy
- **Top 3 problémy**: Nejdůležitější body k řešení
- **Soulad s právními předpisy**: Posouzení souladu s OZ a zákonem č. 39/2020 Sb.
- **Vyjednávací strategie**: Doporučený přístup

#### Prioritní rámec

**Úroveň 1 — Nutnosti (překážky obchodu)**
- Ustanovení porušující kogentní normy OZ nebo zákon č. 39/2020 Sb.
- Chybějící zajištění kupní ceny (úschova)
- Chybějící prohlášení o stavu nemovitosti
- Nepřiměřené smluvní pokuty

**Úroveň 2 — Silné preference**
- Úprava odpovědnosti za vady
- Podmínky exkluzivity
- Podmínky odstoupení od smlouvy
- Výše a podmínky provize

**Úroveň 3 — Ústupky**
- Preferovaná forma úschovy
- Drobné úpravy lhůt
- Formální náležitosti

### Krok 8: Kontrola souladu s katastrem

Doporuč uživateli ověřit:
- Aktuální výpis z katastru nemovitostí (list vlastnictví)
- Absence plomby (probíhající řízení)
- Věcná břemena a zástavní práva
- Poznámky a omezení převodu
- Shoda údajů ve smlouvě s katastrem

## Výstupní formát

```
## Kontrola smlouvy — Shrnutí

**Dokument**: [název/identifikace smlouvy]
**Typ smlouvy**: [zprostředkovatelská / kupní / rezervační / budoucí kupní / nájemní]
**Strany**: [jména stran a role]
**Vaše strana**: [zprostředkovatel / prodávající / kupující / atd.]
**Termín**: [pokud byl uveden]
**Základ kontroly**: [Playbook / Obecné české standardy]

## Klíčová zjištění

[Top 3-5 problémů s barevnými značkami závažnosti]

## Analýza jednotlivých ustanovení

### [Kategorie ustanovení] — [ZELENÁ/ŽLUTÁ/ČERVENÁ]
**Smlouva říká**: [shrnutí ustanovení]
**Standardní pozice**: [váš standard / české právo]
**Odchylka**: [popis rozdílu]
**Právní základ**: [odkaz na relevantní paragraf]
**Obchodní dopad**: [co to prakticky znamená]
**Návrh úpravy**: [konkrétní znění, pokud ŽLUTÁ nebo ČERVENÁ]

[Opakuj pro každé hlavní ustanovení]

## Soulad s právními předpisy

[Posouzení souladu s OZ, zákonem č. 39/2020 Sb. a dalšími předpisy]

## Vyjednávací strategie

[Doporučený přístup, priority, kandidáti na ústupky]

## Další kroky

[Konkrétní akce k provedení]
```

## Poznámky

- Pokud je smlouva v jiném jazyce než češtině, upozorni a zeptej se na postup
- U velmi dlouhých smluv nabídni zaměření na nejpodstatnější části
- Vždy upozorni, že analýza by měla být přezkoumána kvalifikovaným advokátem
- U realitních transakcí vždy doporuč ověření stavu v katastru nemovitostí
- Při kontrole zprostředkovatelských smluv vždy ověř soulad se zákonem č. 39/2020 Sb.
