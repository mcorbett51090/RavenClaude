# Tableau scenarios bank

> Unverified, dated, scope-tagged narratives from real Tableau engagements. War stories of "we hit X, here was the situation, these were our permissions, we tried A/B/C, D worked."

This directory holds **scenarios** that the Tableau agents consult as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed** (`reviewed: false` until a maintainer promotes the lesson).
- **Visible to consumers** via `/plugin install` (privacy-protected by the `/wrap` scrub step that strips client-identifying info).
- **Consulted by agents** as a *secondary* source, never overriding the citation-grounded `knowledge/` decision trees.

For the full architecture, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). To contribute one, use the `/wrap` slash command ([`../../ravenclaude-core/commands/wrap.md`](../../ravenclaude-core/commands/wrap.md)).

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: tableau
product: <tableau-desktop | tableau-cloud | tableau-server | tableau-prep | embedding-api | tableau-pulse | etc.>
product_version: <"2025.3" | "unknown">
scope: tenant-specific | version-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Permissions context
## Attempts
## Resolution
```

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-fixed-lod-ignores-dimension-filter.md`](2026-06-05-fixed-lod-ignores-dimension-filter.md) | likely-general | lod, fixed, order-of-operations, context-filter, wrong-totals | high |
| [`2026-06-05-embedding-jwt-scope-and-rls-mismatch.md`](2026-06-05-embedding-jwt-scope-and-rls-mismatch.md) | version-specific | embedding-api, connected-apps, jwt, rls, 401, scopes | high |
| [`2026-06-05-server-to-cloud-extract-refresh-deadend.md`](2026-06-05-server-to-cloud-extract-refresh-deadend.md) | version-specific | server-to-cloud, content-migration-tool, extracts, tableau-bridge, refresh-schedule | medium |
| [`2026-06-05-slow-dashboard-quick-filter-domain-queries.md`](2026-06-05-slow-dashboard-quick-filter-domain-queries.md) | likely-general | performance, performance-recorder, quick-filters, query-fusion, marks | high |

## Promotion path

When ≥2 independent scenarios (different `contributed_at` quarters, different engagements) corroborate the same finding, a maintainer drafts a `best-practices/` doc by hand from the scenario contents and promotes it via the existing review flow. The scenarios stay in place — the narrative remains useful context even after the rule is canonicalized.
