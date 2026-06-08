---
scenario_id: 2026-06-08-optimized-the-wrong-thing
contributed_at: 2026-06-08
plugin: performance-engineering
product: async-profiler
product_version: "unknown"
scope: likely-general
tags: [profiling, flame-graph, use-red, off-cpu, bottleneck, capacity]
confidence: high
reviewed: false
---

## Problem

A service's p99 ballooned past ~2,000 req/s. The team spent two sprints micro-optimizing a JSON serialization path they "knew" was hot — cached more, swapped the library — and p99 barely moved. The system still fell over at the same point.

## Constraints context

- JVM service; the team had a strong prior that serialization was the cost because it showed up in a quick sampled CPU profile.
- No off-CPU profiling and no USE/RED breakdown had been done — the "bottleneck" was a guess backed by one partial profile.
- They needed to size for a 2x launch and couldn't, because they didn't know the real limit.

## Attempts

- Tried: optimizing the serialization hot path (caching, a faster library). Failed — the on-CPU flame graph did show serialization, but the system was mostly *off* CPU when it was slow, so on-CPU work wasn't the constraint.
- Tried: adding more instances to brute-force the throughput. Failed — without knowing the bottleneck, scaling out just multiplied the contention; the saturation point per instance didn't improve.
- Tried: an off-CPU flame graph (async-profiler) plus a USE walk of every resource. This worked — it showed threads blocked on a connection-pool semaphore waiting for a downstream DB call; the pool was the saturated resource, not CPU.

## Resolution

The off-CPU profile and the USE breakdown (saturation on the DB connection pool) named the real constraint: a synchronous DB call on the hot path starving a too-small pool. The serialization work had been speeding up the thing that wasn't slow. The DB-side fix routed to the database-engineering team; capacity was then computed with Little's law against the *measured* per-instance saturation point plus failover headroom, and the 2x sizing finally had a defensible number.

## Lesson

Profile before you optimize, and read the off-CPU profile — the worst latency is often a thread blocked on a lock, pool, or downstream, which an on-CPU flame graph alone never shows. USE (saturation per resource), not intuition, names the bottleneck; size capacity from the measured saturation point with headroom, never from a guess.
