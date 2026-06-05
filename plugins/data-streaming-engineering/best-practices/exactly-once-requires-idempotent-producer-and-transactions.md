# Exactly-once is idempotent producer plus transactions — not a config flag

**Status:** Absolute rule
**Domain:** Streaming delivery semantics
**Applies to:** `data-streaming-engineering`

---

## Why this exists

"Exactly-once" is the most misunderstood phrase in streaming. At-least-once delivery (the default
for a naive producer with retries) duplicates records on retry; at-most-once drops them on failure.
True exactly-once **processing** in Kafka is not a single setting — it requires the idempotent
producer (dedupes retries within a producer session), transactions (atomically commit produced
records *and* consumer offsets together), and consumers reading at `read_committed`. Teams that set
`acks=all` and call it exactly-once still emit duplicates downstream the first time a broker
failover happens, and the duplicate corrupts any non-idempotent sink (a double-charged payment, a
double-counted metric).

## How to apply

Compose the three pieces, and make the sink idempotent as the real backstop:

```properties
# Producer
enable.idempotence=true          # dedupe retries; implies acks=all, max.in.flight<=5
transactional.id=orders-tx-1     # stable per producer instance -> enables transactions

# Consumer (of a read-process-write pipeline)
isolation.level=read_committed   # never see records from aborted/uncommitted transactions
enable.auto.commit=false         # offsets are committed INSIDE the producer transaction
```

For a read-process-write loop: `beginTransaction()` → process → `sendOffsetsToTransaction()` →
`commitTransaction()`. The offset commit and the output records succeed or fail as one unit.

**Do:**

- Make the downstream **sink idempotent** (upsert by key, dedupe table) — it is the only guarantee that survives a sink outside the transaction (an external DB, an email).
- Use a **stable** `transactional.id` per logical producer so zombie fencing works.
- State the guarantee you actually provide per pipeline: at-least-once + idempotent sink is often the pragmatic, cheaper answer.

**Don't:**

- Claim exactly-once across a non-transactional boundary (HTTP call, second cluster) — it does not extend there.
- Leave `isolation.level` at the `read_uncommitted` default in a transactional pipeline.

## Edge cases / when the rule does NOT apply

- **Pure analytics / approximate counts** tolerant of rare duplicates: at-least-once is fine and far cheaper (transactions add latency and broker load).
- **Non-Kafka stacks** (Pulsar, Kinesis) have their own primitives — the *principle* (dedupe + atomic offset/commit + idempotent sink) carries, the API does not.
- **Sinks you don't control** can't be enrolled in the transaction; idempotent writes are then mandatory.

## See also

- [`../agents/streaming-architect.md`](../agents/streaming-architect.md) — owns the end-to-end delivery-semantics contract.
- [`./outbox-pattern-for-transactional-events.md`](./outbox-pattern-for-transactional-events.md) — how to publish atomically with a DB write at the source.

## Provenance

Codifies Kafka EOS mechanics (idempotent producer + transactions + `read_committed`) and the
`streaming-architect` / `kafka-pipeline-engineer` rule that the idempotent sink is the durable backstop.

---

_Last reviewed: 2026-06-05 by `claude`_
