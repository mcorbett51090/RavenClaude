# Data Streaming Engineering Plugin — Team Constitution

> Team constitution for the `data-streaming-engineering` Claude Code plugin — **3** specialist agents for real-time data infrastructure done right — event streaming and CDC (Kafka/Pulsar/Kinesis), stream processing with correct time/windowing/state, and delivery semantics (exactly-once vs at-least-once) — distinct from data-platform's batch ELT. The Team Lead (the top-level Claude session, typically also running `ravenclaude-core`) dispatches the right specialist(s) and integrates their reports.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).


---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`streaming-architect`](agents/streaming-architect.md) | Streaming architecture: the streaming-vs-batch decision, the topology (sources/topics/processors/sinks), the platform choice (Kafka/Pulsar/Kinesis), delivery-semantics strategy, and the CDC approach | "do we need streaming or is batch fine?", "design our event streaming topology", "Kafka or Kinesis?", "how should we do CDC?" |
| [`kafka-pipeline-engineer`](agents/kafka-pipeline-engineer.md) | The streaming platform and ingestion: topic/partition design, keys and ordering, the schema registry + compatibility/evolution, producers/consumers and consumer groups, CDC (Debezium) pipelines, and connector configuration | "design our Kafka topics", "our schema change broke consumers", "set up CDC from Postgres", "how should we partition this?" |
| [`stream-processing-engineer`](agents/stream-processing-engineer.md) | Stream processing: event-time vs processing-time, windowing (tumbling/sliding/session), watermarks and late data, stateful processing + checkpointing, stream-stream and stream-table joins, and backpressure handling (Flink / Kafka Streams) | "our windowed aggregation is wrong", "handle late-arriving events", "join two streams", "our processor is falling behind" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.


## 2. Cross-cutting house opinions (every agent enforces)

1. **Stream only when latency demands it.** Real-time infra is operationally heavy. If the business need is hourly/daily, batch ELT (data-platform) is simpler and cheaper. Streaming is for genuine low-latency needs, not fashion.
2. **Event-time, not processing-time, for correctness.** Events arrive late and out of order. Window and aggregate on the event's own timestamp with watermarks — processing-time aggregations are wrong the moment the network hiccups.
3. **Pick the delivery semantic deliberately.** At-least-once + idempotent consumers is the pragmatic default; exactly-once costs throughput and complexity and is only truly end-to-end with transactional sinks. Name what you need.
4. **Partition for parallelism and ordering — they conflict.** Order is per-partition only. Choose the partition key for the ordering guarantee you need; over-partitioning kills order, under-partitioning kills throughput.
5. **Schemas evolve; govern them.** A schema registry with compatibility rules (backward/forward) keeps a producer change from breaking every consumer. An unversioned event payload is a future outage.
6. **State and backpressure are first-class.** Stream processors hold state (checkpoint it) and must handle backpressure (a fast producer + slow consumer = unbounded lag or OOM). Design both, don't discover them.

## 3. Seams (the bridges to neighbouring plugins)

- **Batch ELT, warehouse loading, and scheduled pipelines** → `data-platform`; this team owns real-time/streaming, that one owns batch. The litmus: sub-minute latency need → here; hourly/daily → there.
- **The transform layer (dbt) consuming streamed data once landed** → `analytics-engineering`.
- **Event/AsyncAPI contracts for the streams** → `api-engineering` (AsyncAPI); we own the transport + processing.
- **Microsoft Fabric Real-Time Intelligence (Eventstream/Eventhouse/KQL)** → `microsoft-fabric` (the Microsoft-native streaming lane).
- **App-side messaging/queues and the outbox in service code** → `backend-engineering`; we own the streaming platform and CDC.

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol (decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the dated capability map.
