---
scenario_id: 2026-06-05-hold-vs-sell-at-cap-rate-shift
contributed_at: 2026-06-05
plugin: commercial-real-estate
product: disposition
product_version: "n/a"
scope: likely-general
tags: [hold-vs-sell, exit-cap, irr, refinance, disposition]
confidence: medium
reviewed: false
---

## Problem

An owner of a stabilized asset near the end of the business-plan horizon had to decide: sell now, hold and refinance, or hold unlevered. Cap rates had moved since acquisition, and the owner was anchored on the going-in cap rate as the exit assumption — which overstated today's clearing sale price and made "hold" look better than it was. The decision needed today's exit cap, sensitized, not the entry cap assumed flat (CLAUDE.md §3 — exit cap must be sensitized, not assumed flat).

## Context

- Segment: stabilized commercial asset at a hold-period decision point (the framework is asset-class-agnostic; the exit-cap level differs by sector and submarket).
- Constraint: the hold-vs-sell math is a comparison of **net sale proceeds today** (forward NOI ÷ exit cap, net of selling costs and loan payoff) against the **forward return on the equity left in the deal** if held. The exit cap is the single most sensitive input — a 25–50 bps move swings net proceeds by far more than a year of NOI growth.
- Market framing used (dated, `[verify-at-use]`): entering 2026 the cap-rate-vs-10yr-Treasury spread was thin (cited ~110 bps vs a long-run ~150 bps average), with the 10-yr around ~4.15% (early March 2026) and a view that cap rates had likely peaked and could compress 25–50 bps through 2026 — translating to mid-single-digit valuation gains for stabilized assets, led by multifamily/industrial with office lagging. That "compression coming" view is exactly what a hold case leans on — and exactly what must be **sensitized**, because it is a forecast, not a fact.

## Attempts

- Tried: computed net sale proceeds at **today's** exit cap (not the going-in cap), netting selling costs and the loan payoff, then expressed it as an equity multiple on the equity invested. Outcome: at a realistic (wider) exit cap the sale-now proceeds were lower than the owner's anchored expectation — the going-in-cap exit had been flattering the disposition value.
- Tried: built the **hold case as a forward return on the trapped equity** — one more year of cash flow plus the change in equity value under a *range* of exit caps (flat, +25 bps, −25 bps), not a single point. Outcome: the hold only beat the sale if cap rates actually compressed; under a flat or wider exit cap, holding earned a thin or negative return on the equity left in.
- Tried: priced the **refinance** path as the third option (pull equity out via a new loan, hold the asset) — which only made sense if the refi cleared the DSCR/debt-yield test at today's rate (the refi-wall check, §3 #6). Outcome: connected the disposition decision to the refinance-breach pattern — a hold-and-refi is only available if the refi pencils.

## Resolution

The decision was made on a **sensitized exit cap** with a side-by-side of sell-now equity multiple vs the forward return on trapped equity across a cap-rate range, plus the refinance test for the hold-and-refi path — not on a going-in-cap-assumed-flat exit that flattered the hold. The output was a dated hold/sell/refi comparison with the exit cap as an explicit sensitivity axis.

**Action for the next analyst hitting this pattern:** **never exit at the going-in cap assumed flat — sensitize the exit cap (±25–50 bps) and compare sell-now net proceeds against the forward return on the equity that stays trapped in a hold; gate the hold-and-refi path on the refi clearing DSCR/debt-yield at today's rate.** The [`../scripts/cre_calc.py`](../scripts/cre_calc.py) `hold-vs-sell` mode computes net sale proceeds + equity multiple + a rough one-year held return; the [`../knowledge/cre-hold-sell-refi-decision-tree.md`](../knowledge/cre-hold-sell-refi-decision-tree.md) tree sequences the three paths.

**Sources (retrieved 2026-06-05 — `[verify-at-use]`, cap-rate/Treasury figures move quarterly):**
- CLS — CRE market data 2026 (Treasury yields, cap rates; ~110 bps spread vs ~150 bps long-run average, 10-yr ~4.15% early March 2026): https://clscre.com/market-data.html
- CBRE Investment Management — the case for and against narrow cap-rate spreads: https://www.cbreim.com/insights/articles/the-case-for-and-against-narrow-cap-rate-spreads
- Commercial Property Executive / CommercialSearch — cap rates hold steady across major CRE sectors (sector variation, compression view): https://www.commercialsearch.com/news/cap-rates-hold-steady-across-major-cre-sectors/

Cap-rate levels, spreads, and the compression outlook are quarterly-volatile and sector/submarket-specific — every figure here is `[verify-at-use]` against a current capital-markets report (§3 #8).
