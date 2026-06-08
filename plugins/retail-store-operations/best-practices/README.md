# Retail-store-operations best-practices

Atomic, enforceable rules the retail-store-operations agents apply. Each file is one rule with a short rationale; the agents cite them by filename. Canonical decision logic lives in [`../knowledge/retail-store-operations-decision-trees.md`](../knowledge/retail-store-operations-decision-trees.md); these rules are the always-on priors.

| Rule | Gist |
|---|---|
| store-is-a-pnl-not-a-cost-center | Every tactic lands on a store P&L line |
| labor-follows-traffic-not-a-grid | Schedule to the conversion-weighted traffic curve |
| shelf-space-is-finite-capital | Measure space productivity; every SKU earns its facings |
| markdown-is-a-decision-not-a-default | Trigger markdowns on sell-through + weeks-of-supply |
| sell-through-and-wos-are-the-vital-signs | Judge inventory by flow, not raw on-hand units |
| open-to-buy-is-a-budget | Cap forward commitment against planned sales + ending inventory |
| allocate-at-the-store-sku-level | Aggregate availability hides a stockout next to overstock |
| safety-stock-buys-a-named-service-level | Size the buffer to a stated service / in-stock target |
| shrink-is-a-diagnosable-leak | Split shrink into operational / theft / vendor-admin before fixing |
| gmroi-is-the-capital-lens | Turn alone doesn't prove earning — read GMROI too |
| every-metric-names-its-formula-and-window | No metric ships without numerator, denominator, window |
| omnichannel-shares-inventory-not-the-playbook | Net the online claim on shared stock; route online economics out |
