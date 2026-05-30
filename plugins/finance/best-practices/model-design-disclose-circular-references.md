# Design and disclose every circular reference — never let one happen by accident

**Status:** Absolute rule
**Domain:** Financial modeling / auditability
**Applies to:** `finance`

---

## Why this exists

A circular reference in a financial model is either a deliberate, documented piece of structure or it is a bug — there is no third category. The canonical legitimate circular is the **interest-on-cash-sweep loop**: interest expense depends on average debt, the cash sweep depends on free cash flow, and free cash flow depends on interest expense. That loop is real economics and is allowed — *provided it is designed, isolated behind a switch, and disclosed on the Documentation tab*. Every other circular is an accident: a formula that reaches forward into a cell that depends back on it, silently resolved by iterative calculation, producing numbers nobody can trace. The `financial-modeler` agent's anti-pattern list is explicit — "Excel models with circular references that aren't explicitly designed … undisclosed circulars are bugs." An undisclosed circular also breaks under any tool that does not iterate (a recalc in a different setting, a CSV export, a port to Python) and silently returns a different answer.

## How to apply

Make the one legitimate loop explicit, switchable, and documented; ban all others. The standard pattern is a **circularity switch** plus a **copy-paste circuit breaker**:

```
Inputs:   CircularitySwitch   TRUE/FALSE     # FALSE forces interest off a hardcoded prior-balance, breaking the loop
Mechanics:
  InterestExpense = IF(CircularitySwitch, AvgDebt * Rate, PriorAvgDebt * Rate)
  CashSweep       = MAX(0, FreeCashFlow - MinCashBuffer)
Documentation tab:
  "Designed circular: interest-on-cash-sweep. Switch = CircularitySwitch on Inputs.
   To debug, set FALSE, fix the error, set TRUE. No other circulars permitted."
```

**Do:**
- Isolate the designed loop behind a switch so a reviewer can break it to debug, then restore it.
- Disclose every designed circular on the Documentation/Assumptions tab — what it is, why, and how to break it.
- Turn on iterative calc *only* where the designed loop needs it, and say so.

**Don't:**
- Leave a circular reference in the model that you cannot point to on the Documentation tab — that is a bug, not a feature.
- Mask a circular with `IFERROR(formula, 0)` — that hides the loop and silently zeroes a real number.
- Ship a model with iterative calculation on and no documented reason — the next reader cannot tell design from accident.

## Edge cases / when the rule does NOT apply

- **Models with no debt sweep / no interest-on-cash** often have *zero* legitimate circulars — in that case any circular at all is a bug, full stop.
- **A deliberately broken loop for debugging** (switch set to FALSE) is fine and expected; the rule governs the *shipped* state, where the loop is restored and documented.
- **Single-statement analyses** with no debt schedule carry no interest loop and so no designed circular — the rule attaches once a debt schedule and cash sweep exist.

## See also

- [`./link-the-three-statements.md`](./link-the-three-statements.md) — the integrity rule; designed circulars loop through the debt schedule it describes.
- [`./inputs-live-in-one-place.md`](./inputs-live-in-one-place.md) — the circularity switch lives on the Inputs sheet.
- [`../agents/financial-modeler.md`](../agents/financial-modeler.md) — "designed-vs-accidental circulars"; the undisclosed-circular anti-pattern.
- [`../skills/model-review/SKILL.md`](../skills/model-review/SKILL.md) — the error-check pass that hunts undisclosed circulars.

## Provenance

Codifies the `financial-modeler` agent's designed-vs-accidental-circular opinion and the constitution §4 anti-pattern "Excel models with circular references that aren't explicitly designed … undisclosed circulars are bugs" ([`../CLAUDE.md`](../CLAUDE.md)). Adjacent to the existing three-statement/inputs rules.

---

_Last reviewed: 2026-05-30 by `claude`_
