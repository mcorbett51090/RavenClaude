# Data Streaming Engineering scenarios bank

> Unverified, dated, scope-tagged narratives from real streaming engagements. War stories of "we hit X problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real Kafka / Flink / CDC work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) (the decision-tree bank) and [`../best-practices/`](../best-practices/); scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: data-streaming-engineering
product: <kafka | flink | kafka-streams | debezium | kinesis | pulsar | confluent | generic | etc.>
product_version: <"3.7" | "unknown">
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
| [`2026-06-05-consumer-lag-rebalance-storm.md`](2026-06-05-consumer-lag-rebalance-storm.md) | likely-general | consumer-lag, rebalance, max-poll, cooperative-sticky, partition-assignment | high |
| [`2026-06-05-exactly-once-redesign.md`](2026-06-05-exactly-once-redesign.md) | likely-general | exactly-once, at-least-once, idempotent-consumer, transactions, end-to-end | high |
| [`2026-06-05-schema-evolution-break.md`](2026-06-05-schema-evolution-break.md) | likely-general | schema-registry, compatibility, avro, breaking-change, new-topic | high |
| [`2026-06-05-out-of-order-watermark-late-data.md`](2026-06-05-out-of-order-watermark-late-data.md) | likely-general | event-time, watermark, late-data, windowing, allowed-lateness | high |
| [`2026-06-05-partition-skew-hot-key.md`](2026-06-05-partition-skew-hot-key.md) | likely-general | partition-skew, hot-key, keying, parallelism, ordering | medium |

## Promotion path

When ≥2 independent scenarios (different `contributed_at` quarters, different engagements) corroborate the same finding, an agent proposes promotion to a `knowledge/` decision tree or `docs/best-practices/`. As of this bank's first version, promotion is manual and the scenarios stay in place after a rule is canonicalized — the narrative remains useful context.
