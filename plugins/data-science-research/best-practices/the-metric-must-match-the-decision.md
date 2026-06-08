# Choose the metric from the decision, not from habit

The wrong metric makes a bad model look good: accuracy on imbalanced classes, R² on a ranking problem, a symmetric loss when the cost of errors is asymmetric. Derive the metric from the decision and its cost structure — PR-AUC or recall-at-precision for rare positives, a cost-weighted loss for asymmetric error, calibration when probabilities are consumed downstream — then justify the choice. Pair the model's metric with the baseline's on the same metric so "better" is measured against the right bar.
