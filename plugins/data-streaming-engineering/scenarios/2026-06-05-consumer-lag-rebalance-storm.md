---
scenario_id: 2026-06-05-consumer-lag-rebalance-storm
contributed_at: 2026-06-05
plugin: data-streaming-engineering
product: kafka
product_version: "3.6"
scope: likely-general
tags: [consumer-lag, rebalance, max-poll, cooperative-sticky, partition-assignment, heartbeat]
confidence: high
reviewed: false
---

## Problem

A consumer group on a high-volume topic (~40k msg/s, 24 partitions, 8 consumers) was stuck in a rebalance storm: lag climbed steadily, then every ~30–60s the whole group rebalanced, every consumer paused, and lag jumped again. The group never reached steady state. `kafka-consumer-groups --describe` showed the same members leaving and rejoining, and the broker log was full of "member ... failed, removing it from the group" lines. Lag was monotonically increasing — the pipeline was effectively down even though every consumer was "running."

## Constraints context

- At-least-once delivery; the handler did a synchronous downstream HTTP call per message that occasionally took 2–4s under load.
- `max.poll.records` was the default (500); `max.poll.interval.ms` was the default (5 min); the default `RangeAssignor` was in use (stop-the-world rebalances).
- Offsets were auto-committed (`enable.auto.commit=true`, 5s interval).

## Attempts

- Tried: **adding more consumers** (8 → 16). Made it *worse* — more members meant a bigger, slower rebalance and now some consumers were idle (only 24 partitions). The bottleneck was never consumer count.
- Tried: **bumping `session.timeout.ms`**. Helped the heartbeat-expiry flavor of eviction a little, but the group still rebalanced — because the real eviction was `max.poll.interval.ms`, not the heartbeat. The heartbeat runs on a background thread; the poll-interval timer is what a slow handler blows.
- Tried: **reducing `max.poll.records` to 50 + raising `max.poll.interval.ms`, switching to `CooperativeStickyAssignor`, and moving the slow HTTP call off the poll-loop critical path.** This is the resolution — the group reached steady state and lag drained.

## Resolution

**A rebalance storm under lag is almost always "the handler takes longer than `max.poll.interval.ms` to process one `poll()` batch," not "not enough consumers."** When a batch can't be processed before the poll-interval deadline, the broker assumes the consumer is dead, evicts it, and rebalances — which pauses everyone, which makes the next batch later, which evicts the next consumer. It's self-reinforcing.

1. **Diagnose the eviction cause before touching parallelism.** Heartbeat-expiry (`session.timeout.ms`) and poll-interval-expiry (`max.poll.interval.ms`) are different evictions with different fixes. A slow *handler* trips the poll interval; network/GC pauses trip the heartbeat. The broker log and the consumer's own "rebalance" log lines tell you which.
2. **Bound the work per poll.** Lower `max.poll.records` so one batch is processable inside the poll interval, and/or raise `max.poll.interval.ms` to cover the worst-case batch time. The product `max.poll.records × per-record time` must be `< max.poll.interval.ms` with margin.
3. **Get slow I/O off the poll loop.** A multi-second synchronous downstream call per record is the root cause. Batch the downstream calls, parallelize within the handler, or hand off to a bounded worker pool — so `poll()` is called again promptly.
4. **Use a cooperative assignor.** `CooperativeStickyAssignor` (incremental cooperative rebalancing) avoids the stop-the-world pause of the eager `RangeAssignor`/`RoundRobinAssignor` — consumers keep their unaffected partitions during a rebalance instead of all dropping everything. This alone shrinks the blast radius of each rebalance.
5. **More consumers than partitions does nothing.** Parallelism is capped at the partition count. 16 consumers on 24 partitions is fine; 16 on 12 leaves 4 idle. If you genuinely need more parallelism, add partitions (and re-check your keying — see the partition-skew scenario).

The trap is that "lag is high → add consumers" is the wrong reflex when the group is already rebalancing: more members lengthens the rebalance and can't help past the partition count. Fix the per-batch processing time first; scale second.

**Action for the next engineer:** if lag is climbing AND the group is rebalancing repeatedly, do NOT add consumers first. Check *why* members are being evicted (poll-interval vs heartbeat), bound the per-poll work, and switch to `CooperativeStickyAssignor`. Add consumers/partitions only after the group reaches steady state.

Cross-reference: complements [`../best-practices/monitor-consumer-lag-as-primary-health-signal.md`](../best-practices/monitor-consumer-lag-as-primary-health-signal.md), [`../best-practices/partition-for-ordering-and-parallelism.md`](../best-practices/partition-for-ordering-and-parallelism.md), and the [`consumer-lag-triage`](../skills/consumer-lag-triage/SKILL.md) skill. The broker/infra sizing → the cloud plugin; the SLOs lag protects → `observability-sre`.
