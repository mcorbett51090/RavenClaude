# Revenue-Per-Truck-Per-Day Is the Utilization Clock

**Status:** Primary diagnostic
**Domain:** Fleet utilization / dispatch
**Applies to:** `fleet-logistics`

---

## Why this exists

Rate-per-mile and loaded-mile ratio both ignore time. A truck sitting at a shipper dock for 18 hours after delivery earns nothing, and no CPM or loaded-mile calculation captures that cost. Revenue-per-truck-per-day (RPTD) is the single number that combines rate, utilization, and cycle time into one clock. Carriers who only read rate-per-mile miss the dwell, the reload gap, and the repositioning lag that together consume more margin than a rate shortfall.

## How to apply

Calculate RPTD at the fleet level, then by lane and by driver:

```
RPTD = Total revenue ($) / (Number of tractors × Operating days in period)

Target benchmark [unverified — training knowledge]:
- Truckload: $600–$900/truck/day for an efficient regional carrier
- Last-mile: highly variable by stop density; use fleet average as the baseline

Decompose the gap:
  Ideal RPTD = (Average loaded miles/day × effective rate/mile)
  Actual RPTD = Total revenue / (trucks × days)
  Gap = Idle time + dwell + reload lag + deadhead
```

When RPTD falls, sequence the diagnosis:
1. Is average daily miles declining? → dispatch or dwell problem.
2. Is loaded-mile ratio declining? → deadhead problem.
3. Is rate declining? → pricing or lane-mix problem.

**Do:**
- Track RPTD weekly at the fleet level and monthly by lane — it is the earliest-warning utilization metric.
- Use RPTD alongside OR: a carrier can have an acceptable OR but declining RPTD (volume shrinking, cost not yet following).
- Set a minimum RPTD floor by equipment class; assets below floor for 30 consecutive days trigger a lane or driver review.

**Don't:**
- Report only loaded miles or rate-per-mile to ownership — neither captures dwell and reload lag.
- Use RPTD as the sole driver performance metric; a driver with low RPTD may be on a compliant relay assignment rather than idle.

## Edge cases / when the rule does NOT apply

Dedicated contract carriers with fixed routes may have a contractually-set daily rate that makes RPTD a direct contract-compliance metric, not a dispatch optimization signal. LTL carriers should use revenue-per-shipment-day or similar shipment-unit metric, as tractor-level RPTD is less meaningful in network operations.

## See also

- [`../agents/dispatch-routing-specialist.md`](../agents/dispatch-routing-specialist.md) — owns the cycle-time and dwell analysis that drives RPTD.
- [`../agents/logistics-cost-analyst.md`](../agents/logistics-cost-analyst.md) — owns the RPTD scorecard and trend.
- [`./lane-profitability-beats-average-rate.md`](./lane-profitability-beats-average-rate.md) — lane P&L is the next drill-down once fleet RPTD flags a problem.

## Provenance

Synthesized from standard carrier yield-management practice; RPTD is a common operating KPI in TMS reporting and is cited in ATRI carrier financial benchmarking studies as a utilization proxy.

---

_Last reviewed: 2026-06-05 by `claude`_
