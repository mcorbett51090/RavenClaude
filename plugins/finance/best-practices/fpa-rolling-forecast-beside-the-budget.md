# Keep a rolling forecast beside the frozen budget — never overwrite one with the other

**Status:** Pattern
**Domain:** FP&A / planning cadence
**Applies to:** `finance`

---

## Why this exists

A budget and a rolling forecast do two different jobs, and collapsing them destroys both. The **budget** is the commitment baseline set once a year — the fixed yardstick variance is measured against, the thing the board approved, the number bonuses tie to. The **rolling forecast** is the steering tool: refreshed monthly or quarterly, always extending the same horizon forward (e.g. always 12–18 months out), reflecting the latest actuals and driver updates. If you overwrite the budget with the latest forecast, you lose the ability to say "we are $X off plan" — the plan moved. If you freeze the forecast for cosmetic reasons, you lose the steering signal (the `fpa-analyst` anti-pattern: a forecast "frozen for management cosmetic reasons while reality has moved"). Both artifacts coexist; variance is forecast-or-actual *vs the frozen budget*.

## How to apply

Maintain three columns side by side and never let one assignment clobber another:

```
                 Budget (frozen)    Latest forecast (rolling)   Actual (closed)
Q1 revenue       10,000  (set Jan)  10,200 (refreshed Apr)      10,150  (closed)
Q2 revenue       11,000  (set Jan)  10,800 (refreshed Apr)        —
...
Variance to plan = Actual (or Forecast) − Budget        # always vs the FROZEN budget
Forecast accuracy = Actual − prior Forecast             # measured: bias + MAPE
```

**Do:**
- Freeze the budget at approval; timestamp it; never edit it mid-year (corrections get a documented re-baseline, not a silent edit).
- Refresh the forecast on a declared cadence, carry base/upside/downside scenarios (the `fpa-analyst` "three scenarios, always" rule), and re-extend the horizon each refresh.
- Track **forecast accuracy** explicitly — bias and MAPE — so a systematically biased forecast gets recalibrated.

**Don't:**
- Overwrite the budget column with the current forecast to "make variance look better."
- Freeze the forecast to avoid an uncomfortable conversation — that is the cosmetic-freeze anti-pattern.
- Ship a forecast refresh without its assumption set and scenario branches (constitution §4 anti-pattern).

## Edge cases / when the rule does NOT apply

- **A formal re-baseline / re-forecast event** (post-acquisition, major restructuring, a board-approved reset) legitimately resets the budget baseline — but it is explicit, dated, documented, and disclosed, not a quiet overwrite.
- **Zero-based budgeting cycles** rebuild the budget bottom-up each period; the frozen-baseline discipline still applies once the new ZBB budget is approved.
- **Very early-stage companies** may run forecast-only with no formal budget; the moment a board approves a plan, the budget baseline attaches.

## See also

- [`./model-drive-the-forecast-off-operational-drivers.md`](./model-drive-the-forecast-off-operational-drivers.md) — how the forecast itself is built.
- [`../knowledge/finance-decision-trees.md`](../knowledge/finance-decision-trees.md) — the forecast-method decision tree (driver-based vs trend vs zero-based).
- [`../agents/fpa-analyst.md`](../agents/fpa-analyst.md) — "forecast revisions are normal"; the cosmetic-freeze anti-pattern; "three scenarios, always."
- [`../skills/driver-based-forecasting/SKILL.md`](../skills/driver-based-forecasting/SKILL.md) — the refresh playbook.

## Provenance

Codifies the `fpa-analyst` opinions "forecast revisions are normal" and "three scenarios, always," its frozen-cosmetic-forecast anti-pattern, and the constitution §4 "forecast without a documented assumption set" anti-pattern ([`../CLAUDE.md`](../CLAUDE.md)). New rule.

---

_Last reviewed: 2026-05-30 by `claude`_
