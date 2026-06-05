# Backend Engineering scenarios bank

> Unverified, dated, scope-tagged narratives from real backend engagements. War stories of "we hit X problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real backend work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `docs/best-practices/`; scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: backend-engineering
product: <postgres | redis | rabbitmq | node | python | go | generic | etc.>
product_version: <"2026.04" | "unknown">
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
| [`2026-06-05-idempotent-payments-endpoint.md`](2026-06-05-idempotent-payments-endpoint.md) | likely-general | idempotency, payments, retries, dedup-key, race | high |
| [`2026-06-05-n-plus-one-and-pool-exhaustion.md`](2026-06-05-n-plus-one-and-pool-exhaustion.md) | likely-general | n-plus-1, orm, connection-pool, latency, eager-load | high |
| [`2026-06-05-zero-downtime-schema-migration.md`](2026-06-05-zero-downtime-schema-migration.md) | likely-general | migration, zero-downtime, expand-contract, backfill, not-null | high |
| [`2026-06-05-async-job-queue-poison-message.md`](2026-06-05-async-job-queue-poison-message.md) | likely-general | queue, dlq, idempotent-consumer, poison-message, backpressure | medium |

## Promotion path

When ≥2 independent scenarios (different `contributed_at` quarters, different engagements) corroborate the same finding, an agent proposes promotion to a `knowledge/` decision tree or `docs/best-practices/`. As of this bank's first version, promotion is manual and the scenarios stay in place after a rule is canonicalized — the narrative remains useful context.
