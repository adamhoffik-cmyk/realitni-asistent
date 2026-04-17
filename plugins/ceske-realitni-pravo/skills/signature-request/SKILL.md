---
name: signature-request
description: Příprava a směrování dokumentu k podpisu — kontrola před podpisem, konfigurace pořadí podpisů a odeslání k provedení. Použij když je smlouva finalizována a připravena k podpisu, při ověřování správnosti údajů stran a podpisových bloků, nebo při nastavení elektronického či klasického podpisu.
argument-hint: "<dokument nebo smlouva k podpisu>"
---

# /signature-request -- Směrování k podpisu

Příprava dokumentu k podpisu — ověření kompletnosti, nastavení pořadí podpisů a směrování k provedení.

**Důležité**: Pomáhá s právními pracovními postupy, ale neposkytuje právní poradenství. Ověřte, že dokument je ve finální podobě.

## Použití

```
/signature-request $ARGUMENTS
```

Připrav k podpisu: @$1

## Pracovní postup

### Krok 1: Přijetí dokumentu

Přijmi dokument v libovolném formátu: soubor (PDF, DOCX), URL (Google Drive), nebo odkaz.

### Krok 2: Kontrola před podpisem

```markdown
## Kontrola před podpisem

- [ ] Dokument je ve finální dohodnuté podobě (žádné otevřené redline)
- [ ] Všechny přílohy a dodatky jsou připojeny
- [ ] Správné právní údaje stran (jméno/název, IČO, sídlo/bydliště)
- [ ] Podpisové bloky odpovídají oprávněným osobám
- [ ] Data jsou správná nebo ponechána pro datum podpisu
- [ ] Interní schválení bylo získáno (pokud potřeba)
- [ ] Dokument byl zkontrolován advokátem (pokud potřeba)
- [ ] U nemovitostních smluv: údaje odpovídají katastru nemovitostí
```

**Specifické pro české realitní smlouvy:**
- [ ] Kupní smlouva na nemovitost — ověřené podpisy na návrhu na vklad do katastru
- [ ] Správné katastrální údaje (LV, katastrální území, parcely)
- [ ] Úschovní smlouva — připravena současně s kupní smlouvou
- [ ] Plná moc — úředně ověřená, pokud se podepisuje v zastoupení

### Krok 3: Konfigurace podpisů

Zjisti:
- **Podepisující**: Kdo podepisuje? (jména, kontakty, role)
- **Pořadí**: Sekvenční nebo paralelní?
- **Forma podpisu**: Elektronický, vlastnoruční, úředně ověřený?
- **Kopie**: Kdo obdrží kopii podepsaného dokumentu?

**Poznámka k formě podpisu v ČR:**
- **Kupní smlouva na nemovitost**: Podpisy na návrhu na vklad musí být úředně ověřeny (notář nebo CzechPOINT)
- **Zprostředkovatelská smlouva**: Písemná forma povinná (§ 9 zákona č. 39/2020 Sb.), elektronický podpis přípustný
- **NDA**: Prostý podpis obvykle postačuje
- **Plná moc k právním úkonům**: Úředně ověřený podpis

### Krok 4: Směrování k podpisu

**Pokud je připojen e-podpis (DocuSign apod.):**
- Vytvořit obálku/žádost o podpis
- Nastavit podpisová pole a pořadí
- Odeslat k podpisu

**Pokud není připojen:**
- Vygenerovat pokyny k podpisu
- Připravit dokument pro klasický podpis
- Seznam všech podepisujících s kontakty

## Výstup

```markdown
## Žádost o podpis: [Název dokumentu]

### Detaily dokumentu
- **Typ**: [Kupní smlouva / Zprostředkovatelská / NDA / apod.]
- **Strany**: [Strana A] a [Strana B]
- **Stran dokumentu**: [X]

### Kontrola před podpisem: [OK / NALEZENY PROBLÉMY]
[Seznam problémů k vyřešení]

### Konfigurace podpisů
| Pořadí | Podepisující | Kontakt | Role | Forma podpisu |
|--------|-------------|---------|------|---------------|
| 1 | [Jméno] | [e-mail/tel] | [Prodávající] | [ověřený/prostý/elektronický] |
| 2 | [Jméno] | [e-mail/tel] | [Kupující] | [ověřený/prostý/elektronický] |

### Kopie obdrží
- [Jméno] — [e-mail]

### Stav
[Odesláno k podpisu / Připraveno k odeslání / Problémy k vyřešení]

### Další kroky
- [Co očekávat po odeslání]
- [Očekávaná doba vyřízení]
- [Kam uložit podepsaný dokument]
```

## Tipy

1. **Ověřte údaje stran** — Nejčastější chyba je nesprávné jméno/název nebo IČO
2. **Ověřte oprávnění** — Ujistěte se, že podepisující je oprávněn jednat za svou stranu
3. **Úschova kopie** — Podepsané kopie ihned uložte do cloudového úložiště
4. **U nemovitostí** — Po podpisu kupní smlouvy zajistit úschovu kupní ceny a podání návrhu na vklad
