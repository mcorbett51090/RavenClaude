---
scenario_id: 2026-06-05-labor-flat-against-demand
contributed_at: 2026-06-05
plugin: restaurant-operations
product: foh-boh-ops
product_version: "n/a"
scope: likely-general
tags: [labor, scheduling, daypart, splh, service-line, throughput]
confidence: medium
reviewed: false
---

## Problem

A casual full-service unit was scheduling roughly the **same crew every shift** regardless of the day or daypart. Labor cost % looked acceptable on the weekly average, but it hid the real failure: **overstaffed slow lunches** burning labor against thin sales, and **understaffed weekend dinners** where the service line broke — long ticket times, walked guests, and a quietly rising turnover from a crushed Saturday crew. The owner's reflex was a flat headcount cut.

## Context

- Segment: casual, full-service, single unit, dinner-heavy with a weak weekday lunch.
- Constraint: the POS had per-daypart sales history but the schedule was built from a static template, not a demand forecast (§3 #4). Labor % was only ever read as a weekly number, never per daypart against that daypart's sales.
- The operator conflated "average labor % is fine" with "labor is right-sized." A flat cut would have deepened the weekend service failure while barely touching the overstaffed lunch — fixing the wrong shift (§3 #4, the labor-has-a-floor discipline).

## Attempts

- Tried: **scheduled to demand by daypart** (§3 #4, the schedule-to-demand skill) — forecast covers/sales per daypart from POS history, then staffed each daypart to its own labor target while **holding the service line** (a floor below which a labor cut costs more in walked guests + turnover than it saves). Read **sales per labor hour (SPLH)** per daypart instead of a blended weekly labor %. Result: pulled hours out of the overstaffed lunches, added them to the weekend dinner peak — net labor roughly flat, service and throughput up.
- Tried: checked **throughput / table turns** at the dinner peak (§3 #1 KPI set) — the bottleneck was a single understaffed station, not total headcount. Result: re-deployed within the shift rather than just adding bodies.
- Tried: resisted the flat cut. Result: avoided trading a labor point for a larger guest-experience and turnover cost (§3 #4).

## Resolution

Labor was **mis-allocated across dayparts, not too high in total** — the weekly average masked an overstaffed lunch and an understaffed dinner. The fix was scheduling to a per-daypart demand forecast against the service-line floor and reading **SPLH by daypart** rather than a blended weekly %. Throughput at the peak improved by re-deploying within the shift before adding hours.

**Action for the next consultant hitting this pattern:** never judge labor on the weekly blended % — it averages away the shifts that are actually broken (§3 #4). Forecast demand **by daypart**, staff each daypart to its own target with a hard service-line floor, and read **sales per labor hour by daypart**. A flat headcount cut is the wrong lever when the real problem is allocation.

**Sources (retrieved 2026-06-05):** labor-% ranges + payroll-as-share-of-cost trend — Toast *Restaurant Payroll Percentage* (https://pos.toasttab.com/blog/on-the-line/restaurant-payroll-percentage) and The Restaurant Warehouse *Average Restaurant Labor Cost Percentage* (https://therestaurantwarehouse.com/blogs/restaurant-equipment/restaurant-labor-cost-percentage); SPLH / table-turns definitions — TouchBistro *21 Restaurant Metrics* (https://www.touchbistro.com/blog/21-restaurant-metrics-and-how-to-calculate-them/). Specific targets are segment-dependent; treat any number as `[ESTIMATE]` and validate against the unit's actual daypart data (§3 #8).
