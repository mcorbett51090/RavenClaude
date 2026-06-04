---
name: feature-store-consistency
description: "Prevent training-serving skew: compute features once via a feature store or shared transformation so training and serving use identical logic, with point-in-time correctness for temporal features and no leakage of future data."
---

# Feature Store / Train-Serve Consistency

## The #1 production ML bug
'Great offline, bad online' is almost always **training-serving skew** — features computed differently at serving time.

## Fix
Compute features **once** (feature store / shared transform); training and serving read the same logic.

## Point-in-time correctness
For temporal features, join as-of the event time — no future leakage into training. Otherwise the offline metric is a lie.
