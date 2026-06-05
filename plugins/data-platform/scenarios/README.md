# Data-platform scenarios bank

> Unverified, dated, scope-tagged narratives from real dashboard-engagement work. War stories of "we hit X problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real data-platform engagements (the four-layer DB / ELT / dashboard / embed stack). Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) (a 24-doc bank + the decision-tree file) and [`../best-practices/`](../best-practices/); scenarios never replace it.

**Privacy:** scenarios carry **no client/tenant PII** and **no credentials** (the same secrets-stay-a-reference rule the plugin's hook enforces on code). Source systems are named generically (a "mid-market SaaS", a "B2B fintech") unless the detail is a published vendor behavior.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: data-platform
product: <postgres | snowflake | bigquery | cube | metabase | superset | airbyte | fivetran | dbt | duckdb | generic | etc.>
product_version: <"2026.04" | "unknown" | "n/a">
scope: tenant-specific | version-specific | likely-general
tags: [3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context
## Attempts
## Resolution
```

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-elt-backfill-double-counted-rows.md`](2026-06-05-elt-backfill-double-counted-rows.md) | likely-general | elt, backfill, idempotency, merge, watermark, double-count | high |
| [`2026-06-05-scd-type-2-overwrite-lost-history.md`](2026-06-05-scd-type-2-overwrite-lost-history.md) | likely-general | scd, dimension, dbt, snapshot, history, type-2 | high |
| [`2026-06-05-embedded-rls-leak-via-cube-securitycontext.md`](2026-06-05-embedded-rls-leak-via-cube-securitycontext.md) | likely-general | multi-tenant, cube, securitycontext, rls, embed, denial-test | high |
| [`2026-06-05-warehouse-cost-blowout-dashboard-launch.md`](2026-06-05-warehouse-cost-blowout-dashboard-launch.md) | likely-general | warehouse, cost, snowflake, pre-aggregation, autosuspend, finops | medium |

## Promotion path

When ≥2 independent scenarios (different `contributed_at` quarters, different engagements) corroborate the same finding, an agent proposes promotion to a `knowledge/` decision tree or a `best-practices/` rule. As of this bank's first version, promotion is manual and scenarios stay in place after a rule is canonicalized — the narrative remains useful context. Several of these scenarios already corroborate an existing canonical rule (noted in each file's Resolution), so they read as field evidence *behind* the rule, not a substitute for it.
