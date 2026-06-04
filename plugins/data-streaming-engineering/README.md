# Data Streaming Engineering

The **data-streaming-engineering** plugin — real-time data infrastructure done right — event streaming and CDC (Kafka/Pulsar/Kinesis), stream processing with correct time/windowing/state, and delivery semantics (exactly-once vs at-least-once) — distinct from data-platform's batch ELT.

## Agents

- **`streaming-architect`** — Streaming architecture: the streaming-vs-batch decision, the topology (sources/topics/processors/sinks), the platform choice (Kafka/Pulsar/Kinesis), delivery-semantics strategy, and the CDC approach
- **`kafka-pipeline-engineer`** — The streaming platform and ingestion: topic/partition design, keys and ordering, the schema registry + compatibility/evolution, producers/consumers and consumer groups, CDC (Debezium) pipelines, and connector configuration
- **`stream-processing-engineer`** — Stream processing: event-time vs processing-time, windowing (tumbling/sliding/session), watermarks and late data, stateful processing + checkpointing, stream-stream and stream-table joins, and backpressure handling (Flink / Kafka Streams)

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install data-streaming-engineering@ravenclaude
```

## Seams

- **Batch ELT, warehouse loading, and scheduled pipelines** → `data-platform`; this team owns real-time/streaming, that one owns batch. The litmus: sub-minute latency need → here; hourly/daily → there.
- **The transform layer (dbt) consuming streamed data once landed** → `analytics-engineering`.
- **Event/AsyncAPI contracts for the streams** → `api-engineering` (AsyncAPI); we own the transport + processing.
- **Microsoft Fabric Real-Time Intelligence (Eventstream/Eventhouse/KQL)** → `microsoft-fabric` (the Microsoft-native streaming lane).
- **App-side messaging/queues and the outbox in service code** → `backend-engineering`; we own the streaming platform and CDC.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`.
