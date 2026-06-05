# Database Engineering scenarios bank

> Unverified, dated, scope-tagged narratives from real database engagements. War stories of "we hit X problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real database work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `best-practices/`; scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: database-engineering
product: <postgres | mysql | sql-server | pgbouncer | generic | etc.>
product_version: <"16" | "unknown">
scope: tenant-specific | version-specific | likely-general
tags: [3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Constraints context
## Attempts
## Resolution
```

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-slow-query-missing-composite-index.md`](2026-06-05-slow-query-missing-composite-index.md) | likely-general | explain, composite-index, seq-scan, selectivity, sargability | high |
| [`2026-06-05-online-add-not-null-column-lock-storm.md`](2026-06-05-online-add-not-null-column-lock-storm.md) | likely-general | migration, not-null, lock, expand-contract, backfill | high |
| [`2026-06-05-replication-lag-stale-reads-after-failover.md`](2026-06-05-replication-lag-stale-reads-after-failover.md) | likely-general | replication-lag, read-replica, failover, consistency, read-your-writes | medium |
| [`2026-06-05-connection-pool-exhaustion-pgbouncer.md`](2026-06-05-connection-pool-exhaustion-pgbouncer.md) | likely-general | connection-pool, pgbouncer, max-connections, pool-mode, saturation | high |

## Promotion path

When ≥2 independent scenarios (different `contributed_at` quarters, different engagements) corroborate the same finding, an agent proposes promotion to a `knowledge/` decision tree or `best-practices/`. As of this bank's first version, promotion is manual and the scenarios stay in place after a rule is canonicalized — the narrative remains useful context.
