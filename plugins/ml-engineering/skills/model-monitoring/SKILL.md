---
name: model-monitoring
description: "Keep production models honest: monitor input/data drift, prediction/concept drift, and performance decay (when labels arrive); define the retraining trigger up front (schedule/threshold/drop); alert on model health; and close the loop to retraining."
---

# Model Monitoring

## Three signals
- **Input/data drift** — the world changed (early warning, no labels needed).
- **Prediction/concept drift** — the model's outputs / the input->output relation shifted.
- **Performance** — the truth, but only when **labels arrive** (often delayed).

## Retraining trigger (decide up front)
Schedule, drift threshold, or performance drop. Not after accuracy quietly fell for a quarter.

## Operate it
Thresholds + alerts (with observability-sre); a drift alert must trigger a **documented response** + the retraining loop. Significance of a drop -> `applied-statistics`.
