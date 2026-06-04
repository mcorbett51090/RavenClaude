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
