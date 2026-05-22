---
name: model-review
description: 7-pass review of financial models — assumptions, mechanics, integrity (BS balances, CF reconciles), hardcodes, error-checks, scenarios, documentation. Used by `financial-modeler` (primary) and `valuation-analyst` for DCF integrity checks.
---

# Skill: model-review

**Purpose:** 7-pass review pattern for financial models. Used by `financial-modeler` (primary) and `valuation-analyst` for DCF integrity checks.

## When to use

- Reviewing a model built by someone else before relying on it
- Pre-publication review of a model going to a board, lender, or external party
- Triaging a model that "doesn't tie" or produces unexpected results
- Periodic refresh check on a long-lived model

## The 7 passes (in order)

Don't skip ahead. Each pass depends on the prior ones being clean.

### Pass 1 — Assumptions

- Is there a dedicated Assumptions / Inputs tab?
- Are inputs color-coded (blue) and visually distinct from formulas (black) and links (green)?
- Does every load-bearing input have a documented source? (Cite: where, when, who.)
- Are inputs labeled with units (%, $, x, days)?
- Are growth-rate / margin / ratio assumptions reasonable vs. history?

**Pass fails if:** any load-bearing input has no source, OR inputs are scattered across multiple tabs.

### Pass 2 — Mechanics

- Do the three statements tie? (Net income flows to retained earnings; cash flow ties to BS cash; FCF reconciles.)
- Working capital mechanics: do DSO / DPO / DIO drivers produce the AR / AP / inventory balances they should?
- Debt schedule: principal amortization + interest expense + ending balance all tie?
- Tax: effective rate applied? Loss carryforward / NOL mechanics?
- Equity: share count + stock-comp + buybacks all reconciled?

**Pass fails if:** the three statements don't tie, OR any major mechanical relationship is broken.

### Pass 3 — Integrity checks

- Is there a balance-check row on the BS (= A − L − E, should equal 0)?
- Is there a cash tie-out (ending cash on BS = ending cash on CF)?
- Are there debug rows / consistency checks anywhere else (sum of segments = consolidated, etc.)?
- Are there any `#REF!`, `#NAME?`, `#DIV/0!`, `#VALUE!` errors in the model?

**Pass fails if:** any integrity check is missing or returns non-zero, OR any error value exists.

### Pass 4 — Hardcodes

- Are there hardcoded numbers buried inside formulas? (Search for digit patterns inside formulas — `*0.21`, `+12000`, `/365`.)
- Are there hardcoded dates that should be driven from a date schedule?
- Are there hardcoded sheet references that should use named ranges?

**Pass fails if:** any hardcode is material (drives the answer) and isn't justified.

### Pass 5 — Error-checks (IFERROR audit)

- Are there `IFERROR` wrappers masking actual errors?
- Are there `IF` statements that silently route bad data to a default?
- Are there `0` defaults where the right behavior is to fail visibly?

**Pass fails if:** any error-suppression wrapper hides a real bug.

### Pass 6 — Scenarios

- Is there a scenario switch? (A single input that drives the whole model's scenario.)
- Are there at least three scenarios (base / upside / downside)?
- Do all three actually flow through the model end-to-end?
- Is there a sensitivity table on the top 2-3 drivers (revenue growth, margin, WACC for DCF)?

**Pass fails if:** scenarios exist but don't actually switch the model, OR sensitivity tables are missing on a model going external.

### Pass 7 — Documentation

- Is there a Documentation / Cover tab?
- Does it state: version, last refresh date, owner, purpose, scope, key assumptions, known limitations?
- Are the tabs in a sensible order (Cover / Inputs / P&L / BS / CF / DCF / Outputs)?
- Are circular references either eliminated or documented (e.g., interest-on-cash-sweep)?
- Is the model self-explanatory to a new reader?

**Pass fails if:** there's no documentation tab, OR the model has undocumented circulars.

## The deliverable

After running all 7 passes, the review produces:

| Pass | Status (✅ / ⚠️ / 🔴) | Findings | Severity (P0 / P1 / P2) |
|---|---|---|---|

Plus:
- **Top 3 fixes** (the highest-leverage corrections)
- **Reasonableness check on key outputs** (do they pass the smell test?)
- **Recommendation** (use as-is / use with caveats / do not use)

## Severity guide

- **P0** — model produces a wrong answer; fix before use.
- **P1** — model is fragile / opaque, not currently wrong; fix before next refresh.
- **P2** — model is correct but improvable (documentation, polish, structure); fix during next major rebuild.

## See also

- Template: [`../templates/model-documentation.md`](../templates/model-documentation.md)
- Agent: [`../agents/financial-modeler.md`](../agents/financial-modeler.md)
- Agent: [`../agents/valuation-analyst.md`](../agents/valuation-analyst.md)
