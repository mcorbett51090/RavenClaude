# Wealth Management (RIA) scenarios bank

> Unverified, dated, scope-tagged narratives from real RIA-practice engagements. War stories of "we hit X
> problem, here was the situation, these were our constraints, we tried A/B/C, D worked."
>
> **Not investment advice.** Scenarios are educational field notes, not personalized recommendations.

This directory holds **scenarios** — field notes from real advisory work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `best-practices/`; scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: wealth-management-ria
product: <generic | planning | portfolio | compliance | etc.>
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
| [`2026-06-08-fixed-4pct-broke-on-sequence-risk.md`](2026-06-08-fixed-4pct-broke-on-sequence-risk.md) | withdrawal, sequence-risk, guardrails | `surface-every-assumption`, `not-personalized-investment-advice` |
| [`2026-06-08-rebalancing-with-no-written-rule.md`](2026-06-08-rebalancing-with-no-written-rule.md) | ips, rebalancing, taxes, discipline | `the-ips-is-the-governing-document`, `rebalancing-is-a-written-rule` |
| [`2026-06-08-tax-loss-harvest-tripped-the-wash-sale.md`](2026-06-08-tax-loss-harvest-tripped-the-wash-sale.md) | tax-loss-harvesting, wash-sale, asset-location | `after-tax-return-is-the-return` |
| [`2026-06-08-stale-kyc-broke-the-suitability-basis.md`](2026-06-08-stale-kyc-broke-the-suitability-basis.md) | suitability, kyc, books-and-records, periodic-review | `document-the-suitability-basis` |
| [`2026-06-08-no-conflicts-was-a-disclosure-failure.md`](2026-06-08-no-conflicts-was-a-disclosure-failure.md) | fiduciary, reg-bi, conflicts, form-adv | `disclose-and-manage-conflicts`, `fiduciary-is-not-reg-bi` |
