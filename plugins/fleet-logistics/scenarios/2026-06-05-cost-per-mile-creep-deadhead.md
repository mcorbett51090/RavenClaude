---
scenario_id: 2026-06-05-cost-per-mile-creep-deadhead
contributed_at: 2026-06-05
plugin: fleet-logistics
product: cost-analysis
product_version: "n/a"
scope: likely-general
tags: [cost-per-mile, deadhead, utilization, backhaul, lane-profitability]
confidence: medium
---

## Problem

A regional dry-van carrier's margin was eroding across a soft-rate market and the operator's instinct was "rates are too low — we need to raise our prices or shed customers." Revenue per mile looked competitive on paper, but the carrier was still losing money on several lanes. The real driver was hiding in the **denominator**: a creeping all-in cost-per-mile and a deadhead rate well above the industry average, so the carrier was paying full cost on a large slug of empty miles that earned nothing.

## Context

- Segment: for-hire truckload, ~40 trucks, dry van, mixed contract + spot.
- Constraint: the operator tracked revenue-per-mile and a blended "cost per mile" but had **never built CPM bottom-up** — fixed vs. variable was a single blended figure, so it was invisible that fixed CPM was rising as utilization slipped, and that deadhead was the larger leak.
- The operator conflated "low rate" (a revenue symptom) with "unprofitable lane" (which was actually a cost + empty-mile problem). The classic single-cause story the decision trees warn against (§3 #6).

## Attempts

- Tried: **rebuilt CPM bottom-up** before touching rates — fixed monthly block (truck/trailer payment, insurance, permits, overhead) ÷ real miles, plus per-mile variable (fuel via price/MPG, driver pay, maintenance, tires). Anchored the read against the ATRI 2024 benchmark — all-in ~$2.26/mi, non-fuel marginal a record ~$1.78/mi — so the operator could see which components were above industry. Outcome: revealed fixed CPM had climbed because utilization (miles/truck) had slipped, not because any one bill spiked. [`../scripts/fleet_calc.py`](../scripts/fleet_calc.py) `cost-per-mile` did the arithmetic.
- Tried: **measured deadhead** as a first-class number. The carrier was running ~22% empty against an industry that averaged ~16.7% in 2024 and that competitive operators try to hold under 15%. At ~$2.26 all-in CPM, the empty miles were burning real money every month. `fleet_calc.py deadhead` quantified the leak and the dollar prize of pulling it down a few points.
- Tried: **found the backhaul before the rate conversation** — credited backhaul revenue to the thin lanes and re-ran lane P&L. Outcome: several "unprofitable" lanes turned positive once the empty leg was filled, with no rate increase at all (§3 #3). Only the genuinely structurally-low lanes were left for a reprice-or-shed decision.

## Resolution

The margin problem was mostly **cost-per-mile creep from slipping utilization plus an above-average deadhead leak**, not low rates. The fix was operational: rebuild CPM bottom-up to see where cost lived, attack deadhead with backhaul matching, and only *then* reprice or shed the handful of lanes that were structurally thin after the empty leg was filled.

**Action for the next consultant hitting this pattern:** **build CPM bottom-up and measure deadhead before you touch a rate.** Rate-per-mile is meaningless without the cost and the lane (§3 #6); a thin lane is usually a deadhead or utilization artifact, not a pricing failure. Fill the backhaul first (§3 #3), then reprice or shed only what's left. Use [`../scripts/fleet_calc.py`](../scripts/fleet_calc.py) `cost-per-mile` and `deadhead` for the arithmetic, and the "Lane Is Thin but Rate Looks Fine" tree in [`../knowledge/fleet-decision-trees.md`](../knowledge/fleet-decision-trees.md).

**Sources (retrieved 2026-06-05):**
- ATRI — *An Analysis of the Operational Costs of Trucking: 2025 Update* (all-in ~$2.26/mi 2024; non-fuel marginal record ~$1.78/mi; empty miles ~16.7%): https://truckingresearch.org/2025/07/new-atri-report-shows-trucking-profitability-severly-squeezed-by-high-costs-low-rates/
- FleetMaintenance — ATRI 2025 cost-component breakdown (fuel $0.48/mi, driver wages ~$0.80/mi, R&M $0.198/mi, tires $0.047/mi, insurance $0.102/mi, equipment $0.39/mi for 2024): https://www.fleetmaintenance.com/equipment/article/55301363/american-transportation-research-institute-atri-breakdown-of-atri-2025-operational-costs-report
- ApexCapital — deadhead benchmarks (competitive carriers target <15%; many run 20–35%): https://www.apexcapitalcorp.com/blog/what-is-deadheading/

CPM and deadhead benchmarks move yearly (ATRI updates annually) and vary by equipment type and region — treat any specific number as `[verify-at-use]` and validate against the carrier's actual P&L and dispatch data (§3 #8).
