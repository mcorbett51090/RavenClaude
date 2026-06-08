---
scenario_id: 2026-06-08-occupancy-fine-but-economic-occupancy-low
contributed_at: 2026-06-08
plugin: property-management
product: occupancy
product_version: "n/a"
scope: likely-general
tags: [occupancy, economic-occupancy, concessions, noi]
confidence: medium
reviewed: false
---

## Problem

An owner saw 96% physical occupancy and assumed revenue was strong, but NOI lagged budget. The risk: physical occupancy counts heads, not dollars — heavy concessions, loss-to-lease, and delinquency can leave economic occupancy far below the physical number, so a full building still under-collects (§3 #1 #4 #5).

## Context

- Asset class: suburban garden multifamily, recently leased up fast.
- Constraint: economic occupancy = collected rent ÷ GPR, and concessions/loss-to-lease are real give-backs (§3 #5).
- The owner reasoned from the physical occupancy number alone.

## Attempts

- Tried: **computed economic occupancy alongside physical** via the EGI bridge (`property_management_calc.py noi`). Outcome: economic sat well below physical — the lease-up had been bought with one-month-free concessions.
- Tried: **amortized the concession give-back** across the lease term. Outcome: the true revenue per occupied unit was materially below asking (§3 #5).
- Tried: **checked loss-to-lease** vs market. Outcome: in-place rents trailed market on renewals, compounding the gap.

## Resolution

The fix was a **concession burn-off plan plus a renewal rent-to-market schedule**, not more leasing — the building was already full. The output was the EGI bridge, the physical-vs-economic occupancy gap, and the concession amortization.

**Action for the next consultant hitting this pattern:** **read economic occupancy, not just physical, before calling revenue strong.** A full building can under-collect; the gap between physical and economic occupancy is the concession and loss give-back. See Tree 1 and the `property_management_calc.py` `noi` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
