# ESG & Sustainability Reporting scenarios bank

> Unverified, dated, scope-tagged narratives from real ESG-reporting engagements. War stories of "we hit X
> problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real ESG / sustainability-disclosure work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `docs/best-practices/`; scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: esg-sustainability-reporting
product: <csrd-esrs | issb | ghg-protocol | gri | sec | generic | etc.>
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
| [`2026-06-08-scope-2-single-method.md`](2026-06-08-scope-2-single-method.md) | scope-2, market-based, location-based, dual-reporting, emission-factors | `dual-report-scope-2-never-silently-one`, `cite-framework-clause-factor-and-boundary` |
| [`2026-06-08-materiality-survey-not-a-determination.md`](2026-06-08-materiality-survey-not-a-determination.md) | materiality, double-materiality, csrd, governance, assurance | `materiality-is-a-determination-not-a-vibe`, `scope-before-you-calculate` |
