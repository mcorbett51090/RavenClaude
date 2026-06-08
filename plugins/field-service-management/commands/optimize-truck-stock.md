---
description: "Optimize truck-stock for a field-service technician fleet — tier the parts list, set fill-rate targets by SLA tier, rank the add/remove list by first-time-fix payback, and produce reorder points for universal-carry parts."
argument-hint: "[context, e.g. 'HVAC commercial fleet, 12 techs, 4h premium SLA, parts-delay failures at 22% of first-time-fix misses']"
---

You are running `/field-service-management:optimize-truck-stock`. Use the
`parts-and-inventory-analyst` discipline and the `truck-stock-and-parts` skill.

## Steps

1. Traverse the stock-the-part-or-not tree in `knowledge/fsm-decision-trees.md` for the
   equipment types in scope. Establish which parts are candidates for each tier (universal-carry,
   tech-specialty, special-order).

2. Set the fill-rate target by SLA tier (≥ 95% for premium, ≥ 90% for standard, ≥ 85% for
   basic). Use `scripts/fsm_calc.py` `truck_stock_fill_rate()` to calculate the current fill
   rate from usage and stockout data if provided.

3. Build the parts-delay failure analysis: extract all first-time-fix misses classified as
   "parts unavailable." For each part causing misses, calculate:
   - Monthly miss count (fleet-wide)
   - Cost per miss (return-visit labor + SLA penalty if applicable)
   - Monthly carrying cost of adding to universal-carry
   - Payback period (monthly miss cost ÷ monthly carry cost)

   Rank the add list by payback period. Flag parts with payback < 3 months as strong add candidates.

4. Identify rationalization candidates: parts with zero or near-zero usage in the last 6 months.
   For each, model the fill-rate impact of removal. Only recommend removal if fill-rate impact is
   negligible (< 0.5% change in fill rate for the relevant SLA tier).

5. Calculate reorder points for universal-carry parts using the reorder-point formula in
   `skills/truck-stock-and-parts/SKILL.md` (or a simplified 20%/2× rule if variance data is
   unavailable).

6. Recommend the pre-dispatch parts-readiness check design for special-order jobs.

7. Emit the Structured Output block with the add list (ranked by payback), the remove list (with
   fill-rate impact), the reorder points, and handoffs to `technician-productivity-analyst` to
   confirm first-time-fix impact of changes.
