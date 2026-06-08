---
description: "Run a category assortment analysis: GMROI by SKU/category, sell-through vs. target, space-to-sales alignment, and a markdown-or-hold decision with a markdown ladder if applicable."
argument-hint: "[category name and context, e.g. 'women\\'s footwear, 38% sell-through, 9 weeks to season end, 14 wks of supply']"
---

You are running `/retail-store-operations:plan-assortment`. Use the `merchandising-analyst`
discipline and the `merchandising-and-assortment` skill.

## Steps

1. Collect the baseline inputs: sell-through rate, weeks-of-supply, gross margin %, average
   inventory at cost, and sales/linear-foot (or proxy). Flag any missing input explicitly.
2. Calculate GMROI using `scripts/retail_calc.py` `gmroi` mode (or manual: gross margin $ ÷
   avg inventory at cost). Classify by tier (< 1.0 / 1.0–2.0 / 2.0–3.5 / > 3.5).
3. Run the space-to-sales alignment check: rank SKUs by sales velocity; compare to shelf allocation.
   Flag over-spaced slow movers and under-spaced fast movers.
4. Traverse the markdown-or-hold decision tree in
   `knowledge/retail-store-operations-decision-trees.md` using the current sell-through, weeks
   remaining, weeks-of-supply, and seasonal vs. evergreen classification.
5. If the decision is "mark down," output a markdown ladder: discount at current sell-through,
   next trigger point (sell-through gate), and a liquidation floor.
6. Fill `templates/planogram-brief.md` with the space-to-sales reallocation if a planogram
   change is in scope.
7. Emit the Structured Output block with handoffs to `inventory-and-replenishment-analyst`
   (if replenishment triggers need adjustment) and `store-ops-lead` (if category changes
   have material four-wall impact).
