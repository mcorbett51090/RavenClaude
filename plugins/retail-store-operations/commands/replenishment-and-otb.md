---
description: "Size replenishment and safety stock to a named service level and compute open-to-buy: read inventory health, set the reorder point, cap forward commitment against OTB, and fix store-SKU allocation."
argument-hint: "[SKU/category/store + on-hand + on-order + demand + lead time + planned sales/markdowns/ending inventory]"
---

You are running `/retail-store-operations:replenishment-and-otb`. Use `inventory-and-replenishment-planner` + the `inventory-and-replenishment` skill.

## Steps
1. Read inventory health: sell-through %, weeks-of-supply, GMROI by SKU/store — not raw on-hand units. State the window. Flag any aggregate-vs-store-SKU imbalance (stockout next to overstock).
2. Size safety stock to a NAMED service / in-stock level against demand and lead-time variability; set the reorder point and replenishment quantity. State the trapped-cash cost of the buffer.
3. Compute open-to-buy: planned sales − planned markdowns + target ending inventory − (on-hand + on-order). If exhausted/negative, say stop — re-plan or clear before buying more.
4. If a store-SKU imbalance exists, size the transfer/re-allocation by weeks-of-supply and reset per-store replenishment.
5. Route the seams: demand-variability model → `applied-statistics`; vendor lead time / MOQ / cost → `procurement-sourcing`; markdown/cut of overstock → `merchandising-analyst`.
6. Emit the replenishment-and-OTB plan + the Structured Output block (with `P&L impact:` and `Handoff to neighbours:`).
