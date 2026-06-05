# Backhaul Fills the Deadhead Gap Before Repricing

**Status:** Primary diagnostic
**Domain:** Routing / lane economics
**Applies to:** `fleet-logistics`

---

## Why this exists

When a lane's margin is thin, the instinctive response is to request a rate increase. The cheaper diagnostic is: does this lane have an addressable backhaul? A 30% empty-mile ratio on a round-trip lane is a $0.68/total-mile cost drag at a $2.26 CPM. Finding even a partial backhaul that cuts deadhead by half recovers more margin than a 5% rate increase on the outbound — and it requires no customer negotiation. Repricing before solving the backhaul is a harder sell built on an inflated cost base.

## How to apply

Before any rate-increase discussion, run the backhaul diagnostic:

```
Lane backhaul analysis template:
1. Map the return corridor (Google Maps / broker boards / shipper networks)
2. List available freight in the return window (load boards: DAT, Truckstop)
3. Estimate backhaul revenue potential ($) at current spot or contract rate
4. Recalculate effective round-trip CPM with backhaul revenue credited

Revised lane economics:
  Outbound revenue:       $X
  Backhaul revenue:       $Y (partial or full)
  Total miles (round):    M miles
  Total lane cost:        M × CPM
  Net lane margin:        (X + Y) − (M × CPM)
```

Decision sequence:
1. Is there a consistent backhaul match within 50 miles of the destination? → Pursue before any rate call.
2. Is backhaul revenue ≥ 60% of deadhead cost? → Reframe the lane as viable with the backhaul.
3. Is no backhaul available and margin is negative? → Now escalate to repricing or shed the lane.

**Do:**
- Model the lane as a round-trip with backhaul credit before calling it unprofitable.
- Use 90-day load board history for the destination market to assess backhaul availability, not a single-day spot check.
- Include repositioning miles from the backhaul drop to the next load origin in the total-mile count.

**Don't:**
- Present a rate-increase request without a lane P&L that includes backhaul exploration — the shipper will ask why the carrier didn't find freight on the return.
- Accept a backhaul that adds more than 50 miles of repositioning without recalculating whether it remains accretive.

## Edge cases / when the rule does NOT apply

Hazmat or specialized equipment (tankers, flatbeds with escorts) may have no practical backhaul for regulatory or equipment-type reasons — in those cases, rate is the only lever. Dedicated contract lanes with a fixed return commitment already have the backhaul baked in; the analysis is whether the contract rate reflects both directions.

## See also

- [`../agents/dispatch-routing-specialist.md`](../agents/dispatch-routing-specialist.md) — owns backhaul sourcing and repositioning logic.
- [`../agents/logistics-cost-analyst.md`](../agents/logistics-cost-analyst.md) — owns the round-trip lane P&L model.
- [`./lane-profitability-beats-average-rate.md`](./lane-profitability-beats-average-rate.md) — backhaul analysis is a component of the lane P&L built in that rule.

## Provenance

Standard carrier yield-management practice; backhaul-first-then-reprice sequencing is codified in ATRI operational cost guidance and is a standing principle of network planning at asset-based carriers.

---

_Last reviewed: 2026-06-05 by `claude`_
