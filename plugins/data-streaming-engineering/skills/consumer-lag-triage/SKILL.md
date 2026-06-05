---
name: consumer-lag-triage
description: "Structured triage procedure for diagnosing and resolving Kafka consumer group lag — distinguishes slow consumer, under-partitioned topic, rebalance storm, and broker-side causes."
---

# Consumer Lag Triage

## When to Use This

A consumer group's lag is growing — either a sudden spike or a steady drift. This skill produces a root cause within 15 minutes and a remediation plan before lag becomes a data-loss or SLA risk.

## Step 1 — Confirm the Lag Is Real

```shell
# Snapshot lag per partition
kafka-consumer-groups.sh --bootstrap-server broker:9092 \
  --describe --group <group-id>
```

Check columns: `LOG-END-OFFSET`, `CURRENT-OFFSET`, `LAG`. A lag that is constant (not growing) is a healthy steady state. Proceed only if lag is increasing over successive snapshots.

## Step 2 — Narrow the Cause

| Observable | Most likely cause |
|---|---|
| Lag on ALL partitions, all consumers | Slow consumer processing; broker throughput |
| Lag on ONE partition, others fine | Hot partition; single slow consumer instance |
| Lag spikes then recovers repeatedly | Rebalance storm (frequent group rejoins) |
| Lag growing with zero consumer activity | Consumer is down / crashed |
| Lag growing despite high consumer throughput | Under-partitioned topic; need more partitions |

## Step 3 — Diagnose by Cause

**Slow consumer processing:**
- Profile the consumer's `poll()` → processing → `commit()` loop. Processing time must be < `max.poll.interval.ms` (default 5 min); exceeding it triggers a rebalance.
- Check `fetch.max.bytes` and `max.partition.fetch.bytes` — if consumers pull large batches but process slowly, reduce batch size or offload processing asynchronously.

**Rebalance storm:**
- Check `kafka.consumer:type=consumer-coordinator-metrics,attribute=rebalance-rate` metric.
- Common causes: GC pauses exceeding `session.timeout.ms`; deployment rolling restarts without graceful leave; too many partitions per consumer (> ~200 triggers slow rebalance).
- Fix: tune `session.timeout.ms` / `heartbeat.interval.ms`, enable static membership (`group.instance.id`) to survive restarts without rebalance.

**Hot partition:**
- Inspect key distribution with a short consumer that counts by key. Skew means the partition key doesn't distribute work.
- Options: re-key, add a synthetic random suffix for pure-parallel work, or use a custom partitioner.

**Broker-side:**
- Check broker CPU, disk I/O (`kafka.server:type=BrokerTopicMetrics`), and network saturation.
- Unclean leader elections or under-replicated partitions (`UnderReplicatedPartitions > 0`) introduce read stalls.

## Step 4 — Remediation Decision

```
Is the consumer keeping up when healthy (lag stable)?
  Yes → scale consumer instances (add pods/threads up to partition count)
  No  → is processing CPU/IO bound?
    Yes → offload or parallelize processing; check batch size
    No  → check rebalance; tune heartbeat/session timeouts
Is partition count < desired parallelism?
  Yes → increase partitions (irreversible; plan ordering impact)
  No  → review consumer group assignment strategy (cooperative-sticky preferred)
```

## Step 5 — Reset Offsets (Last Resort)

```shell
# Dry run first
kafka-consumer-groups.sh --bootstrap-server broker:9092 \
  --group <group-id> --reset-offsets --to-latest --topic <topic> --dry-run
# Execute
kafka-consumer-groups.sh ... --execute
```

Resetting to `--to-latest` drops all un-consumed messages. Only do this when you've confirmed the data is recoverable from another source or lag recovery is impossible.

## Pitfalls

- Increasing partition count on a keyed topic changes which partition a key maps to — messages for the same key can appear in a different partition after the increase, breaking per-key ordering.
- Adding consumer instances beyond the partition count — extra instances sit idle and contribute to rebalance overhead.
- Setting `max.poll.interval.ms` very high to mask slow processing — this hides real issues and delays rebalance detection when a consumer truly dies.
- Committing offsets before processing completes (fire-and-forget) — lag looks fine while data is actually lost on crash.

## See Also

- [`../../agents/stream-processing-engineer.md`](../../agents/stream-processing-engineer.md) — backpressure and stateful processing
- [`../../agents/kafka-pipeline-engineer.md`](../../agents/kafka-pipeline-engineer.md) — partition design and consumer group ownership
