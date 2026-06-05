# Capacity Factor and Availability Are Different Metrics — Report Both

**Status:** Pattern
**Domain:** Asset performance / O&M
**Applies to:** `renewable-energy`

---

## Why this exists

Solar asset performance is often reported as a single number — "capacity factor" or "performance ratio" — which is insufficient for O&M diagnosis. Capacity factor (actual energy / theoretical maximum energy over a period) conflates resource variability with equipment downtime. Availability (percentage of time the system is operational and capable of producing) isolates the controllable losses. A system with a 22% capacity factor in a low-irradiance winter month looks different from a 22% capacity factor caused by a failed central inverter for 10 days. The first is weather; the second is an O&M failure. Reporting availability separately from capacity factor is what makes O&M performance accountable.

## How to apply

Build the asset performance reporting template to separate resource and equipment contributions:

```
Monthly asset performance report (per site):
  Nameplate capacity (kW-DC):              ______
  Metered production (kWh):                ______
  Modeled production at actual irradiance (kWh): ______  (from PVsyst typical year + actual GHI)

  Capacity factor:
    Actual CF = metered production / (nameplate kW × 720 hrs) = ______%

  Performance Ratio (PR):
    PR = metered production / modeled production = ______%
    Target: ≥ 80% for a well-performing system [unverified — varies by location and technology]

  Availability:
    System-available hours / total hours in period = ______%
    Target: ≥ 98% [unverified — varies by contract and O&M SLA]

  Downtime log:
    Event:              ______   Duration (hrs): ______   Category: equipment / grid / comms / planned
    Production lost (kWh): ______   Revenue impact: $______

  Root cause flag:
    If PR < 80% AND availability > 98%: resource year or soiling/shading — not equipment
    If availability < 98%: equipment failure — O&M response required
    If PR < 80% AND availability < 98%: both causes present — decompose
```

**Do:**
- Separate planned maintenance downtime from unplanned downtime in the availability calculation; mixing them masks O&M performance.
- Report PR against the "typical year" P50 model, not a fixed percentage — the same system has higher natural CF in summer than winter.
- Use availability as the primary O&M SLA metric in the O&M contract, with a minimum threshold and liquidated damages for sustained underperformance.

**Don't:**
- Report only capacity factor to asset owners or investors; it conflates resource and equipment performance.
- Accept "within modeled production" as an O&M pass/fail criterion without also requiring availability reporting — a system at 99% modeled production with a 5% downtime rate masked by irradiance upside is not performing well.

## Edge cases / when the rule does NOT apply

Community solar subscriptions billed at a flat $/kWh subscriber credit may not require investor-level performance decomposition; the billing accuracy is the primary metric. Storage assets require a separate performance framework (round-trip efficiency, state of charge, dispatch availability) that is distinct from PV availability.

## See also

- [`../agents/energy-finance-analyst.md`](../agents/energy-finance-analyst.md) — owns the asset performance scorecard and production guarantee analysis.
- [`../agents/renewables-engagement-lead.md`](../agents/renewables-engagement-lead.md) — uses the performance decomposition to frame asset management reviews.
- [`./a-solar-asset-is-a-25-year-machine-degradation-and-om-are-fi.md`](./a-solar-asset-is-a-25-year-machine-degradation-and-om-are-fi.md) — availability and PR are the operational metrics that validate the 25-year production assumptions in the pro-forma.

## Provenance

The distinction between capacity factor, performance ratio, and availability is standard in IEC 61724 (PV system performance monitoring standards) and is used by asset managers, lenders, and O&M contractors in solar asset reporting.

---

_Last reviewed: 2026-06-05 by `claude`_
