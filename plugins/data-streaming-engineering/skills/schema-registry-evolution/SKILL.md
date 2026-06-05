---
name: schema-registry-evolution
description: "Playbook for managing Avro/Protobuf/JSON Schema schemas in a registry — choosing a compatibility mode, executing safe schema changes, and handling breaking changes without consumer downtime."
---

# Schema Registry Evolution

## When to Use This Skill

Any time a schema change is proposed on a Kafka topic, or when a team is choosing a compatibility mode for a new subject in Confluent Schema Registry or AWS Glue Schema Registry.

## Compatibility Mode Selection

| Mode | What it allows | Use when |
|---|---|---|
| `BACKWARD` | New schema reads data written with old schema | Consumers upgrade first; producer adds optional fields |
| `FORWARD` | Old schema reads data written with new schema | Producers upgrade first; adds fields consumers ignore |
| `FULL` | Both backward + forward | You need rolling deploys with mixed versions in flight |
| `NONE` | No compatibility check | Internal dev topics only — never production |

**Default recommendation:** `FULL` for any topic consumed by multiple independent teams. `BACKWARD` for tightly-coupled producer/consumer pairs where you always update consumers first.

## Safe Change Checklist

**Adding a field (safe):**

1. Add with a default value in the schema (`"default": null` for Avro unions; `optional` in Protobuf).
2. Register the new schema version in the registry; confirm compatibility check passes.
3. Deploy the producer that starts writing the new field.
4. Deploy consumers that read the new field.
5. After all consumers are deployed, remove the default if the field is now required.

**Removing a field (requires care):**

1. First mark it as deprecated in documentation; don't remove yet.
2. Deploy all consumers to stop reading the field.
3. Once no consumer reads it, register the schema without the field (only safe under `BACKWARD` or `FULL`).
4. Never remove a field in the same release that adds another field — one change per version.

**Renaming a field (breaking under all modes):**

- Avro/JSON Schema have no rename primitive. Treat as add + deprecate: add the new name (with default), migrate consumers, then remove the old name across two separate schema versions.

## Breaking Change Protocol

When a breaking change is unavoidable (type change, semantic reinterpretation):

1. Create a **new subject** (new topic name or `<topic>-v2` convention).
2. Run the old and new topics in parallel; dual-publish from the producer if needed.
3. Migrate consumers to the new topic.
4. Retire the old topic after a migration window.

Never mutate the meaning of an existing field name — consumers can't distinguish a type change from a bug.

## Registry Operations Quick Reference

```bash
# Check compatibility before registering
curl -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  --data '{"schema": "<escaped-schema>"}' \
  http://registry:8081/compatibility/subjects/<topic>-value/versions/latest

# List versions for a subject
curl http://registry:8081/subjects/<topic>-value/versions

# Fetch a specific version
curl http://registry:8081/subjects/<topic>-value/versions/3
```

## Pitfalls

- Registering a schema without checking compatibility first — the producer deploys, breaks consumers, and you discover it in prod.
- Using `NONE` mode on a shared topic because "it's easier" — any producer deploy can silently corrupt consumer deserialization.
- Storing the schema ID in a sidecar database instead of trusting the registry wire format — the magic byte + schema ID header in every Kafka message is the contract; don't duplicate it.
- Forgetting that `null` is a type in Avro — a nullable field must be a union `["null", "string"]`, not just `"string"` with a null default.

## See also

- [../../agents/kafka-pipeline-engineer.md](../../agents/kafka-pipeline-engineer.md) — owns schema registry and producer/consumer compatibility
- [../../agents/streaming-architect.md](../../agents/streaming-architect.md) — picks delivery semantics and CDC approach
- [../../CLAUDE.md](../../CLAUDE.md) — house opinions on schema evolution
