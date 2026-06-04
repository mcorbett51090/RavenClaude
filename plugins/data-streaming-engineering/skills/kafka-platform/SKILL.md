---
name: kafka-platform
description: "Run the streaming platform reliably: partition for the ordering you need (order is per-partition; the key is the guarantee), govern schemas with a registry + compatibility rules, configure producer durability (acks/idempotence) and consumer offsets/idempotency, and ingest via CDC not dual-writes."
---

# Kafka / Streaming Platform

## Partitioning
Order is **per-partition only** — the partition **key** is your ordering guarantee. Key by the entity needing order; balance count for throughput.

## Schemas
Registry + **compatibility rules** (backward/forward); evolve additively. Unversioned payload = cross-team outage.

## Producers/consumers
`acks=all` + idempotent producer; consumers commit offsets after processing (at-least-once) and are **idempotent** (redelivery happens).

## CDC, not dual-writes
Debezium + transactional **outbox** so events match committed state. Never write to DB and Kafka separately.
