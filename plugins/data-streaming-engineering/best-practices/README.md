# Data Streaming Engineering — best-practice docs

Named, citable rules for the `data-streaming-engineering` plugin's specialists. Each file is **one rule**, grounded in this plugin's house opinions and the Kafka/Flink/CDC craft. Read, applied, and cited as a whole.

---

## Index

_23 rules. Each file is one named, citable rule; read and apply it whole._

| Doc | Status | Use when |
|---|---|---|
| [`bound-state-and-handle-backpressure.md`](./bound-state-and-handle-backpressure.md) | Absolute rule | A Flink job is running out of memory or the consumer is falling behind the producer. |
| [`handle-late-data-explicitly.md`](./handle-late-data-explicitly.md) | Absolute rule | A windowed aggregation is dropping events that arrived after the window closed. |
| [`design-a-replay-strategy.md`](./design-a-replay-strategy.md) | Absolute rule | A pipeline needs to reprocess historical data or recover from a processing bug. |
| [`partition-for-ordering-and-parallelism.md`](./partition-for-ordering-and-parallelism.md) | Absolute rule | Choosing a Kafka partition key — ordering guarantee vs. parallelism trade-off. |
| [`choose-delivery-semantics-deliberately.md`](./choose-delivery-semantics-deliberately.md) | Absolute rule | Choosing at-least-once, exactly-once, or at-most-once for a pipeline hop. |
| [`exactly-once-requires-idempotent-producer-and-transactions.md`](./exactly-once-requires-idempotent-producer-and-transactions.md) | Absolute rule | Implementing exactly-once — idempotent producer + transactions + read_committed + an idempotent sink. |
| [`checkpoint-stateful-operators-for-recovery.md`](./checkpoint-stateful-operators-for-recovery.md) | Absolute rule | A Flink job failed and there is no checkpoint to recover from. |
| [`event-time-not-processing-time.md`](./event-time-not-processing-time.md) | Absolute rule | A windowed aggregation is using processing time and producing wrong results on late/out-of-order events. |
| [`idempotent-consumers-and-a-dlq.md`](./idempotent-consumers-and-a-dlq.md) | Absolute rule | A consumer is processing a message more than once or a poison-pill message is blocking the pipeline. |
| [`stream-only-when-latency-demands.md`](./stream-only-when-latency-demands.md) | Absolute rule | Evaluating whether a use case needs real-time streaming or batch ELT is sufficient. |
| [`govern-schemas-with-a-registry.md`](./govern-schemas-with-a-registry.md) | Absolute rule | A producer schema change broke a consumer — establish a schema registry with compatibility rules. |
| [`exactly-once-is-end-to-end-or-nothing.md`](./exactly-once-is-end-to-end-or-nothing.md) | Absolute rule | Claiming exactly-once semantics without confirming the sink supports transactions. |
| [`cdc-over-dual-writes.md`](./cdc-over-dual-writes.md) | Absolute rule | Choosing between CDC (Debezium) and dual-writes for capturing database changes. |
| [`topic-naming-convention.md`](./topic-naming-convention.md) | Absolute rule | Creating a new Kafka topic without a consistent, machine-parseable naming convention. |
| [`size-partitions-for-throughput-targets.md`](./size-partitions-for-throughput-targets.md) | Pattern | Setting topic partition count — use measured throughput, not a guess. |
| [`monitor-consumer-lag-as-primary-health-signal.md`](./monitor-consumer-lag-as-primary-health-signal.md) | Primary diagnostic | A streaming pipeline is suspected to be slow or behind — check consumer group lag first. |
| [`outbox-pattern-for-transactional-events.md`](./outbox-pattern-for-transactional-events.md) | Absolute rule | Guaranteeing event delivery from a transactional database write without dual-write races. |
| [`set-retention-and-compaction-policy-explicitly.md`](./set-retention-and-compaction-policy-explicitly.md) | Absolute rule | Creating a new topic without an explicit retention or compaction policy. |
| [`watermark-lag-drives-allowable-lateness.md`](./watermark-lag-drives-allowable-lateness.md) | Absolute rule | Setting a Flink watermark lag — measure P99 source latency, don't guess. |
| [`flink-state-ttl-to-prevent-unbounded-growth.md`](./flink-state-ttl-to-prevent-unbounded-growth.md) | Absolute rule | All keyed Flink state must have a TTL to prevent unbounded memory growth. |
| [`schema-breaking-change-is-a-new-topic.md`](./schema-breaking-change-is-a-new-topic.md) | Absolute rule | A breaking schema change (field rename, type change) must use a new topic and dual-produce migration. |
| [`document-streaming-topology-before-building.md`](./document-streaming-topology-before-building.md) | Pattern | Starting a new streaming pipeline — document the topology diagram and delivery semantics before writing code. |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — data-streaming-engineering team constitution (§2 house opinions, §3 seams).
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs.
