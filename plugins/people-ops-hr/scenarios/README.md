# People Ops / HR scenarios bank

> Unverified, dated, scope-tagged narratives from real people-ops engagements. War stories of "we hit X
> problem, here was the situation, these were our constraints, we tried A/B/C, D worked." **None is legal advice.**

This directory holds **scenarios** — field notes from real people-ops/HR work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble, and never as a legal determination

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `best-practices/`; scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: people-ops-hr
product: <bamboohr | greenhouse | generic | etc.>
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
| [`2026-06-08-self-service-onboarding-that-skipped-offboarding.md`](2026-06-08-self-service-onboarding-that-skipped-offboarding.md) | lifecycle, offboarding, hris, access | `offboarding-is-half-the-lifecycle`, `hris-is-the-source-of-truth-or-nothing` |
| [`2026-06-08-comp-bands-with-no-leveling.md`](2026-06-08-comp-bands-with-no-leveling.md) | compensation, leveling, pay-equity | `level-before-band`, `pay-equity-controls-for-legitimate-factors` |
