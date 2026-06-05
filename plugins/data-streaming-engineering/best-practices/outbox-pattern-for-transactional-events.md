# Use the outbox pattern to guarantee event delivery from transactional writes

**Status:** Absolute rule
**Domain:** CDC / event reliability
**Applies to:** `data-streaming-engineering`

---

## Why this exists

Dual-writes — writing to a database and publishing to Kafka in the same application code path — are not atomic. A crash between the two writes produces either a committed database record with no Kafka event, or a Kafka event with no database record. Both are silent inconsistencies that corrupt downstream pipelines. The outbox pattern solves this by writing the event to an `outbox` table in the same database transaction, then relying on Debezium CDC to stream from the outbox to Kafka — one atomic write, reliable relay.

## How to apply

**Database side (Postgres):**

```sql
-- Create the outbox table in the same database
CREATE TABLE outbox_events (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    aggregate_type  text NOT NULL,          -- 'Order', 'Payment'
    aggregate_id    text NOT NULL,          -- the entity's ID
    event_type      text NOT NULL,          -- 'order.placed'
    payload         jsonb NOT NULL,
    created_at      timestamptz DEFAULT now(),
    processed       boolean DEFAULT false
);

-- Application code: single transaction
BEGIN;
  INSERT INTO orders (id, amount, status) VALUES ($1, $2, 'pending');
  INSERT INTO outbox_events (aggregate_type, aggregate_id, event_type, payload)
  VALUES ('Order', $1, 'order.placed', '{"amount": $2}');
COMMIT;
```

**Debezium connector config:**

```json
{
  "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
  "table.include.list": "public.outbox_events",
  "transforms": "outbox",
  "transforms.outbox.type": "io.debezium.transforms.outbox.EventRouter",
  "transforms.outbox.table.field.event.key": "aggregate_id",
  "transforms.outbox.table.field.event.type": "event_type",
  "transforms.outbox.route.by.field": "aggregate_type"
}
```

The EventRouter transform routes each outbox row to a topic named after `aggregate_type`.

**Do:**
- Write the outbox insert in the same transaction as the domain write — atomicity is the whole point.
- Let Debezium (or a polling relay) handle the outbox-to-Kafka relay, not application code.
- Periodically clean up processed outbox rows (soft-delete or a background job) to avoid unbounded growth.

**Don't:**
- Use dual-writes (application calls DB + Kafka in sequence) — they are not atomic.
- Publish from an `AFTER COMMIT` hook in application code without the outbox table — this is still a dual-write with a smaller race window, not an elimination of it.

## Edge cases / when the rule does NOT apply

- Event stores (where the event log is the system of record, not a relational DB) don't need an outbox — the event IS the write.
- Read-only pipelines (CDC from a source the application doesn't write to) don't need an outbox — Debezium reads the WAL directly.

## See also

- [`../agents/kafka-pipeline-engineer.md`](../agents/kafka-pipeline-engineer.md) — configures Debezium + outbox connectors
- [`./cdc-over-dual-writes.md`](./cdc-over-dual-writes.md) — the parent rule that prohibits dual-writes

## Provenance

The outbox pattern is the canonical solution to the dual-write problem, described in the Debezium documentation and in Gunnar Morling's "Reliable Microservices Data Exchange with the Outbox Pattern" (2019). Codifies data-streaming-engineering CLAUDE.md §2 house opinion #5 ("Schemas evolve; govern them") and the CDC rule.

---

_Last reviewed: 2026-06-05 by `claude`_
