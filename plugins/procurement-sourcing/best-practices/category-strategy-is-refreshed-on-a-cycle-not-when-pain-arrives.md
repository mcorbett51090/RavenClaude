# Refresh the Category Strategy on a Cycle, Not When Pain Arrives

**Status:** Pattern
**Domain:** Category management
**Applies to:** `procurement-sourcing`

---

## Why this exists

Category strategies written once and never refreshed are descriptive documents, not living instruments. The supply market, the business's demand profile, and the category's Kraljic position all shift — a category that was leverage two years ago may be bottleneck today (if a single supplier now dominates) or acquisition (if the specification changed). A procurement team that only revisits category strategy when a crisis occurs (supply shortage, price spike, supplier failure) is reactive, and reactive sourcing consistently pays more and gets worse terms than proactive sourcing. The refresh cycle is what keeps the strategy calibrated to current market reality.

## How to apply

Set an explicit refresh cadence for each category and track it in the category portfolio.

```
Category Strategy Refresh Schedule
──────────────────────────────────────────────────────
Category type (Kraljic)  | Refresh cycle     | Trigger for out-of-cycle refresh
─────────────────────────|───────────────────|──────────────────────────────────
Strategic                | Annual            | Supplier M&A; major spec change;
                         |                   | market disruption; supplier financial distress
Leverage                 | Every 18 months   | Same plus: 2+ new entrants; commodity
                         |                   | index move ≥ 15% in 6 months
Bottleneck               | Every 2 years     | Supplier capacity constraint; new
                         |                   | alternative qualification; spec change
Acquisition              | Every 3 years     | Volume growth into leverage tier;
                         |                   | specification consolidation opportunity

Refresh Output (minimum):
  □ Kraljic position re-assessed (has it moved?)
  □ Supply market update: new entrants, consolidation, capacity
  □ Demand forecast for next 2 years: volume + specification stability
  □ Current supplier performance summary (scorecard link)
  □ Revised sourcing play and rationale
  □ Savings opportunity estimate for next cycle
  □ Category owner and stakeholder sign-off
```

**Do:**
- Build the category refresh calendar into the annual FP&A/procurement planning cycle so it is scheduled, not ad hoc.
- Involve the business owner and technical stakeholder in the refresh — a procurement-only view misses demand-side changes.
- Document the Kraljic re-assessment explicitly; if the position hasn't changed, state why.

**Don't:**
- Treat "the strategy hasn't changed" as a reason to skip the refresh — if you haven't checked, you don't know.
- Allow contract renewal to substitute for a category strategy refresh; the two are related but serve different purposes.
- Run a category strategy refresh in the same week as a sourcing event — the strategy should precede, not follow, the event.

## Edge cases / when the rule does NOT apply

- **Sub-threshold or acquisition categories** where the total spend does not justify a formal category strategy document — a brief market review memo every 3 years satisfies the refresh discipline for these.
- **Commodities on a long-term take-or-pay contract** with fixed terms — the strategy refresh cadence applies to the next contract cycle; a mid-contract refresh is informational, not actionable until the agreement window opens.

## See also

- [`../agents/category-strategist.md`](../agents/category-strategist.md) — owns the category strategy and the refresh process.
- [`./segment-the-spend-before-you-source-it.md`](./segment-the-spend-before-you-source-it.md) — the Kraljic re-assessment in the refresh cycle depends on the segmentation framework this rule establishes.

## Provenance

Codifies the category-strategist's category-lifecycle discipline from the procurement-sourcing plugin's CLAUDE.md §3 #1 (segment before sourcing, Kraljic matrix). The refresh cadence tiers by Kraljic position reflect standard category management practice (Ariba/SAP benchmarks and CIPS category management framework). Verify cadence norms against current benchmarks before citing to a client.

---

_Last reviewed: 2026-06-05 by `claude`_
