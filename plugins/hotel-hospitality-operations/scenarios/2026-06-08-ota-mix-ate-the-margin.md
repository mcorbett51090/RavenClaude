---
scenario_id: 2026-06-08-ota-mix-ate-the-margin
contributed_at: 2026-06-08
plugin: hotel-hospitality-operations
product: channel
product_version: "n/a"
scope: likely-general
tags: [channel-mix, net-rate, ota, goppar]
confidence: medium
reviewed: false
---

## Problem

A GM celebrated record RevPAR driven by OTA volume, but GOPPAR didn't move. The risk: gross rate and net rate diverge by the acquisition cost — an OTA-heavy mix at 15-20% commission [unverified — training knowledge] can lift RevPAR while keeping less margin than a lower-RevPAR, direct-heavy mix (§3 #2 #5).

## Context

- Property: branded full-service, heavy OTA reliance.
- Constraint: net rate = gross rate − acquisition cost; direct keeps more margin (§3 #2).
- The GM reasoned from gross RevPAR.

## Attempts

- Tried: **compared channels at net rate** (`hotel_hospitality_operations_calc.py channel-cost`). Outcome: the OTA net rate trailed the direct net rate materially after commission.
- Tried: **traced the GOPPAR gap to channel cost.** Outcome: commission, not labor, was the leak between RevPAR and GOPPAR (§3 #5).
- Tried: **valued direct/loyalty demand** for the margin and repeat it keeps (§3 #6).

## Resolution

The fix was a **direct-booking and loyalty shift to improve channel mix**, accepting slightly lower gross RevPAR for higher net rate and GOPPAR. The output was the net-rate comparison, the channel-cost GOPPAR bridge, and the mix-shift target.

**Action for the next consultant hitting this pattern:** **manage channel mix at net rate, not gross RevPAR.** Commission can eat a RevPAR record before it reaches GOPPAR; value direct/loyalty for the margin it keeps. See Tree 1 and the `hotel_hospitality_operations_calc.py` `channel-cost` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
