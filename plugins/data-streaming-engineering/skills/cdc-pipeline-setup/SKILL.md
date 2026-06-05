---
name: cdc-pipeline-setup
description: "Step-by-step playbook for standing up a Change Data Capture pipeline with Debezium — source connector configuration, slot management, snapshot strategy, and handling common failure modes."
---

# CDC Pipeline Setup (Debezium)

## When to Use This Skill

When a team needs to stream database changes (inserts, updates, deletes) into Kafka from PostgreSQL, MySQL, or SQL Server using Debezium. Covers initial connector setup through production hardening.

## Pre-flight Checklist

Before deploying the connector:

- [ ] Source DB has logical replication enabled (`wal_level = logical` for Postgres)
- [ ] Debezium DB user has `REPLICATION` role + `SELECT` on all captured tables
- [ ] A **dedicated replication slot** name is chosen (not shared with another tool)
- [ ] Kafka topic naming convention decided (default: `<server>.<schema>.<table>`)
- [ ] Schema registry is running and subjects are pre-created if using AVRO
- [ ] Snapshot strategy chosen (see table below)

## Connector Configuration — PostgreSQL

```json
{
  "name": "postgres-cdc-orders",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "db.internal",
    "database.port": "5432",
    "database.user": "debezium",
    "database.password": "${file:/secrets/debezium.properties:db.password}",
    "database.dbname": "orders",
    "database.server.name": "orders-db",
    "slot.name": "debezium_orders_slot",
    "plugin.name": "pgoutput",
    "table.include.list": "public.orders,public.order_items",
    "snapshot.mode": "initial",
    "key.converter": "io.confluent.kafka.serializers.KafkaAvroSerializer",
    "value.converter": "io.confluent.kafka.serializers.KafkaAvroSerializer",
    "schema.registry.url": "http://schema-registry:8081",
    "heartbeat.interval.ms": "30000",
    "slot.max.retries": "5",
    "slot.retry.delay.ms": "10000"
  }
}
```

## Snapshot Mode Decision

| Mode | When to choose |
|---|---|
| `initial` | First deployment — captures full table state before streaming changes |
| `never` | Topic already has historical data; only want new changes |
| `always` | Connector restart always re-snapshots (only for small tables) |
| `exported` (Postgres) | Large tables: uses a transaction export for consistent point-in-time |
| `initial_only` | One-shot migration: snapshot then stop (use with care — no streaming) |

**Default for new pipelines:** `initial` + monitor snapshot lag via `kafka_connect_snapshot_total_records_remaining`.

## Replication Slot Management

A Debezium replication slot holds WAL until the connector acknowledges it. An idle or stopped connector causes WAL accumulation — monitor slot lag daily:

```sql
SELECT slot_name, pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS lag
FROM pg_replication_slots
WHERE active = false;
```

**Action thresholds:**

| Lag | Action |
|---|---|
| < 1 GB | Normal |
| 1–5 GB | Alert on-call; investigate why connector is stopped |
| > 5 GB | Emergency: restart connector or drop slot to protect DB disk |

To safely drop a stuck slot: `SELECT pg_drop_replication_slot('debezium_orders_slot');` — the connector will re-snapshot on next start if mode is `initial`.

## Handling Schema Changes on the Source

1. Capture the DDL change timestamp from the Debezium `ddl` event (only in schema change topics).
2. Evolve the schema in the registry using the `schema-registry-evolution` skill before the DDL runs if possible.
3. For `ADD COLUMN`: Debezium propagates automatically — new field appears in events after the DDL.
4. For `DROP COLUMN` or type changes: treat as a breaking schema change — create a new Kafka subject.

## Pitfalls

- Sharing a replication slot with another tool (e.g., a read-replica streaming setup) — two consumers on one slot cause duplicate events and undefined ordering.
- Not setting `heartbeat.interval.ms` on a low-traffic table — the slot doesn't advance and WAL accumulates silently until disk fills.
- Running Debezium with `snapshot.mode=always` on a large table — every connector restart triggers a full table scan, flooding the topic and the DB.
- Storing DB credentials in the connector JSON checked into source control — always use `${file:...}` or a secrets provider.

## See also

- [../../agents/kafka-pipeline-engineer.md](../../agents/kafka-pipeline-engineer.md) — CDC pipelines and Debezium configuration
- [../../agents/streaming-architect.md](../../agents/streaming-architect.md) — CDC topology and delivery semantics decisions
- [../../CLAUDE.md](../../CLAUDE.md) — house opinions on schemas and delivery guarantees
