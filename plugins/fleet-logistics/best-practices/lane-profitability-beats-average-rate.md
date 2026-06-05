# Analyze Lane Profitability, Not Average Rate

**Status:** Absolute rule
**Domain:** Fleet economics / lane analysis
**Applies to:** `fleet-logistics`

---

## Why this exists

A fleet's average rate-per-mile is an accounting artifact — it averages profitable lanes against money-losing ones and hides both. A carrier running a $2.50 average rate while holding three lanes below CPM is losing on those lanes every cycle. The lane is the atom of fleet economics: revenue, deadhead, CPM, and cycle time differ by lane, and so does the profit. Averaging across lanes produces a number that cannot be acted on.

## How to apply

Build a lane-level P&L for every regular lane with enough volume to analyze (use trailing 90 days minimum):

```
Lane P&L template (per-lane, per-period):
- Loaded miles driven
- Empty / deadhead miles (both origin and destination repositioning)
- Total miles (loaded + empty)
- Revenue ($) and effective rate ($ / total mile)
- Fuel cost ($): total miles × fuel CPM
- Driver cost ($): total miles × driver CPM
- Fixed cost allocation ($): loaded miles × fixed CPM share
- Total lane cost ($)
- Lane margin ($) and margin %
- Cycle time (days): load pick → next load ready
- Revenue-per-truck-per-day: lane revenue / cycle time
```

Rank lanes by margin %, then by revenue-per-truck-per-day. The bottom quartile gets either repriced, restructured with a backhaul, or shed.

**Do:**
- Use total miles (loaded + empty) in the denominator for the effective rate — loaded miles only flatters the rate.
- Flag lanes where cycle time is long and revenue-per-truck-per-day is below the fleet average.
- Compare the lane's margin against the fleet's OR to decide whether it's accretive or dilutive.

**Don't:**
- Average lane economics across regions or customer types and call it a rate analysis.
- Make a rate-increase request without a lane P&L behind it — the customer will ask, and the carrier should know first.
- Ignore the backhaul when evaluating a lane: a low-margin outbound paired with a strong backhaul may be the fleet's best cycle.

## Edge cases / when the rule does NOT apply

Owner-operators with a single lane or a single customer are already at the lane level — apply the formula, but the "ranking" step is trivial. For spot freight with no repeat pattern, use the per-load equivalent (revenue ÷ total miles including the pick-up deadhead) rather than building a 90-day series.

## See also

- [`../agents/logistics-cost-analyst.md`](../agents/logistics-cost-analyst.md) — owns lane P&L construction and ranking.
- [`../agents/dispatch-routing-specialist.md`](../agents/dispatch-routing-specialist.md) — owns the backhaul and repositioning logic that changes lane economics.
- [`./rate-per-mile-is-meaningless-without-the-cost-and-the-lane.md`](./rate-per-mile-is-meaningless-without-the-cost-and-the-lane.md) — the parent rule; this doc is the operational implementation.

## Provenance

Codifies the team's house opinion (CLAUDE.md §3 #6) applied at the lane level: a rate without the cost and the lane is meaningless. Standard practice in carrier yield management (ATRI, 2024 Operational Costs study).

---

_Last reviewed: 2026-06-05 by `claude`_
