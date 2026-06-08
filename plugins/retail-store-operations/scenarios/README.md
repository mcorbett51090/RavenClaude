# Retail Store Operations scenarios bank

> Unverified, dated, scope-tagged narratives from real retail store-operations engagements. War stories of "we hit X
> problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real store-operations / merchandising / inventory work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and the best-practices; scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: retail-store-operations
product: <pos | planogram | merchandising | inventory | generic | etc.>
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
| [`2026-06-08-markdown-taken-too-late.md`](2026-06-08-markdown-taken-too-late.md) | markdown, sell-through, weeks-of-supply, seasonal | `markdown-is-a-decision-not-a-default`, `sell-through-and-wos-are-the-vital-signs` |
| [`2026-06-08-stockout-next-to-overstock.md`](2026-06-08-stockout-next-to-overstock.md) | allocation, replenishment, weeks-of-supply, open-to-buy | `allocate-at-the-store-sku-level`, `open-to-buy-is-a-budget` |
