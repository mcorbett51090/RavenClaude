---
scenario_id: 2026-06-08-labor-cut-craters-conversion
contributed_at: 2026-06-08
plugin: retail-store-operations
product: generic
product_version: "unknown"
scope: likely-general
tags: [labor, scheduling, conversion, labor-percent, traffic]
confidence: high
reviewed: false
---

## Problem

A store running labor % over plan got a directive to cut hours to hit the weekly number. The manager cut across the board on a flat grid, which clipped coverage during the Saturday-afternoon and weekday-evening peaks. The labor report looked fixed the next week — labor % came back to plan — but comp sales softened and conversion at the door slipped. The store had traded a visible labor line for an invisible sales line, and the sales loss was bigger than the labor saved.

## Constraints context

- Schedule was a flat headcount grid, not shaped to the conversion-weighted traffic curve.
- The only metric anyone watched weekly was labor % of sales; conversion and traffic weren't on the same report.
- The cut was applied uniformly because uniform was easy, not because the dead hours were where the slack was.

## Attempts

- Tried: an across-the-board hours cut to make labor %. Backfired — it pulled coverage out of the peak, and the conversion loss (invisible on the labor report) exceeded the labor savings on the sales line.
- Tried: re-shaping instead of cutting — overlaying the door-counter traffic curve on the schedule, moving hours OUT of the genuinely dead morning hours and INTO the peak. This recovered most of the labor % with no net headcount cut and protected conversion.
- Tried: putting conversion and traffic on the same weekly review as labor %, so the trade was explicit on every schedule change rather than discovered a week later in soft comps.

## Resolution

The store re-shaped the schedule to the conversion-weighted traffic curve rather than cutting heads, recovering labor % primarily by moving hours from dead hours into the peak. Peak coverage was treated as protected — never the lever used to make a weekly labor number. The weekly review was changed to show labor %, conversion, and traffic together so the labor-vs-conversion trade was named on every change.

## Lesson

Labor follows traffic, not a flat grid, and labor % over plan is usually a scheduling-shape problem before it's a headcount problem. Re-shape against the traffic curve before cutting heads, and never cut peak labor to make a weekly labor % — the lost conversion is invisible on the labor report but real on the sales line.
