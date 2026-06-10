---
scenario_id: 2026-06-08-occupancy-up-revpar-flat
contributed_at: 2026-06-08
plugin: hotel-hospitality-operations
product: revpar
product_version: "n/a"
scope: likely-general
tags: [revpar, adr, occupancy, trade-off]
confidence: medium
reviewed: false
---

## Problem

A revenue manager dropped rate to hit a 90% occupancy target and reported a 'record occupancy month,' but RevPAR was flat. The risk: occupancy and ADR trade off, so chasing one in isolation can leave RevPAR — the product that pays the bills — exactly where it started or lower (§3 #1).

## Context

- Property: select-service, leisure-heavy weekends.
- Constraint: RevPAR = ADR × occupancy; the right trade-off maximizes the product, not occupancy (§3 #1).
- The manager reasoned from the occupancy target alone.

## Attempts

- Tried: **computed RevPAR before and after the rate cut** (`hotel_hospitality_operations_calc.py revpar`). Outcome: the ADR drop offset the occupancy gain — RevPAR was flat.
- Tried: **read the demand curve** for those nights. Outcome: demand was rate-inelastic enough that the discount bought volume the property would have gotten near rack (§3 #1).
- Tried: **carried it to GOPPAR.** Outcome: the extra occupied rooms added housekeeping and amenity cost, so GOPPAR actually fell (§3 #5).

## Resolution

The fix was a **rate-integrity posture on inelastic nights** and selective discounting only where occupancy was genuinely at risk — optimizing the product, not the occupancy number. The output was the RevPAR comparison, the demand read, and the GOPPAR impact.

**Action for the next consultant hitting this pattern:** **optimize RevPAR (the product), not occupancy or rate alone.** A record-occupancy month at a cut rate can leave RevPAR flat and GOPPAR down; read the demand curve and carry to profit. See Tree 1 and the `hotel_hospitality_operations_calc.py` `revpar` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
