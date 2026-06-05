# ML Engineering scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) ML/MLOps engagements. War stories of "the model hit X problem in production, here was the situation, these were the constraints, we tried A/B/C, D was the fix." Enabled as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — field notes from real ML-engineering work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `best-practices/`; scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: ml-engineering
product: <mlflow | feast | sagemaker | vertex | kserve | seldon | evidently | python | generic | etc.>
product_version: <"2026.04" | "unknown">
scope: tenant-specific | version-specific | likely-general
tags: [3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Constraints context
## Attempts
## Resolution
```

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-training-serving-skew-feature-source.md`](2026-06-05-training-serving-skew-feature-source.md) | likely-general | training-serving-skew, feature-store, online-offline, point-in-time, parity | high |
| [`2026-06-05-drift-detection-and-retrain-trigger.md`](2026-06-05-drift-detection-and-retrain-trigger.md) | likely-general | drift, psi, concept-drift, retrain-trigger, monitoring | medium |
| [`2026-06-05-temporal-leakage-inflated-offline-metric.md`](2026-06-05-temporal-leakage-inflated-offline-metric.md) | likely-general | leakage, temporal-split, validation, offline-online-gap, label-window | high |
| [`2026-06-05-canary-rollback-bad-model-version.md`](2026-06-05-canary-rollback-bad-model-version.md) | likely-general | canary, rollback, registry, shadow, serving-version | medium |

## Promotion path

When ≥2 independent scenarios (different `contributed_at` quarters, different engagements) corroborate the same finding, an agent proposes promotion to a `knowledge/` decision tree or a `best-practices/` rule. As of this bank's first version, promotion is manual and the scenarios stay in place after a rule is canonicalized — the narrative remains useful context.

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank or the cross-cutting house opinions in [`../CLAUDE.md`](../CLAUDE.md) §2. The most-likely-to-benefit specialists — `training-pipeline-engineer`, `model-serving-engineer`, `ml-monitoring-engineer` — should check the bank when a situation matches.
