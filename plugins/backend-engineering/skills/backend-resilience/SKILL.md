---
name: backend-resilience
description: "Make the backend survive its dependencies: timeout every outbound call, retry idempotent-only with exponential backoff + jitter, add circuit breakers and bulkheads, define a graceful-degradation mode, and design idempotent background workers with DLQs and backpressure."
---

# Backend Resilience

## Timeouts
Every outbound call has one (sized to the dependency's SLO). No timeout = cascading outage.

## Retries
**Idempotent only**, bounded, exponential backoff + **jitter** (avoid synchronized storms). A retry on a non-idempotent call = a duplicate.

## Isolate
**Circuit breaker** (fail fast on a failing dep) + **bulkhead** (one slow dep can't starve the rest).

## Degrade + async
Define the degraded mode (stale cache / queued / clear error). Workers: **idempotent** + **DLQ** + **bounded queue** (backpressure, not unbounded growth).
