# Retail Store Operations

The **retail-store-operations** plugin — the brick-and-mortar store craft: how a physical store runs (SOPs, labor against traffic, shrink, the store P&L), what sits on the shelf at what price (planograms, assortment, markdown), and whether the right inventory is in the right store (sell-through, replenishment, open-to-buy) — distinct from the online/DTC channel, the vendor negotiation, the demand model, and the BI warehouse.

## Agents

- **`store-operations-lead`** — The store as a P&L: store SOPs and daily operations, labor scheduling against the conversion-weighted traffic curve, loss-prevention and shrink diagnosis (operational vs. theft vs. vendor/admin), the store P&L (sales, labor %, controllable expense), and customer experience / conversion. Runs the four walls as a margin engine, not a cost center.
- **`merchandising-analyst`** — The shelf: planograms and space productivity (sales / margin per facing or linear foot), assortment and category management, pricing and the markdown cadence tied to sell-through and weeks-of-supply, and visual merchandising. Treats shelf space as finite capital that every SKU must earn.
- **`inventory-and-replenishment-planner`** — The right stock in the right store: inventory health (sell-through / weeks-of-supply / GMROI), replenishment, safety stock sized to a named service level, open-to-buy (OTB), and store-SKU allocation. Plans at the store-SKU level because aggregate availability is a comforting lie during a stockout.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install retail-store-operations@ravenclaude
```

## Seams

- **The website, the online cart, online conversion, ship-from-store / BOPIS economics** → `ecommerce-dtc`; this team owns the four-wall store, they own the online channel. The shared-inventory seam is flagged here.
- **The vendor / supplier negotiation, sourcing terms, cost price** → `procurement-sourcing`; we consume the cost, they own the deal.
- **The demand forecast and the statistical safety-stock model** → `applied-statistics`; we set the service-level target, they build the model.
- **The BI dashboard, the warehouse, the pipeline behind the metrics** → `data-platform`; we define the metric, they build the reporting.
- **Employee PII (schedules, performance), payment data, loss-prevention surveillance** → `ravenclaude-core/security-reviewer` + `data-governance-privacy`.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`. Designed to be installed alongside `ecommerce-dtc`, `procurement-sourcing`, `applied-statistics`, and `data-platform`.
