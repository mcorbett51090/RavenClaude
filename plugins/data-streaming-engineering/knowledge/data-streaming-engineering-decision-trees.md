# Data Streaming — Decision Trees

_Decision trees + a dated capability map. Capability rows are `[verify-at-build]` — re-check against the vendor before quoting. Last reviewed: 2026-06-04._

Traverse before building a stream or choosing delivery semantics.

## Decision Tree: Streaming or batch?

Justify streaming with a real latency need; otherwise batch is simpler and cheaper.

```mermaid
graph TD
  A[A data need] --> B{Sub-minute reaction required?}
  B -- No, hourly/daily is fine --> C[Batch ELT -> data-platform]
  B -- Yes --> D{Continuous unbounded events?}
  D -- No, periodic snapshots --> C
  D -- Yes --> E[Streaming justified]
  E --> F{Source is a database?}
  F -- Yes --> G[CDC: Debezium + outbox - NOT dual-writes]
  F -- No, app/IoT events --> H[Produce to topics, keyed for ordering]
```

_Streaming is operationally heavy — don't pay for it without a latency need._

## Decision Tree: Delivery semantics

Pick the weakest semantic that meets the requirement; stronger costs throughput + complexity.

```mermaid
graph TD
  A[A pipeline hop] --> B{Can the consumer be made idempotent?}
  B -- Yes --> C[At-least-once + idempotent consumer - pragmatic default]
  B -- No --> D{Does the sink support transactions?}
  D -- Yes --> E[Exactly-once end-to-end - accept the throughput cost]
  D -- No --> F[At-least-once + dedup at the sink / accept duplicates]
  C --> G[Commit offsets AFTER processing]
  E --> G
```


## Decision Tree: Which window type?

The window type is the analytical question; pick it from the question, not by habit.

```mermaid
graph TD
  A[A windowed aggregation] --> B{Is the boundary driven by user activity gaps?}
  B -- Yes, sessionize by inactivity --> C[Session window: gap timeout closes it]
  B -- No --> D{Do consecutive results need to overlap / slide?}
  D -- Yes, rolling/moving metric --> E[Sliding window: size + slide interval]
  D -- No, fixed non-overlapping buckets --> F{Need a result per fixed period e.g. per minute?}
  F -- Yes --> G[Tumbling window: each event in exactly one window]
  F -- No, per-key count/volume threshold --> H[Count/global window with trigger]
  C --> I[All on event-time + watermark + a late-data policy]
  E --> I
  G --> I
```

_Sliding windows multiply state (each event in many windows) — bound it. Every window runs on event-time with a watermark and an explicit late-data policy._

## Decision Tree: Which schema-compatibility mode?

Compatibility mode is a contract about who can deploy first; choose by upgrade order.

```mermaid
graph TD
  A[Evolving an event schema] --> B{Who upgrades first?}
  B -- Consumers before producers --> C[BACKWARD: new schema reads old data - safe to add optional fields]
  B -- Producers before consumers --> D[FORWARD: old schema reads new data - safe to add then drop later]
  B -- Either order / mixed fleet --> E[FULL: both directions - most constrained, additive-only]
  A --> F{Breaking change unavoidable e.g. rename, type change?}
  F -- Yes --> G[New topic/version + dual-write window + migrate consumers, NOT in place]
  C --> H[Register + enforce in the registry; CI-check before deploy]
  D --> H
  E --> H
```

_An unversioned payload is a future cross-team outage. A genuinely breaking change is a new topic + migration, never a silent in-place edit._

## Decision Tree: How do I reprocess / recover?

Match the recovery mechanism to what you're fixing; idempotent consumers make all of these safe.

```mermaid
graph TD
  A[Need to reprocess data] --> B{Rebuilding current state e.g. a new cache/materialized view?}
  B -- Yes --> C{Source topic is log-compacted changelog?}
  C -- Yes --> D[Replay from compacted topic - latest value per key]
  C -- No --> E[Replay from earliest within retention OR rebuild from system of record]
  B -- No --> F{Fixing a processing bug retroactively?}
  F -- Yes --> G{History still within retention?}
  G -- Yes --> H[Reset offsets to the window, reprocess with idempotent consumer]
  G -- No --> I[Backfill from the source of record / warehouse]
  F -- No, onboarding a new consumer --> J[Read from earliest; ensure idempotent so it doesn't double-apply]
```

_Replay is a design constraint: it needs retention to cover the window, idempotent consumers, and an offset-reset plan that won't corrupt live state._

## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| Apache Kafka | GA, ecosystem default | KRaft (no ZooKeeper) standard |
| Schema Registry (Avro/Protobuf/JSON) | GA | Compatibility rules essential |
| Debezium CDC | GA | Log-based change capture |
| Apache Flink | GA | Event-time, watermarks, exactly-once |
| Kafka Streams | GA | JVM library; stateful processing |
| Kafka transactions / EOS | GA | Exactly-once within Kafka; sink matters |
| Pulsar / Kinesis | GA | Multi-tenant / AWS-managed alternatives |
