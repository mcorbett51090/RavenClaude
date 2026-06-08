# Changelog — retail-store-operations

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

## 0.2.0 — 2026-06-08

Depth pass. Same 3 agents / 3 skills / 3 commands / 2 templates / 1 hook — deeper knowledge, rules, scenarios, and a runnable calculator.

- **Best-practices 8 → 12** — added `shrink-is-a-diagnosable-leak` (now indexed), `gmroi-is-the-capital-lens`
  (turn alone doesn't prove earning — read the capital lens too), `every-metric-names-its-formula-and-window`
  (no metric ships without numerator / denominator / window), and `omnichannel-shares-inventory-not-the-playbook`
  (net the online claim on shared stock; route online economics to `ecommerce-dtc`). `best-practices/README.md` index updated.
- **Knowledge bank 2 → 5 Mermaid trees** — added shrink-leak diagnosis (operational vs. theft vs. vendor/admin),
  labor-% over plan (re-shape vs. cut heads), and reading the inventory vital signs (flow lens + capital lens).
  The dated 2026 metric/formula map (`[verify-at-build]`) is retained; last reviewed 2026-06-08.
- **Scenarios 2 → 5** — added `shrink-blamed-on-theft`, `labor-cut-craters-conversion`, and `fast-turn-sku-fails-gmroi`
  (9-field schema, `reviewed: false`). `scenarios/README.md` bank table updated.
- **Runnable calculator** — `scripts/retail_calc.py` (stdlib only, Python 3.8+, `ruff`-clean: F,E9,B,C4,I,UP):
  `gmroi` (gross margin $ / avg inventory cost), `sell-through` (units sold / received + weeks-of-supply), and
  `otb` (open-to-buy from planned sales / markdowns / EOM-BOM stock). A calculator, not a data source —
  decision-support, not financial advice.
- plugin.json bumped to **0.2.0**; description best-practices count 8 → 12 and calculator noted.

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
