# Manufacturing Operations scenarios bank

> Unverified, dated, scope-tagged narratives from real manufacturing-operations engagements. War stories of "we hit X
> problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real shop-floor work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `best-practices/`; scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: manufacturing-operations
product: <oee | mrp | spc | capa | toc | generic | etc.>
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
| [`2026-06-08-oee-that-was-inflated.md`](2026-06-08-oee-that-was-inflated.md) | oee, denominators, six-big-losses, bottleneck, toc | `oee-denominators-must-be-defined`, `the-bottleneck-sets-the-rate` |
| [`2026-06-08-capa-that-was-just-scrap.md`](2026-06-08-capa-that-was-just-scrap.md) | capa, ncr, root-cause, preventive-action, spc | `containment-is-not-a-capa`, `prevention-beats-detection-beats-scrap` |
