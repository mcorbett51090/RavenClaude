---
description: "Build a reproducible training pipeline with experiment tracking, a registry, feature consistency, and leakage-free validation."
argument-hint: "[model + data]"
---

You are running `/ml-engineering:build-training-pipeline`. Use `training-pipeline-engineer` + the `reproducible-training` skill.

## Steps
1. Build prep->train->evaluate->register with versioned inputs + tracking.
2. Ensure train/serve feature consistency (feature store/shared transform).
3. Validate leakage-free, time-aware; test set once.
4. Route significance to applied-statistics.
5. Emit (from `templates/training-pipeline.md`) + Structured Output block.
