---
scenario_id: 2026-06-08-aged-inventory-was-burning-floorplan
contributed_at: 2026-06-08
plugin: automotive-dealership
product: inventory
product_version: "n/a"
scope: likely-general
tags: [days-supply, floorplan, aged-inventory, carrying-cost]
confidence: medium
reviewed: false
---

## Problem

A used-car manager held aged units waiting for full gross, and the lot looked well-stocked. The risk: aged inventory burns floorplan interest, holdback, and depreciation daily, and a high days-supply quietly converts into carrying-cost cash that can exceed the gross being protected (§3 #2).

## Context

- Store: new + used, used desk holding for gross.
- Constraint: days-supply = units ÷ daily sales rate; floorplan cost accrues per unit per day (§3 #2).
- The manager reasoned from the gross-per-unit target, not the carrying cost.

## Attempts

- Tried: **computed days-supply and floorplan carrying cost** (`automotive_dealership_calc.py days-supply`). Outcome: days-supply ran well over target and the monthly floorplan drag was material.
- Tried: **compared the carry on aged units against the gross being held for.** Outcome: the depreciation + floorplan on the oldest units was eroding faster than the gross would ever accrue (§3 #2).
- Tried: **flagged the units past target days-supply** for price-to-turn. Outcome: a clear aged-unit action list.

## Resolution

The fix was a **price-to-turn policy on units past target days-supply**, freeing floorplan cash and turning the lot — not holding for a gross that depreciation was outrunning. The output was the days-supply read, the floorplan cost, and the aged-unit list.

**Action for the next consultant hitting this pattern:** **read days-supply and floorplan carry before holding for gross.** Aged units burn carrying-cost cash that can exceed the gross protected; price-to-turn past target. See Tree 1 and the `automotive_dealership_calc.py` `days-supply` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
