# A Control Premium Must Be Sourced and Bounded

**Status:** Absolute rule
**Domain:** Valuation / M&A
**Applies to:** `finance`

---

## Why this exists

Acquisition price analyses routinely apply a control premium to a minority-interest comparable-company value to arrive at an enterprise acquisition price, and practitioners frequently reach for a round number (30%, 40%) that they remember from a prior deal or a vague recollection of published data. An unsourced, unbounded premium inflates the justified acquisition price and misrepresents the fairness-opinion foundation. The premium is also not symmetric: it varies by sector, deal size, buyer type (strategic vs. financial), and market conditions. A 35% premium applied to a software transaction is not the same as the same premium applied to a commodities business. Every control premium deserves its own sourcing.

## How to apply

Source the control premium from a current, period-specific precedent study and bound it with a range before using it in a valuation.

```
Control Premium Sourcing Checklist
────────────────────────────────────────────
□ Pull a comparable-transaction study from a primary source
  (e.g., FactSet/MergerStat, S&P Global, Kroll, Bloomberg) with:
  - Transactions within the last 3–5 years
  - Same sector / SIC code or adjacent (state the match criteria)
  - Similar deal size tier (± 1 order of magnitude on EV)
  - Minimum n = 10 transactions (note if data is thinner)

□ Compute: median, mean, 25th/75th percentile of observed premiums.
□ State the reference date of the market data.
□ Apply a range, not a point: e.g., "25%–40%, central estimate 32%."
□ Disclose in the valuation memo:
  - Source name + download date
  - Sample criteria (sector, size, period)
  - Summary statistics
  - Rationale for placement within the range (strategic vs. financial buyer; contested vs. negotiated)
```

**Do:**
- Refresh the precedent study for every new valuation — market premiums shift with credit conditions, sector momentum, and deal volume.
- Disclose the premium explicitly in the football-field output and in the methodology section of any fairness-opinion support document.
- Triangulate against the implied premium from your own DCF (acquisition price / minority-interest MVIC – 1).

**Don't:**
- Apply a memorized or round-number premium without a sourced study.
- Use a study from a different sector and claim it as comparable.
- Present the premium-adjusted value as the only output; show the pre-premium minority value and the premium separately so the reader can evaluate each.
- Apply a control premium on top of a DCF that already assumes control synergies — this double-counts.

## Edge cases / when the rule does NOT apply

- **Minority-stake acquisitions (< 50 %, no control)** — a control premium is not appropriate; apply a minority discount instead if the reference comparable is a control transaction.
- **Asset transactions (not stock)** — the control-premium concept does not apply directly; use asset-level comps and a different methodology.
- **409A minority valuations** — typically requires a marketability discount (DLOM), not a control premium; the 409A context inverts the direction.

## See also

- [`../agents/valuation-analyst.md`](../agents/valuation-analyst.md) — owns the control-premium sourcing discipline.
- [`./valuation-triangulate-three-methods.md`](./valuation-triangulate-three-methods.md) — the control-premium-adjusted comps value is one method in the three-method triangle.

## Provenance

Codifies the valuation-analyst's discipline from the finance plugin's CLAUDE.md §4 anti-pattern ("Valuation outputs presented as a single point estimate rather than a range with method weights") and the `dcf-valuation` skill's football-field cross-check. The FactSet/MergerStat and Kroll sourcing references are standard US M&A practice; verify dataset availability and coverage for non-US transactions.

---

_Last reviewed: 2026-06-05 by `claude`_
