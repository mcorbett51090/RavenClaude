---
scenario_id: 2026-06-05-irrigation-water-cost
contributed_at: 2026-06-05
plugin: precision-agriculture
product: irrigation
product_version: "n/a"
scope: segment-specific
tags: [irrigation, soil-moisture-sensor, water-cost, scheduling, roi]
confidence: medium
reviewed: false
---

## Problem

An irrigated grower was scheduling by calendar and feel — running the pivot on a fixed rotation regardless of soil moisture or recent rain — and pumping cost (energy + water) had become a large, controllable line. The question was whether soil-moisture-sensor-driven scheduling would cut enough water and pumping hours to pay for the sensors and still protect yield, or whether it was a tech purchase chasing a saving too small to matter on this operation.

## Context

- Segment: irrigated row-crop (segment-specific — applies to growers who pump, not dryland), center-pivot, energy-priced pumping, ~600 irrigated acres.
- Constraint: scheduling drives both water cost and yield — over-watering wastes pumping dollars and can leach N; under-watering at a critical growth stage costs yield. The controllable lever is **applying the right amount at the right time** (§3 #3), and the saving has to be measured per acre-inch against the sensor cost.
- The grower had no soil-moisture data in the root zone, so every irrigation decision was a guess about whether the crop actually needed water.

## Attempts

- Tried: framed the decision as a **per-acre-inch pumping-cost saving vs sensor cost** ROI, not a yield play. Extension and field data put soil-moisture-sensor scheduling savings in a meaningful band — properly calibrated sensors cited at large water-use reductions, and an IoT-scheduled system at roughly **~29% less water and ~16% fewer pumping hours** vs conventional weather-based scheduling [verify-at-use, study-specific]. Sensor cost ranges widely (low-cost prototypes ~$60 to commercial multi-sensor installs) [verify-at-use].
- Tried: tied the saving to the operation's **actual pumping cost per acre-inch** (energy price × pumping efficiency) so the payback is computed on this grower's water cost, not a generic percentage — a 29% cut on cheap surface water pays back far slower than on expensive deep-well energy pumping.
- Tried: protected the yield side — the goal is to cut *unnecessary* irrigations (right amount, right time), not to under-water the crop at a critical stage; the sensors inform when the root zone genuinely needs water rather than blanket-cutting applications.

## Resolution

The deliverable was a **sensor-scheduling payback model**: water + pumping-hour saving (a defensible percentage of current applications) × this operation's pumping cost per acre-inch, against the installed sensor cost — with the yield-protection caveat that the saving comes from skipping unneeded irrigations, not from deficit-irrigating. On a high-energy-cost pumping operation the payback was quick; the grower's lesson was that **irrigation ROI is a per-acre-inch pumping-cost saving measured against sensor cost, and it scales with how expensive your water actually is.**

**Action for the next consultant hitting this pattern:** compute irrigation-tech ROI as **(water + pumping-hour saving %) × pumping cost per acre-inch − sensor cost**, using the operation's *real* pumping cost, never a generic percentage. The saving must come from timing (right amount, right time — §3 #3), not from under-watering at critical stages. The [`../scripts/ag_calc.py`](../scripts/ag_calc.py) `breakeven`/`input-cost` modes frame the cost side; this is segment-specific to growers who pump.

**Sources (retrieved 2026-06-05):**
- Michigan State University Extension — _Utilizing Soil Moisture Sensors for Efficient Irrigation Management_ (sensor types, costs, water-use reduction): https://www.canr.msu.edu/resources/utilizing-soil-moisture-sensors-for-efficient-irrigation-management
- U. of Minnesota Extension — _Soil moisture sensors for irrigation scheduling_: https://extension.umn.edu/irrigation/soil-moisture-sensors-irrigation-scheduling
- OSU Extension — _Soil moisture monitoring to support irrigation scheduling_ (EM-9868): https://extension.oregonstate.edu/catalog/em-9868-soil-moisture-monitoring-support-irrigation-scheduling

Water-saving percentages, sensor costs, and pumping cost per acre-inch are highly site-, crop-, and energy-price-dependent — treat every figure as `[verify-at-use]` and recompute against the grower's own pumping cost and irrigation records (§3 #3, #8).
