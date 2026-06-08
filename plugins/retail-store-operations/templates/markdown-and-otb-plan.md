# Markdown and Open-to-Buy Plan

> Output of `merchandising-analyst` / `inventory-and-replenishment-planner` and the merchandising / inventory skills.
> A markdown with no sell-through trigger, or a buy with no open-to-buy cap, is not ready to ship.

## 1. Inventory health read

| SKU / Category | Sell-through % (window) | Weeks-of-supply | GMROI | Position |
|---|---|---|---|---|

_State the window on every metric. Flag any aggregate-vs-store-SKU imbalance (stockout next to overstock)._

## 2. Markdown cadence (sell-through triggered)

| Step | Trigger (sell-through / WOS) | Depth | Timing | Margin vs. carrying-cost trade |
|---|---|---|---|---|
| First markdown | | <usually shallow> | | <first is the cheapest> |
| Step-down | | | | |
| Terminal clearance | | | | |

_If slow sell-through is an assortment problem (wrong SKU), route to rationalization before discounting._

## 3. Open-to-buy calculation

| Component | $ |
|---|---|
| Planned sales | |
| − Planned markdowns | |
| + Target ending inventory | |
| − On-hand | |
| − On-order | |
| **= Open-to-buy remaining** | |

_If OTB is exhausted or negative → stop, you're over-bought. Re-plan or clear before buying more._

## 4. Replenishment + allocation

- **Service / in-stock level target:** <stated explicitly>
- **Safety stock (sized to that target):** <vs. demand + lead-time variability>
- **Reorder point / replenishment qty:** <>
- **Store-SKU transfer / re-allocation:** <from overstocked to stocked-out, sized by WOS>
- **Trapped-cash trade:** <cost of the buffer / the over-buy>

## 5. Build handoff

| What | Routed to |
|---|---|
| The demand-variability / elasticity model | `applied-statistics` |
| Vendor lead time / MOQ / cost price | `procurement-sourcing` |
| Floor execution of the planogram / markdown | `store-operations-lead` |
| The inventory / OTB / merchandising dashboard | `data-platform` |

---

```
Status: ...
Files changed: ...
P&L impact: ...
Assumptions & data gaps: ...
Handoff to neighbours: ...
Open questions: ...
Grounding checks performed: ...
```
