---
name: feature-engineering-and-modeling
description: "Engineer features and fit, select, and honestly evaluate classical models on tabular data: build leakage-aware features, set a baseline, choose between regression / trees / gradient boosting, build a leakage-safe cross-validation harness with every transform fit inside the fold, and pick the metric from the decision and its cost structure."
---

# Feature Engineering & Modeling

## Baseline first
Set a dumb baseline (mean / majority class / simple linear) — it's the bar every model must clear. A model that barely beats it is a finding about the data, not a win. Report the lift, not just the absolute score.

## Engineer features leakage-aware
Encodings, interactions, transforms, binning, time/group aggregates — but defer every **fit-based** transform (scaling, imputing, target encoding) to inside the cross-validation fold. Computing them on the full data before the split leaks the test set.

## Classical before deep
For tabular data: regularized regression and shallow trees for interpretability; gradient boosting (XGBoost / LightGBM) as the strong default. Reach for deep learning / AutoML only when it earns its complexity and operational cost.

## Build a leakage-safe CV harness
Split before any fit. Wrap transforms in a `Pipeline`/`ColumnTransformer` so they stay inside the fold by construction. Use stratified folds for imbalance, `GroupKFold` for grouped data, `TimeSeriesSplit` for temporal data. Tuning hyperparameters? Nested CV, and the test set is touched once.

## Choose the metric from the decision
The wrong metric makes a bad model look good — accuracy on imbalanced classes, R² on a ranking problem, a symmetric loss for asymmetric cost. Derive the metric from the cost structure (PR-AUC, recall-at-precision, cost-weighted loss, calibration) and justify it.

## Report honestly
Report the CV **spread**, not a single-split point estimate; the lift over baseline; and the leakage check. Feature importance is association, not causation — route causal and significance claims to `applied-statistics`.

## Output
A model experiment record: the features, the baseline, the model, the CV scheme, the metric and its justification, the leakage check, and the honest score with its spread. Hand productionizing to `ml-engineering` and significance to `applied-statistics`.
