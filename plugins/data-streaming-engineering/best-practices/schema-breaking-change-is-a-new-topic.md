# A breaking schema change is a new topic — never an in-place edit

**Status:** Absolute rule
**Domain:** Schema registry / event schema evolution
**Applies to:** `data-streaming-engineering`

---

## Why this exists

A breaking schema change — renaming a field, changing a field's type, removing a required field — deployed in-place on an existing topic will break every consumer that has already deserialized older messages. The schema registry's compatibility rules (BACKWARD, FORWARD, FULL) only govern additive changes within a topic. A genuinely breaking change that is forced through by disabling compatibility checking leaves consumers in an undefined state: some process old messages, some process new messages, and no consumer can safely process both. The correct migration path is a new topic, a dual-produce window, and a planned consumer migration.

## How to apply

**Breaking vs non-breaking change checklist:**

| Change | Breaking? | Safe path |
|---|---|---|
| Add optional field with default | No | Register new schema, existing consumers ignore |
| Remove optional field | No (FORWARD) | Remove from producer, old consumers read null |
| Rename a field | Yes | New topic |
| Change field type (int → string) | Yes | New topic |
| Remove required field | Yes | New topic |
| Add required field without default | Yes | New topic |

**New-topic migration procedure:**

```
1. Create: commerce.prod.order.placed.v2 (new schema)
2. Dual-produce: producer writes to BOTH v1 and v2 for a migration window (e.g., 2 weeks)
3. Migrate consumers: one consumer group at a time, verify, then cut over to v2
4. Stop v1 production: once all consumers are on v2, stop writing to v1
5. Retain v1: keep v1 topic readable until its retention window expires
   (don't delete — some replaying consumer may still need it)
```

**Do:**
- Register the new schema under the new topic before any dual-produce begins.
- Use the migration window to validate consumers on the new schema before cutting over.
- Keep the old topic readable through its full retention period.

**Don't:**
- Disable schema registry compatibility checking to force through a breaking change in-place.
- Delete the old topic the day consumers are migrated — wait for the retention window.
- Assume all consumers are in sync and cut over without verifying consumer group offsets on the new topic.

## Edge cases / when the rule does NOT apply

- Adding an optional field with a default value in an Avro schema is backward-compatible and does NOT require a new topic — this is the safe non-breaking path and should be the first option explored before creating a new topic.

## See also

- [`../agents/kafka-pipeline-engineer.md`](../agents/kafka-pipeline-engineer.md) — manages schema registry and compatibility rules
- [`./govern-schemas-with-a-registry.md`](./govern-schemas-with-a-registry.md) — the schema governance rule this exception-handles

## Provenance

Apache Kafka / Confluent Schema Registry documentation on compatibility modes and schema evolution best practices. Codifies data-streaming-engineering CLAUDE.md §2 house opinion #5 ("A schema registry with compatibility rules keeps a producer change from breaking every consumer").

---

_Last reviewed: 2026-06-05 by `claude`_
