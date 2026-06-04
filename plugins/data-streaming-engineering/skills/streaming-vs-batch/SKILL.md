---
name: streaming-vs-batch
description: "Decide streaming vs batch honestly by the real latency need (sub-minute reaction -> streaming; hourly/daily -> batch via data-platform), then design the topology, platform choice, and delivery semantics if streaming is justified."
---

# Streaming vs Batch

## Decide by latency need
| Need | Approach |
|---|---|
| Sub-minute reaction / real-time | **Streaming** |
| Hourly / daily analytics | **Batch ELT** -> data-platform |

Streaming is operationally heavy — justify it with latency, not novelty.

## If streaming
Topology: sources -> topics (partitioned/keyed) -> processors -> sinks, **delivery semantic named at each hop**. Platform by fit (Kafka default / Pulsar multi-tenant / Kinesis AWS-managed). Get data in via **CDC/outbox**, never dual-writes.
