---
scenario_id: 2026-06-05-out-of-order-watermark-late-data
contributed_at: 2026-06-05
plugin: data-streaming-engineering
product: flink
product_version: "1.19"
scope: likely-general
tags: [event-time, watermark, late-data, windowing, allowed-lateness]
confidence: high
reviewed: false
---

## Problem

A Flink job computing per-minute revenue from a mobile-app event stream produced numbers that didn't match the batch reconciliation: some minutes were ~10–15% low, and the discrepancy was worst during evening peak. The owner's first theory was "we're losing events." Events weren't being lost — they were arriving **late and out of order** (mobile clients buffer offline, then flush; a 7:01pm event could land at 7:04pm) and the windowed aggregation was either dropping them or had already closed and emitted the window before they arrived. Processing-time intuition ("the event happened when we saw it") was baked into the job.

## Constraints context

- Source was a Kafka topic of mobile telemetry; clients on flaky networks buffered events and sent them in bursts, so event-time-vs-arrival skew ranged from seconds to a few minutes, spiking at peak.
- The Flink job had been written with a tumbling **processing-time** window initially, then "fixed" to event-time but with an **aggressive watermark** (`forBoundedOutOfOrderness(Duration.ofSeconds(2))`) that assumed near-real-time arrival — so a watermark advanced past 7:02 while 7:01 events were still in flight, closing the 7:01 window early.
- No late-data handling: events arriving after the watermark passed their window were silently dropped (Flink's default).

## Attempts

- Tried: **switching from processing-time to event-time windows.** Necessary but not sufficient — the window now used the event's own timestamp, but the 2-second watermark still declared completeness before the late mobile events arrived, so the windows still closed too early and dropped the stragglers.
- Tried: **making the watermark hugely conservative** (`forBoundedOutOfOrderness(Duration.ofMinutes(10))`) to cover the worst-case lateness. It captured the late events but pushed end-to-end latency to 10+ minutes for *every* window — trading the correctness problem for a latency problem, and over-buffering state.
- Tried: **a realistic watermark sized to the p99 observed lateness (~90s) + `allowedLateness` + a side output for the truly-late stragglers + idempotent late updates to the sink.** This is the resolution — windows close at a sane latency, most lateness is absorbed by the watermark bound, the long tail updates the result instead of being dropped, and nothing is silently lost.

## Resolution

**Watermark lag is a latency-vs-completeness dial, and "late data" is whatever arrives after the watermark passes its window — you must size the watermark to real observed lateness and have an explicit policy for the tail, not drop it silently.** A windowed aggregation on event-time with a too-tight watermark drops exactly the late events that make the numbers low.

1. **Size the watermark to measured lateness, not a guess.** Measure the event-time-to-arrival skew distribution (it spiked at peak here). Set the bounded-out-of-orderness to around the p99 (~90s), accepting that fraction as the window-close latency. Too tight drops late data; too loose taxes every window's latency and state. It's a dial — set it from data.
2. **Add `allowedLateness` for the tail past the watermark.** The watermark handles the bulk; `allowedLateness` keeps the window state around a bit longer so events arriving after the watermark (but within the lateness grace) trigger a *recomputation* and an updated emission, rather than a drop. The sink must accept the update (see #4).
3. **Route truly-late events to a side output — never drop silently.** Events later than watermark + allowedLateness go to a `sideOutputLateData` stream. Now "we're losing events" becomes an observable, countable late-event stream you can alarm on and reconcile, instead of an invisible 10–15% shortfall. A spike in the side output is the early warning the original job didn't have.
4. **Make the sink idempotent for late updates.** A window that re-emits after a late event must *replace* the prior value for that window key, not add to it — keyed upsert on `(window_start, key)`. Otherwise allowedLateness produces double-counting (the mirror image of the original undercount).

The trap is reasoning in processing-time ("it happened when we saw it") on a source that arrives late and out of order. Event-time fixes *which* timestamp; the watermark + allowedLateness + side output fix *completeness*; the idempotent sink fixes the re-emission. All four are needed — event-time alone, with a tight watermark and no late-data policy, still drops the stragglers.

**Action for the next engineer:** if windowed numbers run low versus a batch reconciliation, suspect late/out-of-order data before "lost events." Measure the arrival-skew distribution, size the watermark to the p99, add `allowedLateness` + a late-data side output, and make the sink idempotent so late re-emissions correct rather than double-count. Watch the side-output rate as the completeness health signal.

Cross-reference: complements [`../best-practices/event-time-not-processing-time.md`](../best-practices/event-time-not-processing-time.md), [`../best-practices/handle-late-data-explicitly.md`](../best-practices/handle-late-data-explicitly.md), [`../best-practices/watermark-lag-drives-allowable-lateness.md`](../best-practices/watermark-lag-drives-allowable-lateness.md), the [`../knowledge/data-streaming-engineering-decision-trees.md`](../knowledge/data-streaming-engineering-decision-trees.md) `## Decision Tree: Which window type?`, and the [`../skills/stream-processing/SKILL.md`](../skills/stream-processing/SKILL.md) skill. The batch reconciliation source → `data-platform`; the SLOs the latency dial trades against → `observability-sre`.
