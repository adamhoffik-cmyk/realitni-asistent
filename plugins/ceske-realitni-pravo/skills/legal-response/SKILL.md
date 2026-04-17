---
name: legal-response
description: Generování odpovědi na běžný právní dotaz pomocí šablon, s kontrolou eskalačních kritérií. Použij při odpovídání na žádosti o přístup k osobním údajům, dotazy klientů, žádosti obchodních partnerů o NDA, nebo jiné běžné právní dotazy v realitní praxi.
argument-hint: "[typ dotazu]"
---

# /legal-response -- Generování odpovědi ze šablon

Generuj odpověď na běžný právní dotaz s přizpůsobením pro české prostředí.

**Důležité**: Tento nástroj pomáhá s právními pracovními postupy, ale neposkytuje právní poradenství. Odpovědi by měly být přezkoumány kvalifikovaným advokátem.

## Použití

```
/legal-response [typ dotazu]
```

Typy dotazů:
- `gdpr` nebo `osobni-udaje` — Žádosti subjektů údajů (přístup, výmaz, oprava)
- `nda` nebo `mlcenlivost` — Žádosti o dohodu o mlčenlivosti
- `reklamace` — Reklamace služeb zprostředkovatele
- `stiznost` — Stížnosti klientů
- `obchodni-sdeleni` — Marketingová sdělení a souhlas
- `aml` — AML identifikace a podezřelé transakce
- `vlastni` — Vlastní šablona

## Pracovní postup

### Krok 1: Identifikace typu dotazu

Přijmi typ dotazu od uživatele. Pokud je nejednoznačný, ukaž dostupné kategorie.

### Krok 2: Načtení šablony

Hledej šablony v `legal.local.md`. Pokud nejsou, nabídni vytvoření nebo použij výchozí strukturu.

### Krok 3: Kontrola eskalačních kritérií

Před generováním odpovědi ověř, zda situace nevyžaduje individuální přístup.

#### Obecná eskalační kritéria
- Hrozba soudního řízení nebo regulačního šetření
- Dotaz od regulátora (ÚOOÚ, ČOI, FAÚ) nebo soudu
- Odpověď by mohla vytvořit právní závazek
- Mediální pozornost
- Více jurisdikcí

#### Eskalace u žádostí subjektů údajů (GDPR)
- Žádost se týká údajů nezletilého
- Žádost od ÚOOÚ
- Údaje jsou předmětem soudního řízení
- Žadatel je v aktivním sporu
- Neobvykle široký rozsah žádosti
- Zvláštní kategorie údajů (zdravotní, biometrické)

#### Eskalace u reklamací a stížností
- Klient hrozí soudním řízením
- Stížnost na ČOI nebo jinou instituci
- Škoda přesahující pojistné krytí
- Mediální zájem

**Při detekci eskalace:**
1. **Zastav**: Negeneruj šablonovou odpověď
2. **Upozorni**: Informuj o detekovaném eskalačním kritériu
3. **Doporuč**: Navrhni konzultaci s advokátem
4. **Nabídni**: Připrav návrh k přezkumu advokátem (označený „NÁVRH — K PŘEZKUMU ADVOKÁTEM")

### Krok 4: Shromáždění detailů

#### Žádost subjektu údajů (GDPR):
- Jméno žadatele a kontakt
- Typ žádosti (přístup, výmaz, oprava, přenositelnost, námitka)
- Jaké údaje se týká
- Lhůta pro odpověď (30 dní od přijetí)

#### Reklamace služeb:
- Jméno klienta
- Číslo smlouvy
- Popis reklamace
- Relevantní smluvní ustanovení

#### NDA žádost:
- Žadatel a organizace
- Protistrana
- Účel NDA
- Vzájemná nebo jednostranná

### Krok 5: Generování odpovědi

Přizpůsob šablonu s konkrétními údaji. Zajisti:
- Profesionální tón v češtině
- Všechny právně požadované náležitosti
- Odkaz na konkrétní data, lhůty a povinnosti
- Jasné další kroky

## Kategorie odpovědí

### 1. Žádosti subjektů údajů (GDPR)

**Podkategorie**: Potvrzení přijetí, žádost o ověření totožnosti, vyřízení žádosti, částečné zamítnutí, zamítnutí.

**Klíčové prvky šablony:**
- Odkaz na GDPR a zákon č. 110/2019 Sb.
- Lhůta 30 dní (prodloužení o 60 dní s oznámením)
- Práva subjektu údajů včetně práva podat stížnost k ÚOOÚ
- Kontaktní údaje správce

**Příklad struktury:**
```
Předmět: Vaše žádost o [přístup/výmaz/opravu] osobních údajů — Ref. {{id_zadosti}}

Vážený/á {{jmeno_zadatele}},

potvrzujeme přijetí Vaší žádosti ze dne {{datum_zadosti}} o [přístup k / výmaz / opravu] Vašich osobních údajů dle nařízení (EU) 2016/679 (GDPR).

[Potvrzení / žádost o ověření / vyřízení / zamítnutí s odůvodněním]

Na Vaši žádost odpovíme nejpozději do {{lhuta_odpovedi}}.

Máte právo podat stížnost k Úřadu pro ochranu osobních údajů (www.uoou.cz).

S pozdravem,
{{podpis}}
```

### 2. Reklamace a stížnosti klientů

**Podkategorie**: Potvrzení přijetí, vyřízení reklamace, zamítnutí s odůvodněním.

**Klíčové prvky:**
- Odkaz na příslušnou smlouvu
- Zákon o ochraně spotřebitele č. 634/1992 Sb.
- Občanský zákoník č. 89/2012 Sb.
- Poučení o možnosti řešení sporu (ČOI, soud)

### 3. Obchodní sdělení (marketing)

**Klíčové prvky:**
- Zákon č. 480/2004 Sb. o některých službách informační společnosti
- Prokazatelný souhlas příjemce
- Možnost odhlášení (opt-out)
- Identifikace odesílatele

### 4. AML odpovědi

**Klíčové prvky:**
- Zákon č. 253/2008 Sb.
- Povinnost identifikace — nelze odmítnout klienta bez identifikace
- Povinnost mlčenlivosti o oznámení podezřelého obchodu (§ 38)
- Spolupráce s FAÚ

## Výstupní formát

```
## Vygenerovaná odpověď: [Typ dotazu]

**Komu**: [příjemce]
**Předmět**: [předmět]

---

[Text odpovědi]

---

### Kontrola eskalace
[Potvrzení, že nebyla detekována eskalační kritéria, NEBO označené kritérium s doporučením]

### Následné akce
1. [Akce po odeslání]
2. [Kalendářní připomínky]
3. [Evidence]
```

## Poznámky

- Vždy prezentuj návrh k přezkumu uživatelem
- U regulovaných odpovědí (GDPR, AML) vždy uveď příslušnou lhůtu
- Šablony by měly být pravidelně aktualizovány při změnách legislativy
- V realitní praxi zvažuj specifika zákona č. 39/2020 Sb.
