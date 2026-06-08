---
scenario_id: 2026-06-08-front-only-gross-hid-a-good-deal
contributed_at: 2026-06-08
plugin: automotive-dealership
product: total-gross
product_version: "n/a"
scope: likely-general
tags: [total-gross, fi-penetration, pvr, desking]
confidence: medium
reviewed: false
---

## Problem

A desk manager pushed for thick front gross and resisted aggressive pricing, while total store gross stalled. The risk: judging deal quality on front gross alone ignores the high-margin back-end — a thinner front that closes more units and attaches more compliant F&I can produce more total gross (§3 #3 #4).

## Context

- Store: volume brand, competitive front-gross market.
- Constraint: total gross = front + back; PVR is the back-end lever (§3 #3 #4).
- The desk reasoned from front gross per unit only.

## Attempts

- Tried: **computed total gross per unit (front + back)** (`automotive_dealership_calc.py gross-per-unit`). Outcome: the back-end carried more of the deal than the front realized.
- Tried: **modeled a thinner-front / higher-volume scenario** with steady F&I penetration. Outcome: more units at a thinner front plus the attached back produced more total gross (§3 #3).
- Tried: **held the F&I penetration push inside the compliance boundary**, routing disclosure/pricing questions to counsel (§2).

## Resolution

The fix was a **total-gross desking policy (front + back) with a compliant F&I attach focus**, not front-gross maximization. The output was the total-gross-per-unit read, the volume scenario, and the penetration target inside compliance.

**Action for the next consultant hitting this pattern:** **manage total gross (front + back), not front alone.** A thin front with a strong, compliant back can beat a fat front with no back; keep the F&I push inside counsel's compliance rules. See Tree 1 and the `automotive_dealership_calc.py` `gross-per-unit` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
