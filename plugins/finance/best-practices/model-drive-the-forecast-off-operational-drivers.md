# Drive the forecast off operational drivers, not a growth-rate on last year's total

**Status:** Pattern
**Domain:** Financial modeling / FP&A forecasting
**Applies to:** `finance`

---

## Why this exists

A forecast built as `=PriorRevenue * (1 + growth%)` is a guess wearing a formula. It hides the levers a decision-maker actually controls — units, price, headcount, conversion, churn — inside a single opaque percentage. A **driver-based** forecast decomposes each line into the operational quantities that produce it, so when a stakeholder asks "what if we hire two reps a quarter later?" or "what if churn runs 6% not 4%?", the model answers by changing a driver, not by re-guessing the total. Driver-based models are also *falsifiable*: each driver can be checked against history and against an external benchmark, where a blended growth rate cannot. The `financial-modeler` and `fpa-analyst` agents both own this; the `driver-based-forecasting` skill is the build playbook.

## How to apply

Decompose every material line into quantity × rate drivers, each living on the Inputs sheet, and pick the revenue tree that matches the business model:

```
Revenue (SaaS):        beginning ARR + new ARR − churned ARR + expansion ARR
  new ARR     = reps × ramped-quota × productivity%
  churned ARR = beginning ARR × gross-churn-rate
Revenue (usage):       active accounts × usage-per-account × price-per-unit
Revenue (transactional): volume × take-rate
COGS / gross margin:   per-unit cost × volume  (not a flat margin %)
Opex:                  headcount × fully-loaded-cost-per-FTE, by function + ramp curve
Working capital:       DSO / DPO / DIO drivers → AR / AP / inventory roll
```

**Do:**
- Choose the revenue tree by business model (subscription / usage / transactional) — don't force one shape onto all.
- Drive opex off **headcount math** (comp + benefits + payroll tax + ramp), per the `fpa-analyst` opinion that "headcount math beats opex assumptions."
- Benchmark each driver against history (last-12-month actuals) and an external comp before locking it.

**Don't:**
- Forecast a total line by a single blended growth rate when the underlying drivers are knowable.
- Bury the drivers in formulas — they belong on the Inputs sheet, labelled and sourced (see [`./inputs-live-in-one-place.md`](./inputs-live-in-one-place.md)).
- Let a "miscellaneous / other" driver exceed ~5% of a line without breaking it out (`fpa-analyst` anti-pattern).

## Edge cases / when the rule does NOT apply

- **Genuinely immaterial lines** (a small, stable, non-strategic cost) can carry a simple trend or inflation factor — driver decomposition is not free, and materiality governs effort (house opinion #5).
- **Very early-stage / pre-revenue** companies may lack the operating history to calibrate drivers; a scenario-banded top-down range is honest where a false-precision driver tree is not. State the limitation.
- **A short-horizon flash estimate** explicitly labelled directional can trend-extrapolate; the rule attaches to the forecast of record, not every quick look.

## See also

- [`./inputs-live-in-one-place.md`](./inputs-live-in-one-place.md) — where every driver must live, labelled and sourced.
- [`./fpa-rolling-forecast-beside-the-budget.md`](./fpa-rolling-forecast-beside-the-budget.md) — the cadence the driver model refreshes on.
- [`../knowledge/finance-decision-trees.md`](../knowledge/finance-decision-trees.md) — the forecast-method decision tree (driver-based vs trend vs zero-based).
- [`../skills/driver-based-forecasting/SKILL.md`](../skills/driver-based-forecasting/SKILL.md) — the build playbook.
- [`../agents/fpa-analyst.md`](../agents/fpa-analyst.md) — "headcount math beats opex assumptions"; revenue-by-segment surface area.

## Provenance

Codifies the `driver-based-forecasting` skill, the `fpa-analyst` opinion "headcount math beats opex assumptions" and revenue-decomposition surface area, and the `financial-modeler` working-capital-driver mechanics ([`../CLAUDE.md`](../CLAUDE.md) §8). New, adjacent to the existing inputs/linkage rules.

---

_Last reviewed: 2026-05-30 by `claude`_
