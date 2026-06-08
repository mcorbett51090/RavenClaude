# Public-sector-grants scenarios bank

> Unverified, dated, scope-tagged narratives from real grants engagements. War stories of "we hit X problem, here was
> the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real grant work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `docs/best-practices/`; scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: public-sector-grants
product: <federal-noFO | 2-cfr-200 | single-audit | grants-gov | generic | etc.>
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
| [`2026-06-08-chased-an-off-mission-grant.md`](2026-06-08-chased-an-off-mission-grant.md) | go-no-go, fit, sustainability, mission-drift | `fund-the-mission-not-the-money`, `go-no-go-is-a-real-decision` |
| [`2026-06-08-subrecipient-mistaken-for-a-vendor.md`](2026-06-08-subrecipient-mistaken-for-a-vendor.md) | sub-recipient, monitoring, single-audit, uniform-guidance | `allowable-allocable-reasonable-all-three`, `cite-the-authority-not-a-memory` |
