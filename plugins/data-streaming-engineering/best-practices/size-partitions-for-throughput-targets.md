# Size partition counts against measured throughput targets — not as a future-proofing guess

**Status:** Pattern
**Domain:** Kafka / partition design
**Applies to:** `data-streaming-engineering`

---

## Why this exists

Over-partitioning is the most common Kafka sizing mistake. Partitions are not free: each partition is a file descriptor, a replication leader, a metadata entry, and a state partition in every consumer group. A topic with 200 partitions for a throughput that needs 8 adds overhead to every broker rebalance, controller election, and consumer group coordination event. Under-partitioning is rarer but is a hard ceiling: you cannot consume faster than one partition per consumer thread. The correct partition count is derived from the measured or expected throughput target, not from "more partitions = more parallelism."

## How to apply

**Formula:**
```
partition_count = ceil(max_throughput_MB_per_sec / min(producer_rate, consumer_rate))
```

For most SMB-scale streaming workloads:

| Throughput target | Starting partition count |
|---|---|
| < 10 MB/s | 3-6 |
| 10-50 MB/s | 6-12 |
| 50-200 MB/s | 12-30 |
| > 200 MB/s | Measure first, then decide |

**Rule of thumb:** start conservative (3-6 for a new topic), then scale up by adding partitions after measuring consumer lag. You can always add partitions — you cannot remove them without a topic rebuild.

**Do:**
- Measure (or estimate) the expected message rate and size before setting partition count.
- Start with a lower count and increase based on observed consumer lag metrics.
- Document the throughput rationale in the topic's runbook entry.

**Don't:**
- Set partition count to 100+ "for future growth" on a low-throughput topic.
- Assume more partitions always means faster — they increase broker and consumer overhead.
- Change partition count on a keyed topic without a migration plan (partitions determine key-to-partition mapping; adding partitions breaks key ordering for existing data).

## Edge cases / when the rule does NOT apply

- Compacted changelog topics (used for KTable materialization) should be sized for state size and consumer parallelism, not message throughput — apply the same formula but substitute state-segment count for throughput.
- A topic that will be scaled to many consumer instances in the future may warrant a higher partition count if adding partitions later would break key ordering requirements (plan the future key-ordering guarantee first).

## See also

- [`../agents/kafka-pipeline-engineer.md`](../agents/kafka-pipeline-engineer.md) — owns partition design
- [`./partition-for-ordering-and-parallelism.md`](./partition-for-ordering-and-parallelism.md) — the ordering/parallelism trade-off rule this extends

## Provenance

Grounded in Apache Kafka performance documentation and Confluent's partitioning guidelines. Standard practice: measure, start low, scale up. Codifies data-streaming-engineering CLAUDE.md §2 house opinion #4 ("Partition for parallelism and ordering — they conflict").

---

_Last reviewed: 2026-06-05 by `claude`_
