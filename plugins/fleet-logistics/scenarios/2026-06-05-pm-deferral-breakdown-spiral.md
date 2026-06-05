---
scenario_id: 2026-06-05-pm-deferral-breakdown-spiral
contributed_at: 2026-06-05
plugin: fleet-logistics
product: maintenance
product_version: "n/a"
scope: likely-general
tags: [preventive-maintenance, downtime, maintenance-cpm, roadside, reactive-repair]
confidence: medium
---

## Problem

A growing carrier's repair spend was "exploding" and the owner wanted to renegotiate parts pricing or change vendors. The actual driver was a **deferred-PM spiral**: to keep trucks earning during a tight freight stretch, the shop had been pushing PM intervals, which converted scheduled downtime into roadside failures — each one a tow, a premium emergency repair, a missed-load penalty, and a stranded driver. The carrier was paying several times more per repair than a planned service would have cost, plus the downtime.

## Context

- Segment: for-hire truckload, ~25 trucks, aging mid-life tractors.
- Constraint: the carrier tracked total repair dollars but **not maintenance CPM** and **not planned-vs-unplanned split**, so "repair is up" looked like a price problem rather than a deferral problem. There was no unplanned-downtime-rate metric at all.
- The owner conflated "repair bill is high" (a P&L symptom) with "parts/labor got expensive" (one of several causes). The PM-deferral feedback loop was invisible without the planned/unplanned split.

## Attempts

- Tried: **split repair spend into planned vs. unplanned** and computed **maintenance CPM**. Outcome: the unplanned share had ballooned — the spend wasn't a price increase, it was reactive emergency work. The literature frames the gap starkly: reactive maintenance commonly runs **3–9x** the cost of planned PM, emergency repairs cost **30–50% more** and often add towing + rush parts, and a single unexpected engine failure can sideline a truck for days at **$5,000–$12,000** in repairs. [`../scripts/fleet_calc.py`](../scripts/fleet_calc.py) `replace-repair` folds the downtime cost into a per-mile figure.
- Tried: **instrumented unplanned-downtime rate** (downtime days ÷ available days per unit) and attached a dollar cost to a downtime day — industry framing puts unplanned downtime at roughly **$448–$760 per vehicle per day**, higher for larger units. Outcome: the downtime cost alone justified restoring PM intervals.
- Tried: **restored PM-to-CPM discipline** — pulled deferred units back onto interval, and used the maintenance-CPM-vs-replacement-CPM crossover to flag the two worst tractors as replacement candidates rather than bottomless repair sinks (§3 #5). Outcome: unplanned events fell, and the replacement calls were made on the cost crossover, not on age alone.

## Resolution

The "exploding repair cost" was a **deferred-PM spiral**, not a parts-price problem: pushed PM intervals turned cheap scheduled service into expensive roadside failures plus downtime. The fix was to restore PM intervals, instrument maintenance CPM and unplanned-downtime rate, and route the genuinely worn-out units to the replacement-timing tree.

**Action for the next consultant hitting this pattern:** when repair spend rises, **split planned vs. unplanned and read maintenance CPM before negotiating price.** A deferred PM is a roadside failure plus a missed load — preventive maintenance is cheaper than the breakdown (§3 #5). Attach a dollar cost to a downtime day, and use the maintenance-CPM-vs-replacement-CPM crossover (the "Truck Replacement Timing" tree in [`../knowledge/fleet-decision-trees.md`](../knowledge/fleet-decision-trees.md), and `fleet_calc.py replace-repair`) to separate "service it" from "replace it."

**Sources (retrieved 2026-06-05):**
- FleetRabbit — *Preventive vs Reactive Fleet Maintenance: The True Cost Comparison* (reactive 3–9x preventive; emergency repairs 30–50% more): https://fleetrabbit.com/industry/transportation-and-logistics/preventive-vs-reactive-fleet-maintenance-cost-comparison
- HeavyVehicleInspection — reactive vs preventive ($5,000–$12,000 engine failure; days of downtime): https://heavyvehicleinspection.com/article/preventive-maintenance-vs-reactive
- Mudflap — reactive-maintenance cost per mile + downtime ($448–$760/vehicle/day): https://www.mudflapinc.com/resources/reactive-maintenance-cost-per-mile

Cost multiples and downtime-per-day figures vary by fleet, equipment age, and lane — treat any specific number as `[verify-at-use]`/`[ESTIMATE]` and validate against the carrier's actual maintenance records (§3 #8).
