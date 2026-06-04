---
name: reproducible-training
description: "Build reproducible training: a versioned prep->train->evaluate->register pipeline (not a notebook), experiment tracking (params/metrics/code/data/env), a model registry as source of truth, and leakage-free time-aware validation."
---

# Reproducible Training

## Pipeline, not a script
prep -> train -> evaluate -> **register**, with versioned inputs. A notebook isn't reproducible.

## Track everything
Params, metrics, **code version**, **data version**, environment. An untracked experiment is an indefensible result.

## Registry
Versioned models + metrics + lineage + model card = source of truth for promotion.

## Validate honestly
No target leakage, no future info, **time-aware splits** for temporal data, test set used once. A leaked metric is a production letdown with a delay. Significance -> `applied-statistics`.
