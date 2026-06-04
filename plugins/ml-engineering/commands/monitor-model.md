---
description: "Set up drift + decay monitoring with thresholds, alerts, and a retraining trigger that closes the loop to training."
argument-hint: "[deployed model + label availability]"
---

You are running `/ml-engineering:monitor-model`. Use `ml-monitoring-engineer` + the `model-monitoring` skill.

## Steps
1. Monitor input drift + prediction drift + performance (when labels arrive).
2. Define the retraining trigger up front; distinguish data vs concept drift.
3. Wire alerts (observability-sre); close the loop to training-pipeline-engineer.
4. Route drop-significance to applied-statistics.
5. Emit (from `templates/monitoring-plan.md`) + Structured Output block.
