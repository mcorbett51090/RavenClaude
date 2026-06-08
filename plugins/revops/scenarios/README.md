# RevOps scenarios bank

> Unverified, dated, scope-tagged narratives from real revenue-operations engagements. War stories of "we hit X
> problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real RevOps work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `docs/best-practices/`; scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: revops
product: <salesforce | hubspot | clari | generic | etc.>
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
| [`2026-06-08-two-definitions-of-mql.md`](2026-06-08-two-definitions-of-mql.md) | funnel, mql, definition, handoff, sla | `one-funnel-one-definition`, `routing-and-scoring-are-slas` |
| [`2026-06-08-forecast-on-padded-pipeline.md`](2026-06-08-forecast-on-padded-pipeline.md) | forecast, coverage, pipeline-hygiene, win-rate | `inspect-pipeline-before-the-math`, `coverage-is-derived-from-win-rate`, `forecast-is-a-methodology` |
| [`2026-06-08-last-touch-defunds-demand.md`](2026-06-08-last-touch-defunds-demand.md) | attribution, budget, demand-gen, multi-touch, last-touch | `attribution-is-a-lens-not-truth` |
| [`2026-06-08-quota-from-the-board-number.md`](2026-06-08-quota-from-the-board-number.md) | quota, capacity, comp, ramp, behavior | `quota-is-bottoms-up-from-capacity`, `comp-drives-behavior` |
| [`2026-06-08-crm-garbage-corrupts-routing.md`](2026-06-08-crm-garbage-corrupts-routing.md) | data-quality, routing, scoring, sla, dedupe | `data-quality-is-the-substrate`, `routing-and-scoring-are-slas` |
