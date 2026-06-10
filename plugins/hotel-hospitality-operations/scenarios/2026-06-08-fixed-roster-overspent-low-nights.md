---
scenario_id: 2026-06-08-fixed-roster-overspent-low-nights
contributed_at: 2026-06-08
plugin: hotel-hospitality-operations
product: labor
product_version: "n/a"
scope: likely-general
tags: [labor-productivity, hours-per-occupied-room, staffing, flow-through]
confidence: medium
reviewed: false
---

## Problem

A property staffed a steady weekly roster and ran labor over budget despite soft midweek occupancy. The risk: labor staffed as a fixed roster ignores occupancy, over-spending on low nights and eroding flow-through to GOPPAR exactly when revenue is thin (§3 #4 #5).

## Context

- Property: full-service, strong weekends, soft midweek.
- Constraint: labor hours should flex to occupied rooms × hours-per-occupied-room (§3 #4).
- The team reasoned from the standing schedule.

## Attempts

- Tried: **re-read labor as hours-per-occupied-room** by department (`hotel_hospitality_operations_calc.py labor`). Outcome: midweek cost-per-occupied-room ran far above the weekend standard — the roster, not demand, was the driver.
- Tried: **modeled labor flexed to the occupancy pace forecast.** Outcome: flexing midweek hours protected flow-through without touching weekend service (§3 #4).
- Tried: **named the service elements to protect** so the cut didn't hit guest scores (§3 #6).

## Resolution

The fix was a **labor model flexed to the occupancy forecast with protected service elements**, not a blanket cut or a fixed roster. The output was the hours-per-occupied-room read, the flexed schedule, and the flow-through recovery.

**Action for the next consultant hitting this pattern:** **staff labor to occupancy by hours-per-occupied-room, not a fixed roster.** A standing schedule over-spends on low nights and erodes flow-through; flex to the pace forecast and protect the service that drives scores. See Tree 2 and the `hotel_hospitality_operations_calc.py` `labor` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
