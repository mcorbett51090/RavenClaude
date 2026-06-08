---
description: "Design or reset store replenishment triggers for a SKU or SKU class: reorder point, safety stock with an explicit service-level target, and reorder quantity — after establishing inventory accuracy."
argument-hint: "[SKU or category, e.g. 'top-20 fast movers, 4-day DC lead time, target 98% in-stock, current OOS rate 8%']"
---

You are running `/retail-store-operations:set-replenishment`. Use the
`inventory-and-replenishment-analyst` discipline and the `inventory-and-replenishment` skill.

## Steps

1. Establish inventory accuracy first: review system on-hand vs. last physical count or cycle
   count. If accuracy is unknown or below 90%, the first output is a cycle-count plan, not a
   replenishment trigger.
2. Separate phantom inventory (system shows on-hand; shelf is empty) from true OOS. Flag
   which root causes are present and confirm they are addressed before setting new triggers.
3. Collect replenishment inputs: average daily sales (rolling 4–8 weeks), lead time in days,
   demand variability (σ of daily sales), vendor pack size, service-level target.
4. Calculate reorder point and safety stock using the formulas in the
   `inventory-and-replenishment` skill. State the service-level target explicitly (95% / 98% /
   99%) — never present safety stock without it.
5. Calculate weeks-of-supply at the reorder point using `scripts/retail_calc.py`
   `weeks_of_supply` mode to confirm the trigger is correctly sized.
6. Traverse the replenish-vs.-allocate tree in
   `knowledge/retail-store-operations-decision-trees.md` to confirm whether a store-initiated
   pull or a DC-push allocation is appropriate.
7. If BOPIS-eligible SKUs are in scope, add the BOPIS buffer logic and a cancel-rate KPI.
8. Emit the Structured Output block with handoffs to `merchandising-analyst` (if OOS is a
   planogram/assortment issue) and `loss-prevention-advisor` (if phantom inventory suggests
   unbookmarked shrink).
