# Changelog — retail-store-operations

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

## 0.1.0 — 2026-06-08

Initial release. The brick-and-mortar store-operations layer, distinct from the online/DTC channel.

- **3 agents** — `store-operations-lead` (store SOPs, labor scheduling against traffic, loss-prevention / shrink,
  the store P&L, customer experience), `merchandising-analyst` (planograms and space productivity, assortment /
  category management, pricing and markdown cadence, visual merchandising), `inventory-and-replenishment-planner`
  (inventory health, replenishment, sell-through, safety stock, open-to-buy, store-SKU allocation). Each carries the
  full scenario-authoring frontmatter.
- **3 skills** — `store-labor-and-pnl`, `merchandising-and-assortment`, `inventory-and-replenishment`.
- **Knowledge bank** — `retail-store-operations-decision-trees.md`: Mermaid trees (markdown-vs-hold on aged inventory,
  replenish-vs-OTB-cap on a buy, shrink-leak diagnosis, inventory vital signs) + a dated 2026 metric/formula map
  (sell-through / GMROI / weeks-of-supply / OTB; `[verify-at-build]`).
- **8 best-practices**, **3 commands** (`store-pnl-review`, `plan-markdown`, `replenishment-and-otb`),
  **2 templates** (store-P&L-and-labor plan, markdown-and-OTB plan), **1 advisory hook**
  (`check-retail-store-operations-anti-patterns.sh`; `RETAIL_STRICT=1` to make it blocking), and a **scenarios bank** (2 field notes).
- Seams: online channel → `ecommerce-dtc`; sourcing/vendors → `procurement-sourcing`; demand stats → `applied-statistics`;
  BI → `data-platform`. Requires `ravenclaude-core@>=0.7.0`.
