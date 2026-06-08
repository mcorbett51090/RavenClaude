# supply-chain-planning

The **plan layer between buy and move**. This plugin's team helps you build and run the S&OP/IBP
cycle, produce defensible demand forecasts with measured accuracy, set inventory and safety-stock
policies that balance service level against working capital, and design the planning architecture
(network echelons, make-vs-buy positioning, planning calendar).

> **The one-line philosophy:** good supply-chain planning converts uncertainty into managed
> variability — with an accurate, bias-tracked forecast, a safety stock sized to the real
> distribution of errors, and a monthly S&OP that reconciles demand and supply before the problems
> become fires.

## When to use this plugin (vs. its neighbours)

| You're asking… | Use |
| --- | --- |
| "Build a demand forecast / measure forecast accuracy" | **supply-chain-planning** (`demand-planning-analyst`) |
| "Set safety-stock levels / inventory policy / service-level targets" | **supply-chain-planning** (`inventory-optimization-engineer`) |
| "Design or facilitate the monthly S&OP / IBP cycle" | **supply-chain-planning** (`sop-process-lead`) |
| "Design our planning architecture / make-vs-buy / planning calendar" | **supply-chain-planning** (`supply-chain-planner`) |
| "Execute purchase orders / manage suppliers / negotiate terms" | `procurement-sourcing` |
| "Move the freight / manage transport execution" | `freight-forwarding-sales` / `fleet-logistics` |
| "Run formal statistical significance tests on forecast models" | `applied-statistics` |
| "Build a BI dashboard on inventory / supply-chain KPIs" | `data-platform` |

## What's inside

- **4 agents** — `supply-chain-planner`, `demand-planning-analyst`,
  `inventory-optimization-engineer`, `sop-process-lead`.
- **3 skills** — `demand-forecasting`, `inventory-policy-and-safety-stock`, `sop-process`.
- **3 commands** — `/supply-chain-planning:build-demand-forecast`,
  `:set-inventory-policy`, `:run-sop-cycle`.
- **2 templates** — `sop-deck`, `safety-stock-model`.
- **Knowledge bank** — `knowledge/supply-chain-planning-decision-trees.md`: Mermaid trees for
  forecast-method selection, inventory-policy selection, and make-vs-buy/supply-network positioning,
  plus a dated 2026 capability map.
- **6 best-practices** and **1 advisory hook** (flags ungrounded safety-stock numbers, forecasts
  without accuracy metrics, hard-coded demand figures, and unqualified "just-in-time" language).
- **`scripts/supply_calc.py`** — stdlib calculator: EOQ, safety stock, reorder point, fill rate,
  MAPE and bias.

## House opinions (the short list)

1. Forecast accuracy is always measured — MAPE and bias together.
2. Safety stock covers variability, not the average demand.
3. S&OP reconciles demand and supply every single month.
4. Segment ABC/XYZ before setting policy.
5. The bullwhip is real — dampen it.
6. Service level is a deliberate choice with a cost.

## Requires

`ravenclaude-core@>=0.7.0`. See [`CLAUDE.md`](CLAUDE.md) for the full team constitution and seams.
