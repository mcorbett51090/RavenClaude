---
name: schema-evolution-playbook
description: "Step-by-step playbook for evolving Avro/Protobuf/JSON Schema event schemas without breaking consumers, covering compatibility modes, migration patterns, and registry operations."
---

# Schema Evolution Playbook

## When to Use This

A producer needs to change an event schema — add a field, rename one, remove one, change a type. Use this playbook before any schema change lands in production to ensure zero consumer breakage.

## Compatibility Mode Selection

| Change type | Backward compatible | Forward compatible | Full compatible |
|---|---|---|---|
| Add optional field with default | Yes | No | No |
| Remove optional field | No | Yes | No |
| Add + remove optional fields | No | No | Yes (both modes) |
| Rename field | Never compatible — use aliases instead | | |
| Change field type | Almost never — add new field, deprecate old | | |

**Default recommendation:** set the registry to `BACKWARD` — consumers can upgrade independently after the producer ships.

## Step-by-Step Migration

1. **Identify all consumers** — query the schema registry's subject references or run `kafka-consumer-groups.sh --list` to enumerate active groups for the topic.
2. **Classify the change** — use the table above to pick the minimum compatibility mode needed.
3. **Register the candidate schema** — use the registry's `POST /compatibility` endpoint to check before any topic write:
   ```shell
   curl -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" \
     --data '{"schema": "<escaped-json>"}' \
     https://registry/compatibility/subjects/order-events-value/versions/latest
   ```
4. **Add default values for new fields** — Avro requires a default for backward-compatible additions; `null` is acceptable for optional fields but explicit application defaults carry intent.
5. **For breaking changes — dual-write transition:**
   - Introduce a new topic (`order-events-v2`) or a new subject strategy (e.g. `TopicRecordNameStrategy`).
   - Run both producers simultaneously until all consumers migrate.
   - Tombstone old topic (set retention to short window) only after all consumer-group offsets have passed the last old-schema message.
6. **Deprecate old fields in the schema** — use doc strings or a custom `"deprecated": true` property; do not delete for at least two release cycles.
7. **Update the schema registry soft-delete / hard-delete policy** — only hard-delete after all consumers confirm upgrade.

## Renaming Fields Without Breaking

Use Avro aliases:

```json
{
  "name": "userId",
  "type": "string",
  "aliases": ["user_id"],
  "doc": "Renamed from user_id in v3. Alias preserved for old consumers."
}
```

Protobuf: keep the field number; change the name only in the `.proto` source — wire format is number-keyed.

## Pitfalls

- Registering a schema without checking compatibility first — the registry will reject it at write time, not before, causing producer failures mid-stream.
- Removing a field that a consumer reads without a default — consumers throw deserialization errors on historical messages replayed from offset 0.
- Using `TopicNameStrategy` with multiple record types in one topic — evolving one breaks the other; prefer `TopicRecordNameStrategy` or separate topics.
- Skipping the compatibility check step because "it's just adding a field" — null defaults are easy to forget, and missing them causes backward-incompatibility silently.
- Deleting a schema version before all consumers have processed every message serialized under it — even with short retention, reprocessing from a snapshot can surface old versions.

## See Also

- [`../../agents/kafka-pipeline-engineer.md`](../../agents/kafka-pipeline-engineer.md) — schema registry + compatibility/evolution ownership
- [`../../agents/streaming-architect.md`](../../agents/streaming-architect.md) — delivery semantics and topology decisions
