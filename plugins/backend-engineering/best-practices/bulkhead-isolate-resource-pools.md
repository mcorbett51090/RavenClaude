# Isolate resource pools with bulkheads

**Status:** Pattern
**Domain:** Backend resilience
**Applies to:** `backend-engineering`

---

## Why this exists

A shared thread pool or connection pool is a blast-radius amplifier. When one slow downstream (a partner API, a cold database shard, a blob store) starts queuing threads waiting for responses, it consumes the entire shared pool and blocks every other independent workload — including health-check endpoints. A bulkhead partitions those pools so that saturation of one lane cannot drown the others.

## How to apply

Assign a bounded pool to each independently-fallible downstream dependency or call category. Reject new work when a pool is full rather than queueing indefinitely.

```java
// Example: Resilience4j bulkhead (semaphore)
BulkheadConfig config = BulkheadConfig.custom()
    .maxConcurrentCalls(20)       // max parallel calls to this downstream
    .maxWaitDuration(Duration.ofMillis(0)) // fail fast if full
    .build();
Bulkhead bulkhead = Bulkhead.of("payment-service", config);

// Wrap the call
Supplier<Response> decorated = Bulkhead.decorateSupplier(bulkhead, () -> paymentClient.charge(req));
Try<Response> result = Try.ofSupplier(decorated)
    .recover(BulkheadFullException.class, ex -> fallback());
```

**Do:**
- Size each pool to the realistic concurrency you expect from that downstream, not to "all available threads."
- Pair a bulkhead with a timeout — a bulkhead without a timeout still lets threads block indefinitely.
- Expose pool utilization as a metric (`active`, `available`, `rejected`) and alert on sustained full-pool.
- Apply bulkheads to thread pools *and* connection pools (database, HTTP client).

**Don't:**
- Use one global pool for all downstream calls.
- Set pool sizes so large they defeat the isolation (a pool of 500 on a 500-thread server is no bulkhead).
- Silently drop rejected work — record rejections as a distinct metric so they are visible in dashboards.

## Edge cases / when the rule does NOT apply

A service with a single downstream dependency gains little from a bulkhead; the entire service is already coupled to that one dependency. In that case, a circuit breaker and timeout alone are sufficient. Also skip bulkheads for fire-and-forget async workers where each job already runs in its own isolated consumer.

## See also

- [`../agents/backend-reliability-engineer.md`](../agents/backend-reliability-engineer.md) — owns resilience pattern design.
- [`./use-circuit-breakers-for-downstream-dependencies.md`](./use-circuit-breakers-for-downstream-dependencies.md) — circuit breakers trip on failure rates; bulkheads cap concurrency — use both together.
- [`./timeout-and-bounded-retry.md`](./timeout-and-bounded-retry.md) — bulkheads without timeouts still block.

## Provenance

Standard distributed-systems resilience pattern from Michael Nygard's _Release It!_ and the Netflix Hystrix / Resilience4j lineage. Codifies the `backend-reliability-engineer` responsibility for preventing cascading failures.

---

_Last reviewed: 2026-06-05 by `claude`_
