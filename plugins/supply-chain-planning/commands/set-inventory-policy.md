---
description: "Set a segmented inventory policy: ABC/XYZ segmentation, service-level target approval, safety-stock calculation (z × σ_demand × √LT), reorder point, EOQ, and the working-capital tradeoff table."
argument-hint: "[SKU portfolio or segment, e.g. 'finished-goods portfolio, 500 SKUs, monthly review']"
---

You are running `/supply-chain-planning:set-inventory-policy`. Use the `inventory-optimization-engineer`
discipline and the `inventory-policy-and-safety-stock` skill.

## Steps

1. Confirm inputs are available: demand history (for CV calculation), unit costs, ordering cost,
   holding rate, supplier lead time + variability.
2. Segment the portfolio: ABC (revenue/volume Pareto) × XYZ (CV = σ/μ). Produce the 9-cell matrix.
3. Traverse `## Decision Tree: Inventory-policy selection` in
   `knowledge/supply-chain-planning-decision-trees.md` and assign replenishment method per cell.
4. Set service-level targets by ABC/XYZ cell. Document who approves each target.
5. Calculate safety stock per SKU (or per cell as representative): `SS = z × σ_demand × √LT`.
   Use the combined formula if σ_LT / LT > 0.2. Use `scripts/supply_calc.py` `safety_stock()`.
6. Calculate reorder point: `ROP = D̄ × LT + SS`.
7. Calculate EOQ: `EOQ = √(2DS/H)`. Use `scripts/supply_calc.py` `eoq()`.
8. Build the working-capital tradeoff table: CSL → SS units → SS investment ($) → annual carrying
   cost ($). Highlight the incremental cost of each 1% service-level step.
9. Emit the Structured Output block with all inputs documented and an approval note for the
   service-level targets.
