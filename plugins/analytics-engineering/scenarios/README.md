# Analytics Engineering scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) analytics-engineering engagements — dbt / SQL / warehouse war stories of "the pipeline produced X wrong number, here was the situation, these were the constraints, we tried A/B/C, D fixed it." Added in the value-add build-out (2026-06-05).

This directory holds **scenarios** — field notes from real transform-layer work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Canonical knowledge lives in [`../knowledge/analytics-engineering-decision-trees.md`](../knowledge/analytics-engineering-decision-trees.md) and [`../best-practices/`](../best-practices/); scenarios never replace it. The "Resolution" here is a modeling/testing move plus a verified outcome (the wrong number went away, the test caught it next time), not a generic tip.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: analytics-engineering
product: <dbt-core | dbt-cloud | snowflake | bigquery | redshift | databricks | generic | etc.>
product_version: <"1.8" | "unknown">
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

> **Privacy:** scenarios carry **no** client-identifying info, no real warehouse names, no row-level data, and no revenue figures attributable to a named org. Row counts and dollar amounts are illustrative ranges, marked `[ESTIMATE]`, or carry a public source. This mirrors the marketplace `/wrap` scrub discipline.

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-fan-out-join-double-counting.md`](2026-06-05-fan-out-join-double-counting.md) | likely-general | fan-out, join, grain, double-counting, revenue, semantic-layer | high |
| [`2026-06-05-incremental-late-arriving-data.md`](2026-06-05-incremental-late-arriving-data.md) | likely-general | incremental, late-arriving, lookback, merge, watermark, append | high |
| [`2026-06-05-semantic-layer-metric-drift.md`](2026-06-05-semantic-layer-metric-drift.md) | likely-general | semantic-layer, metric-drift, revenue, single-definition, governance | high |
| [`2026-06-05-test-coverage-gap-silent-corruption.md`](2026-06-05-test-coverage-gap-silent-corruption.md) | likely-general | data-quality, test-coverage, relationships, freshness, ci-gate | medium |

## Promotion path

When ≥2 independent scenarios (different `contributed_at` quarters, different engagements) corroborate the same finding, an agent proposes promotion to a [`../knowledge/`](../knowledge/) decision tree or [`../best-practices/`](../best-practices/). As of this bank's first version, promotion is manual and the scenarios stay in place after a rule is canonicalized — the narrative remains useful context.

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank or a freshly-verified warehouse fact. The likeliest beneficiaries are `analytics-engineer` (modeling/incremental scenarios), `semantic-layer-engineer` (metric-drift), and `data-quality-testing-engineer` (test-coverage).
