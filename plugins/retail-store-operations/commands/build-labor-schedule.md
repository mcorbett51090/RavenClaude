---
description: "Build a traffic-curve-based labor schedule for a store or week: translate hourly traffic data into coverage requirements, shape shifts to demand, project labor % of sales and sales per labor hour, and flag predictive-scheduling compliance exposure."
argument-hint: "[store context, e.g. 'specialty apparel, 6-day week, target labor 18%, holiday week with Saturday peak index 2.4x']"
---

You are running `/retail-store-operations:build-labor-schedule`. Use the
`labor-scheduling-analyst` discipline and the `labor-scheduling` skill.

## Steps

1. Collect the traffic basis: hourly transaction counts or traffic counter data by day-of-week,
   minimum 4 weeks of history. If unavailable, state this explicitly and proceed with the
   best available proxy (transaction counts); flag the schedule as estimated.
2. Build the traffic curve: compute the hourly traffic index (hour volume ÷ daily average) by
   day-of-week. Identify peak blocks, valley blocks, and transition windows.
3. Apply coverage ratios for the store format: associates-per-customer-per-hour for the
   selling floor, manager-on-duty coverage, task-shift windows (receiving, stocking in valleys).
   State the format assumption and flag if ratios need calibration against conversion data.
4. Design shift shapes to match the traffic curve: opening coverage, peak layers, flex shifts
   on peak blocks, closing coverage. Assign task-heavy work to valley windows.
5. Sum total scheduled hours. Calculate projected labor % of sales using target weekly sales.
   Calculate sales per labor hour using `scripts/retail_calc.py` `sales_per_labor_hour` mode.
   If labor % exceeds target, identify which blocks to trim without cutting peak coverage.
6. Traverse the staff-to-traffic tree in
   `knowledge/retail-store-operations-decision-trees.md` if a gap between scheduled and
   required coverage is detected.
7. Scan the schedule for predictive-scheduling compliance flags: advance-notice window,
   on-call shifts, right-to-rest gaps (< 8 hours between shifts), minor-work-hour limits.
   Flag each with a "requires counsel review" note.
8. Fill `templates/store-labor-model.md` with the complete schedule, coverage table, labor
   metrics, and compliance flags.
9. Emit the Structured Output block with a handoff to `store-ops-lead` if labor % significantly
   impacts four-wall contribution.
