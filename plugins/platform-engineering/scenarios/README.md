# Platform Engineering scenarios bank

> Unverified, dated, scope-tagged narratives from real platform-engineering engagements. War stories of "we hit X
> problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real platform work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `docs/best-practices/`; scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: platform-engineering
product: <backstage | port | crossplane | terraform | score | generic | etc.>
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
| [`2026-06-08-backstage-catalog-drift.md`](2026-06-08-backstage-catalog-drift.md) | catalog, ownership, auto-discovery, drift | `the-catalog-is-source-of-truth-or-nothing`, `ownership-is-a-hard-requirement` |
| [`2026-06-08-self-service-that-was-a-ticket-queue.md`](2026-06-08-self-service-that-was-a-ticket-queue.md) | self-service, golden-path, guardrails-as-defaults, adoption | `self-service-means-no-human-in-the-loop`, `guardrails-as-defaults-not-gates` |
