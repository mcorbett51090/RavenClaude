---
description: "Build a demand forecast: clean demand history, traverse the forecast-method tree, fit the statistical baseline, measure MAPE and bias on a holdout period, design the consensus overlay, and hand off the error distribution for safety-stock sizing."
argument-hint: "[SKU or product family, e.g. 'widget-A monthly demand, 36 periods of history, no known seasonality']"
---

You are running `/supply-chain-planning:build-demand-forecast`. Use the `demand-planning-analyst`
discipline and the `demand-forecasting` skill.

## Steps

1. Confirm the demand signal (actual orders / POS — not shipments) and the history length. If
   < 6 clean periods, flag and switch to analogue or judgement-based method.
2. Clean the history: identify and document promotions, one-off orders, and stock-out periods.
3. Traverse `## Decision Tree: Forecast-method selection` in
   `knowledge/supply-chain-planning-decision-trees.md` and select the method.
4. Fit the statistical baseline on the training set; measure MAPE and bias on the holdout
   (last 3–6 periods). Use `scripts/supply_calc.py` `mape_bias()`.
5. If seasonality is detected, compute seasonal indices and document the base year.
6. Design the consensus overlay process: who provides overrides, what documentation is required,
   how post-audit will work.
7. Package the output: method + parameters, MAPE/bias results, seasonal indices if applicable,
   forecast error σ for safety-stock sizing, and the consensus overlay log template.
8. Emit the Structured Output block and hand off the error distribution to
   `inventory-optimization-engineer`.
