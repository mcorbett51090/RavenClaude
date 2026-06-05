# Set watermark lag based on observed source latency — not as a fixed constant

**Status:** Absolute rule
**Domain:** Flink / stream processing / event-time
**Applies to:** `data-streaming-engineering`

---

## Why this exists

A watermark declares the maximum expected delay between event time and arrival time. Set it too small and late-arriving events are dropped (windows close before they arrive). Set it too large and every window result is delayed by the watermark lag — a 10-minute watermark means no window fires for 10 minutes after the window's event-time boundary, even when all events have arrived. The correct watermark lag is measured from the observed 99th-percentile source-to-Kafka latency on the actual data path, not from a guess or a safety margin.

## How to apply

**Step 1 — Measure source latency:**
```python
# Measure the gap between event_time and processing_time for a sample of events
gap_p50 = percentile(arrival_time - event_time, 50)   # typical delay
gap_p99 = percentile(arrival_time - event_time, 99)   # worst-case delay
```

**Step 2 — Set watermark lag to the P99 delay + a small buffer:**
```java
// Apache Flink: WatermarkStrategy for an event stream
WatermarkStrategy
    .<Order>forBoundedOutOfOrderness(Duration.ofSeconds(30))  // P99 + 10s buffer
    .withTimestampAssigner((event, ts) -> event.getEventTimestampMs());
```

**Step 3 — Set an explicit allowedLateness on the window:**
```java
stream
    .keyBy(Order::getTenantId)
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .allowedLateness(Duration.ofMinutes(2))  // retrigger the window up to 2 min after it fires
    .aggregate(new RevenueAggregator());
```

**Do:**
- Re-measure source latency after any change to the producer, network topology, or batch size.
- Use `allowedLateness` to retrigger windows for late data rather than discarding it silently.
- Route truly late events (past `allowedLateness`) to a side output for auditing — don't discard them.

**Don't:**
- Set watermark lag to a round number (`5 minutes`) without measuring actual source latency.
- Use processing-time watermarks as a substitute for event-time watermarks when events can arrive out of order.
- Increase the watermark indefinitely to "never drop data" — this increases window latency for all results.

## Edge cases / when the rule does NOT apply

- Pure processing-time applications (e.g., a stateless filter on a real-time alerting pipeline with no windowing) don't use event-time watermarks.
- Kafka Streams applications that use `suppress` rather than `allowedLateness` have a different but equivalent late-data policy mechanism.

## See also

- [`../agents/stream-processing-engineer.md`](../agents/stream-processing-engineer.md) — owns windowing and watermark configuration
- [`./handle-late-data-explicitly.md`](./handle-late-data-explicitly.md) — the late-data policy rule that watermark sizing feeds into

## Provenance

Apache Flink documentation on watermarks and event-time processing. The P99-plus-buffer approach is the standard production recommendation. Codifies data-streaming-engineering CLAUDE.md §2 house opinion #2 ("Event-time, not processing-time, for correctness").

---

_Last reviewed: 2026-06-05 by `claude`_
