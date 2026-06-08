---
name: inventory-and-replenishment
description: "Keep the right stock in the right store: read inventory health by sell-through / weeks-of-supply / GMROI, size replenishment and safety stock to a named service level, compute and protect open-to-buy, and allocate at the store-SKU level instead of the comforting aggregate."
---

# Inventory and Replenishment

## Read the vital signs, not the units
Judge inventory by sell-through %, weeks-of-supply (WOS), and GMROI — never raw on-hand units. Normalize on-hand to the demand rate (WOS) before calling a position over- or under-stocked. GMROI answers whether the inventory earns its carrying cost. State the window on every metric.

## Size safety stock to a named service level
Size the buffer to a target in-stock / service level against demand variability and lead-time variability — and state the target. "More buffer" with no target is trapped cash with a story; raising the service level has a named cash cost, so make the trade explicit. Set the reorder point and replenishment quantity off that model.

## Open-to-buy is a budget
OTB = planned sales − planned markdowns + target ending inventory − (on-hand + on-order). If OTB is exhausted or negative, you're over-bought — re-plan or clear before buying more. Over-buying pre-commits the markdown, the most expensive mistake in retail.

## Allocate at the store-SKU level
Aggregate availability is a comforting lie during a stockout. Drill to store-SKU: a stocked-out store next to a 14-week-of-supply store is a transfer sized by WOS plus a per-store replenishment reset, not a "total is fine".

## The forecast is an input you consume
Set the service-level target and the seasonality assumption; route the demand-variability model to `applied-statistics`. Vendor lead time / MOQ / cost route to `procurement-sourcing`.

## Output
An inventory plan: the sell-through / WOS / GMROI read, the service-level-sized replenishment and safety stock, the OTB calc, and the store-SKU allocation/transfer — each naming trapped cash or lost sales. Hand the markdown/cut of overstock to `merchandising-analyst`.
