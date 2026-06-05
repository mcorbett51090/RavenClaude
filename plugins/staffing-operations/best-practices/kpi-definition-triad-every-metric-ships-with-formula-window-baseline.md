# KPI Definition Triad — Every Metric Ships with Formula, Window, and Baseline

**Status:** Absolute rule
**Domain:** Staffing operations
**Applies to:** `staffing-operations`

---

## Why this exists

"Fill rate is 62%" is not a finding. It is a number without a denominator, a time window, or a reference point. Fill rate has at least four common formulas; which one is used determines whether the number is meaningfully comparable to a benchmark or prior period. A metric without its definition triad — formula, window, baseline — cannot be acted on and should not ship in a deliverable.

## How to apply

Every KPI in a deliverable must carry its triad in a structured footnote or table:

```
KPI Citation Template
──────────────────────
Metric:    Fill rate (healthcare travel, allied division)
Value:     62%
Formula:   Orders filled ÷ orders received (workable orders only)
Window:    Trailing 90 days, ending 2026-05-31
Baseline:  71% same period prior year; 80% = MSP Tier-1 SLA threshold
Source:    Client ATS extract provided 2026-06-01
```

For a scorecard table format, add columns rather than footnotes:

| Metric | Value | Formula | Window | Baseline | Status |
|--------|-------|---------|--------|----------|--------|
| Fill rate | 62% | Filled ÷ workable orders | T-90 days | 71% PY; 80% SLA | Below target |
| TTF | 18 days | Order open to start | T-90 days | 14 days PY | Watch |

**Do:**
- Define the denominator when the metric has multiple common formulas (fill rate, time-to-fill, gross margin).
- Select the window before calculating; do not choose the window after seeing which one looks best.
- State the baseline as a specific reference — a prior period, an SLA threshold, or an industry benchmark with a source — not just "industry average."

**Don't:**
- Ship a metric with a value but no formula, window, or baseline — it cannot be interpreted.
- Use inconsistent denominators across periods when comparing (e.g., workable orders in one period, total orders received in another).
- Treat a benchmark quoted from a vendor's press release as a primary-source baseline without noting its origin and date.

## Edge cases / when the rule does NOT apply

Informal internal communications (a quick status update between team members) may use shorthand metrics without the full triad. Any metric entering a client deliverable, an exec readout, or a slide deck requires the full triad.

## See also

- [`../agents/staffing-operations-analyst.md`](../agents/staffing-operations-analyst.md) — the primary enforcer of the KPI definition discipline in scorecard and diagnostic work.
- [`./pair-fill-rate-with-time-to-fill.md`](./pair-fill-rate-with-time-to-fill.md) — the companion rule applying the triad to the paired fill-rate / TTF output.

## Provenance

Codifies CLAUDE.md §3 #1 (every KPI ships with a definition, a window, and a baseline) as a structured format. The formula-window-baseline triad is the minimum information required for a metric to be actionable in an operations engagement.

---

_Last reviewed: 2026-06-05 by `claude`_
