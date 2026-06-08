---
description: "Engineer features and fit a leakage-safe classical baseline: a dumb baseline to clear, regression / trees / gradient boosting, a cross-validation harness with transforms inside the fold, and the metric chosen from the decision."
argument-hint: "[the profiled dataset + the prediction goal + the cost structure of errors]"
---

You are running `/data-science-research:build-baseline-model`. Use `feature-and-modeling-engineer` + the `feature-engineering-and-modeling` skill.

## Steps
1. Set a dumb baseline (mean / majority class / simple linear) — the bar the model must clear; report lift over it, not just the absolute score.
2. Engineer features, deferring every fit-based transform (scaling/imputing/encoding) to inside the fold; wrap them in a `Pipeline`/`ColumnTransformer`.
3. Fit a classical model (regularized regression / tree / gradient boosting — XGBoost/LightGBM); classical before deep on tabular data.
4. Build a leakage-safe CV harness: split before any fit; stratified / `GroupKFold` / `TimeSeriesSplit` as the data demands; nested CV if tuning, and the test set is touched once.
5. Choose the metric from the decision and cost (PR-AUC / recall-at-precision / cost-weighted / calibration, not blind accuracy) and justify it; report the CV spread.
6. Emit the model experiment record + the Structured Output block (with `Uncertainty + caveats:` and `Leakage check:`). Route significance to `applied-statistics`, productionizing to `ml-engineering`.
