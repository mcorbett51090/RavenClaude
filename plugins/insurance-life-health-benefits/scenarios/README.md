# Life / Health / Employee-Benefits scenarios bank

> Unverified, dated, scope-tagged narratives from real benefits engagements. War stories of "we hit X problem, here
> was the situation, these were our constraints, we tried A/B/C, D worked." **Educational scaffolding, not legal, tax,
> or actuarial advice.**

This directory holds **scenarios** — field notes from real benefits work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `best-practices/`; scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: insurance-life-health-benefits
product: <fully-insured | self-funded | level-funded | generic | etc.>
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
| [`2026-06-08-self-funded-to-dodge-a-renewal.md`](2026-06-08-self-funded-to-dodge-a-renewal.md) | funding, self-funded, stop-loss, renewal | `funding-is-a-risk-decision`, `decompose-every-renewal` |
| [`2026-06-08-hdhp-cost-shift-revolt.md`](2026-06-08-hdhp-cost-shift-revolt.md) | plan-design, hdhp, hsa, total-cost | `total-cost-of-coverage-not-premium`, `benefits-are-a-system-not-a-pile` |
