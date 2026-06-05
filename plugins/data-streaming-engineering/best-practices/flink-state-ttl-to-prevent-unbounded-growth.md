# Configure state TTL on all keyed Flink state to prevent unbounded heap growth

**Status:** Absolute rule
**Domain:** Flink / state management
**Applies to:** `data-streaming-engineering`

---

## Why this exists

Keyed state in a Flink operator (ValueState, MapState, ListState) grows indefinitely if no TTL is set — one entry per key, forever. A customer-session aggregation job that sees 10 million unique customers over a year will hold 10 million state entries, most of which are for sessions that ended months ago. Without TTL, the RocksDB state backend fills disk and heap pressure causes checkpointing latency or OOM evictions. State TTL is the garbage collection mechanism for keyed state; omitting it is a memory management defect.

## How to apply

```java
// Configure TTL at state descriptor creation time
StateTtlConfig ttlConfig = StateTtlConfig
    .newBuilder(Time.hours(24))             // evict state after 24 hours of no updates
    .setUpdateType(StateTtlConfig.UpdateType.OnCreateAndWrite)
    .setStateVisibility(StateTtlConfig.StateVisibility.NeverReturnExpired)
    .cleanupFullSnapshot()                  // also clean on checkpoint
    .build();

ValueStateDescriptor<UserSession> descriptor =
    new ValueStateDescriptor<>("user-session", UserSession.class);
descriptor.enableTimeToLive(ttlConfig);

ValueState<UserSession> state = getRuntimeContext().getState(descriptor);
```

**TTL by state type:**

| State type | Typical TTL | Rationale |
|---|---|---|
| Session aggregation | 30 min - 2 hours | Session inactivity timeout + buffer |
| Per-user daily aggregate | 25-26 hours | Cover a calendar day with a 1-2 hour buffer |
| Deduplication window | 2x the expected message delivery window | Covers redelivery |
| KTable join state | Retention of the joined stream | Must cover the join window |

**Do:**
- Set TTL on every `ValueState`, `MapState`, and `ListState` in every keyed operator.
- Choose `UpdateType.OnCreateAndWrite` — the TTL clock resets on every update, expiring only truly inactive keys.
- Monitor RocksDB state size via Flink metrics (`taskmanager_job_task_operator_rocksdb_state_size`).

**Don't:**
- Omit TTL assuming "the keyspace is small" — keyspaces grow, and migrating without TTL requires a stateful restart.
- Set TTL to `Long.MAX_VALUE` (effectively infinite) — treat it the same as omitting TTL.
- Use `StateVisibility.ReturnExpiredIfNotCleanedUp` in production — expired state should not be visible.

## Edge cases / when the rule does NOT apply

- Append-only accumulators over a bounded time window (e.g., a global count since launch) are intentionally unbounded and should use a different pattern (a partitioned aggregate mart, not Flink keyed state).
- Flink SQL's `MATCH_RECOGNIZE` and CEP operators manage their own state windows internally — no explicit TTL needed if the pattern has a bounded `WITHIN` clause.

## See also

- [`../agents/stream-processing-engineer.md`](../agents/stream-processing-engineer.md) — owns stateful operator design
- [`./checkpoint-stateful-operators-for-recovery.md`](./checkpoint-stateful-operators-for-recovery.md) — the checkpointing rule that TTL configuration interacts with

## Provenance

Apache Flink documentation on State TTL (available since Flink 1.6). Standard production Flink operational practice. Codifies data-streaming-engineering CLAUDE.md §2 house opinion #6 ("State and backpressure are first-class. Design both, don't discover them").

---

_Last reviewed: 2026-06-05 by `claude`_
