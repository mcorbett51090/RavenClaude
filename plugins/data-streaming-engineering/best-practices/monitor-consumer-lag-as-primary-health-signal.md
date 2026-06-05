# Monitor consumer group lag as the primary streaming pipeline health signal

**Status:** Primary diagnostic
**Domain:** Kafka / observability
**Applies to:** `data-streaming-engineering`

---

## Why this exists

Consumer lag — the offset distance between the producer's latest committed offset and the consumer group's committed offset — is the single number that tells you whether a streaming pipeline is keeping up. A pipeline that processes every message but is 10 minutes behind on a 5-minute SLA is failing, and lag is the only signal that catches it before the downstream consumer (a dashboard, a database, an alert) surfaces the wrong data. Lag is also the primary signal for backpressure: an increasing lag trend means the consumer is slower than the producer and will eventually fall behind indefinitely if not addressed.

## How to apply

**Monitor with `kafka-consumer-groups.sh` or the Kafka AdminClient API:**

```bash
kafka-consumer-groups.sh \
  --bootstrap-server kafka:9092 \
  --describe --group commerce-order-processor
```

Output: `LAG` column per partition. Aggregate across partitions for total lag.

**Prometheus + Kafka exporter (recommended for production):**

```yaml
# Alert rule
- alert: KafkaConsumerLagHigh
  expr: kafka_consumergroup_lag_sum{consumergroup="commerce-order-processor"} > 10000
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Consumer group {{ $labels.consumergroup }} lag > 10k messages for 5m"
```

**Lag SLA targets by pipeline class:**

| Pipeline class | Acceptable lag | Alert threshold |
|---|---|---|
| Real-time alert/action | < 1k messages | > 5k |
| Near-real-time dashboard | < 10k messages | > 50k |
| Data-warehouse sink | < 100k messages | > 500k |

**Do:**
- Set lag alerts for every consumer group in production.
- Trend lag over time (increasing = a growing problem; stable high lag = acceptable for batch-style consumers).
- Alert on lag growth rate, not just absolute lag (a stable 100k is fine; a growing 100k→500k in an hour is not).

**Don't:**
- Use producer/consumer throughput metrics as the primary health signal — lag is what matters.
- Ignore a lag spike during deployments (expected) vs. a sustained lag increase (a real problem).
- Mix lag-per-partition views with aggregate lag — check both; a skewed partition is masked in the aggregate.

## Edge cases / when the rule does NOT apply

- Consumer groups that intentionally process in micro-batches (e.g., a daily warehouse sink that consumes once per hour) will show high lag between runs — this is expected; the alert threshold should reflect the batch window, not a real-time SLA.

## See also

- [`../agents/stream-processing-engineer.md`](../agents/stream-processing-engineer.md) — owns backpressure and lag handling in processing jobs
- [`./bound-state-and-handle-backpressure.md`](./bound-state-and-handle-backpressure.md) — the backpressure rule that lag detection feeds into

## Provenance

Standard Apache Kafka operational practice. Lag monitoring is the canonical first-line diagnostic recommended in Confluent's "Kafka in Production" documentation. Codifies data-streaming-engineering CLAUDE.md §2 house opinion #6 ("State and backpressure are first-class").

---

_Last reviewed: 2026-06-05 by `claude`_
