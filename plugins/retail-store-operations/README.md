# retail-store-operations

The **brick-and-mortar retail store operations** layer. This plugin's team helps you run the
four-wall P&L, execute planograms, keep inventory accurate, schedule labor to the traffic curve,
and drive shrink to zero — across one store or a multi-store district.

> **The one-line philosophy:** the store floor is a system. Planogram compliance is revenue.
> Labor follows customers, not clocks. Shrink has a root cause. And inventory is one pool —
> BOPIS, ship-from-store, and walk-in draw from the same shelf.

---

## When to use this plugin (vs. its neighbours)

| You're asking… | Use |
|---|---|
| "Why is this store's sales/sqft below comp?" | **retail-store-operations** (`store-ops-lead`) |
| "Run a markdown analysis / reset a planogram" | **retail-store-operations** (`merchandising-analyst`) |
| "Out-of-stocks are up but system inventory looks fine" | **retail-store-operations** (`inventory-and-replenishment-analyst`) |
| "Build a labor schedule / fix labor % of sales" | **retail-store-operations** (`labor-scheduling-analyst`) |
| "Shrink rate jumped — root cause and playbook" | **retail-store-operations** (`loss-prevention-advisor`) |
| "Online channel, digital acquisition, DTC model" | `ecommerce-dtc` |
| "Upstream demand planning, network allocation" | `supply-chain-planning` |
| "Vendor selection, buying, PO negotiation" | `procurement-sourcing` |
| "Corporate P&L consolidation, financial reporting" | `finance` |

---

## What's inside

- **5 agents** — `store-ops-lead`, `merchandising-analyst`, `inventory-and-replenishment-analyst`,
  `labor-scheduling-analyst`, `loss-prevention-advisor`.
- **3 skills** — `merchandising-and-assortment`, `inventory-and-replenishment`, `labor-scheduling`.
- **3 commands** — `/retail-store-operations:plan-assortment`, `:set-replenishment`,
  `:build-labor-schedule`.
- **2 templates** — `planogram-brief`, `store-labor-model`.
- **Knowledge bank** — `knowledge/retail-store-operations-decision-trees.md`: Mermaid trees for
  markdown-or-hold, replenish-vs-allocate, and staff-to-traffic, plus a dated 2026 capability map
  of POS, merch/space, and workforce-management platforms.
- **6 best-practices** and **1 advisory hook** (flags schedules with no traffic basis, markdowns
  with no sell-through rationale, hard-coded figures without dates, and replenishment without
  service-level notes).
- **Calculator** — `scripts/retail_calc.py`: GMROI, sell-through %, shrink %, weeks-of-supply,
  conversion rate, sales per labor hour.

---

## House opinions (the short list)

1. GMROI, not just gross margin — return on inventory investment is the real measure.
2. Sell-through tells you whether to reorder or mark down.
3. Staff to the traffic curve, not the clock.
4. Shrink has a root cause — find it before you spend on prevention.
5. Planogram compliance is a revenue lever, not housekeeping.
6. Omnichannel inventory is one pool.

---

## Requires

`ravenclaude-core@>=0.7.0`. See [`CLAUDE.md`](CLAUDE.md) for the full team constitution and seams.
