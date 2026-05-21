# Model documentation — [Model name]

> The "Documentation" tab content for any financial model. Copy into your model's Cover / Documentation sheet, or save alongside the model as a companion markdown file.

## Identity

- **Model name:** [e.g., "Project Atlas 3-statement model"]
- **Version:** [v0.1, v1.0, etc.]
- **Last refresh:** [YYYY-MM-DD]
- **Owner:** [name + role]
- **Reviewer:** [name + role]
- **Status:** Draft | Active | Archived
- **Confidentiality:** internal | client-confidential | privileged

## Purpose

[One paragraph: what this model is for, who uses it, what decisions it supports.]

## Scope

- **In scope:** [periods covered, entities, segments]
- **Out of scope:** [explicit exclusions]
- **Currency:** [reporting currency + any FX assumptions]
- **GAAP / IFRS / management view:** [which set of accounting policies]

## Key assumptions (cite each source)

| Assumption | Value | Source | Date | Sensitivity in output |
|---|---|---|---|---|
| Revenue growth | x% | [source] | YYYY-MM-DD | High / Med / Low |
| Gross margin | x% | [source] | YYYY-MM-DD | High / Med / Low |
| Effective tax rate | x% | [source] | YYYY-MM-DD | Low |
| WACC (for DCF) | x% | Build per [source] | YYYY-MM-DD | High |
| Terminal growth | x% | Cap at long-run real GDP, [source] | YYYY-MM-DD | High |
| ... | ... | ... | ... | ... |

## Tab inventory

| Tab name | Purpose | Color convention |
|---|---|---|
| Cover / Documentation | This tab | n/a |
| Assumptions / Inputs | All driver inputs; blue cells | Blue = input |
| P&L | Income statement build | Black = formula |
| BS | Balance sheet build | Black = formula |
| CF | Cash flow build (indirect) | Black = formula |
| DCF | Valuation build (if applicable) | Black = formula |
| Outputs | Summary tables and charts | Green = link |
| Debug / Check | Integrity checks (BS balance, cash tie-out, etc.) | Red = error / debug |

## Integrity checks present

- [ ] Balance check row on BS (A − L − E = 0)
- [ ] Cash tie-out (BS ending cash = CF ending cash)
- [ ] Sub-segment to consolidated tie-out
- [ ] No error values (`#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?`)

## Scenarios

- **Base case:** [description]
- **Upside case:** [description and what drivers move]
- **Downside case:** [description and what drivers move]
- **Scenario switch cell:** [e.g., `Assumptions!B2`]

## Circular references

- [ ] None
- [ ] Documented: [list each intentional circular and why]

## Known limitations

- [Anything the model doesn't capture that a reader should know about.]

## Change log

| Date | Version | Author | Change |
|---|---|---|---|
| YYYY-MM-DD | v1.0 | [name] | Initial build |
| ... | ... | ... | ... |

---

**Reviewed:** [YYYY-MM-DD] by [name]
