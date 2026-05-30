# Drive every scenario from one switch, and present a range — never a single point

**Status:** Pattern
**Domain:** Financial modeling / scenario design
**Applies to:** `finance`

---

## Why this exists

A model that emits a single number is a guess with extra decimal places. Real decisions need to know how the answer moves when the two or three assumptions that matter most move — and the only honest way to show that is a **scenario set driven from one switch** plus a **sensitivity table** on the highest-leverage drivers. The `fpa-analyst` rule is "three scenarios, always — base / upside / downside; a single forecast is false precision," and the `valuation-analyst` rule is "range first, midpoint second." The mechanical trap is scenarios implemented as scattered `IF` statements: change the case in one place, forget another, and base and downside silently blend into an incoherent hybrid. One switch cell, read everywhere, makes the active case unambiguous and the model re-flowable in a single keystroke.

## How to apply

Put one `ScenarioSwitch` on the Inputs sheet; every scenario-dependent driver reads its value from a case table keyed on that switch; outputs carry a sensitivity table on the top 2–3 drivers:

```
Inputs:
  ScenarioSwitch   = 2          # 1 = downside, 2 = base, 3 = upside
  RevGrowth        = CHOOSE(ScenarioSwitch, 1%, 4%, 8%)        # one source, three cases
  ChurnRate        = CHOOSE(ScenarioSwitch, 8%, 5%, 3%)
Outputs:
  Sensitivity grid: EV (or EBITDA) across WACC × terminal-growth, or across the top revenue driver
  Presentation:     low / mid / high — the range is the headline, the midpoint is the footnote
```

**Do:**
- Carry base / upside / downside as the default set; attach probability weights when the audience needs an expected value (`driver-based-forecasting` skill).
- Build a sensitivity table on the two or three drivers that actually move the answer — for a DCF, WACC, terminal growth, and the top revenue driver (`valuation-analyst`).
- Present the result as a range; reserve the single number for a headline that sits *next to* the range, never alone.

**Don't:**
- Implement scenarios as scattered `IF(case="base",…)` formulas — one switch, read everywhere, or the cases drift.
- Show a sensitivity table on a driver the output is insensitive to — it manufactures false reassurance.
- Present a point estimate as "the answer" — that is the `valuation-analyst` single-point anti-pattern and the `fpa-analyst` false-precision anti-pattern.

## Edge cases / when the rule does NOT apply

- **A purely mechanical tie-out** (does the balance sheet balance?) is a yes/no, not a scenario — it lives in the error-check block, not the scenario switch.
- **Below-threshold or directional flash work** may legitimately run a single case if labelled directional — but the forecast of record and any valuation carry the full range.
- **Probability-weighted blends** are an addition, not a replacement: still show the underlying scenarios, because a weighted midpoint with no visible range hides the dispersion.

## See also

- [`./inputs-live-in-one-place.md`](./inputs-live-in-one-place.md) — the single switch cell lives on the Inputs sheet.
- [`./fpa-rolling-forecast-beside-the-budget.md`](./fpa-rolling-forecast-beside-the-budget.md) — the three-scenario rolling forecast cadence.
- [`./valuation-discipline-the-terminal-value.md`](./valuation-discipline-the-terminal-value.md) — the WACC × terminal-growth sensitivity grid this rule asks for.
- [`../agents/valuation-analyst.md`](../agents/valuation-analyst.md) — "range first, midpoint second"; the single-point anti-pattern.
- [`../skills/dcf-valuation/SKILL.md`](../skills/dcf-valuation/SKILL.md) — the football-field and sensitivity build.

## Provenance

Codifies the `fpa-analyst` "three scenarios, always" opinion, the `valuation-analyst` "range first, midpoint second" / single-point-estimate anti-pattern, and the constitution §4 anti-pattern "valuation outputs presented as a single point estimate rather than a range" ([`../CLAUDE.md`](../CLAUDE.md)). New, adjacent to the inputs and forecast rules.

---

_Last reviewed: 2026-05-30 by `claude`_
