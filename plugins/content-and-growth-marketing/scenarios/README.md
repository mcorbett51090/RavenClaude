# Content & Growth Marketing scenarios bank

> Unverified, dated, scope-tagged narratives from real content-and-growth engagements. War stories of "we hit X
> problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real content, SEO, and lifecycle work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `docs/best-practices/`; scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: content-and-growth-marketing
product: <ghost | wordpress | ahrefs | klaviyo | hubspot | generic | etc.>
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
| [`2026-06-08-blog-that-never-compounded.md`](2026-06-08-blog-that-never-compounded.md) | content-strategy, topic-clusters, seo, distribution | `strategy-compounds-tactics-decay`, `search-intent-is-the-unit-not-the-keyword` |
| [`2026-06-08-emails-in-the-spam-folder.md`](2026-06-08-emails-in-the-spam-folder.md) | deliverability, segmentation, lifecycle, vanity-metrics | `deliverability-is-the-foundation`, `segment-and-trigger-dont-blast` |
