# Data Science Research scenarios bank

> Unverified, dated, scope-tagged narratives from real data-science / research engagements. War stories of "we hit X
> problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real analysis work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `docs/best-practices/`; scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: data-science-research
product: <scikit-learn | xgboost | pandas | mlflow | dvc | generic | etc.>
product_version: "<version or unknown>"
scope: <likely-general | product-specific>
tags: [<tag>, ...]
confidence: <high | medium | low>
reviewed: false
---
```

## Current bank

| File | Tags | Corroborates |
|---|---|---|
| [`2026-06-08-target-leakage-too-good-to-be-true.md`](2026-06-08-target-leakage-too-good-to-be-true.md) | leakage, cross-validation, evaluation, pipeline | `leakage-is-the-cardinal-sin`, `cross-validate-a-single-split-lies` |
| [`2026-06-08-notebook-that-wouldnt-reproduce.md`](2026-06-08-notebook-that-wouldnt-reproduce.md) | reproducibility, seeds, environment, data-versioning | `reproducible-or-it-didnt-happen`, `every-finding-carries-its-uncertainty` |
| [`2026-06-08-accuracy-lied-on-imbalanced-fraud.md`](2026-06-08-accuracy-lied-on-imbalanced-fraud.md) | metric-choice, imbalance, evaluation, precision-recall | `the-metric-must-match-the-decision`, `cross-validate-a-single-split-lies` |
| [`2026-06-08-mean-imputation-erased-the-signal.md`](2026-06-08-mean-imputation-erased-the-signal.md) | missingness, imputation, eda, feature-engineering | `understand-missingness-before-imputing`, `engineer-features-as-of-prediction-time` |
| [`2026-06-08-deep-net-that-couldnt-beat-the-mean.md`](2026-06-08-deep-net-that-couldnt-beat-the-mean.md) | baseline, modeling, tabular, deep-learning | `baseline-before-the-fanciest-model`, `profile-before-you-model` |
