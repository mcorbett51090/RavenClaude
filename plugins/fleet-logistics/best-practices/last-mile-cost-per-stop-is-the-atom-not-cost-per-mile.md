# Last-Mile: Cost Per Stop Is the Atom, Not Cost Per Mile

**Status:** Absolute rule
**Domain:** Last-mile fleet economics
**Applies to:** `fleet-logistics`

---

## Why this exists

Cost-per-mile is the correct unit of analysis for linehaul and long-haul trucking. It is the wrong unit for last-mile and final-mile delivery operations, where the value driver is stop density and cost-per-stop, not miles. A last-mile route with 40 stops in 60 miles has a very different economics profile than a route with 15 stops in 60 miles — the CPM is identical, but the revenue per stop and the cost per delivery are completely different. Carriers and shippers who benchmark last-mile on CPM systematically miss the real lever, which is route density optimization.

## How to apply

Build last-mile economics on a cost-per-stop (CPS) framework:

```
Cost-per-stop model (per route, per period):
  Total route cost ($):                   ______
    Driver labor (hours on route × rate): ______
    Fuel (miles × fuel CPM):             ______
    Vehicle fixed allocation ($/day):    ______
    Package-handling / service time:     ______
  Total stops completed:                 ______
  Cost per stop:                         $______

  Revenue per stop:                      $______
  Margin per stop:                       $______

  Route efficiency metrics:
    Stops per hour:                      ______  (target: 12–18 for residential [unverified])
    Stops per mile:                      ______  (higher = denser = better)
    Failed delivery rate:                ______% (re-attempts double the CPS)
```

Optimization levers ranked by impact:
1. **Route density** — more stops per mile reduces vehicle fixed cost per stop.
2. **Failed delivery rate** — a 15% failed delivery rate adds 15% to effective CPS; address with delivery-window management.
3. **Stop sequence** — optimized stop order reduces total route miles and hours.
4. **Vehicle right-sizing** — a large van doing 10 stops/day has a higher fixed CPS than a cargo bike or compact van at the same stop density.

**Do:**
- Report last-mile economics in CPS alongside CPM — both belong on the scorecard, because CPM alone masks density.
- Benchmark CPS by route type (residential vs. commercial, urban vs. suburban) — they are not comparable.
- Model failed delivery cost explicitly; the re-attempt is often invisible in the aggregate but large in CPS terms.

**Don't:**
- Apply linehaul OR analysis directly to a last-mile P&L — the cost structures are different.
- Set last-mile pricing based solely on mileage — a flat per-stop price is more accurate to the cost structure.

## Edge cases / when the rule does NOT apply

Long-distance parcel delivery (e.g., a 300-mile single-package run to a rural address) reverts to CPM analysis; the "last mile" economics only apply where multi-stop routes are the operating pattern. Freight forwarding and less-than-truckload (LTL) terminal operations use a hybrid metric (cost per hundredweight or cost per shipment).

## See also

- [`../agents/dispatch-routing-specialist.md`](../agents/dispatch-routing-specialist.md) — owns route density optimization and stop-sequence planning.
- [`../agents/logistics-cost-analyst.md`](../agents/logistics-cost-analyst.md) — owns the CPS model and last-mile scorecard.
- [`./revenue-per-truck-per-day-is-the-utilization-clock.md`](./revenue-per-truck-per-day-is-the-utilization-clock.md) — for last-mile, revenue-per-truck-per-day is still valid alongside CPS; use both.

## Provenance

Standard last-mile logistics practice; the shift from CPM to CPS as the core metric is well established in e-commerce fulfillment and parcel delivery operations research and carrier management consulting.

---

_Last reviewed: 2026-06-05 by `claude`_
