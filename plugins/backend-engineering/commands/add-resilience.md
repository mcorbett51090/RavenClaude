---
description: "Add backend resilience: timeouts, idempotent-only backoff+jitter retries, circuit breakers, degraded mode, and idempotent workers with DLQs."
argument-hint: "[dependency / async workload + failure modes]"
---

You are running `/backend-engineering:add-resilience`. Use `backend-reliability-engineer` + the `backend-resilience` skill.

## Steps
1. Timeout every outbound call; size to the dependency.
2. Bounded retries (idempotent only) with backoff+jitter; add circuit breaker + bulkhead.
3. Define the degraded mode; design workers with idempotency + DLQ + backpressure.
4. Route protected SLOs to observability-sre.
5. Emit (from `templates/resilience-config.md`) + Structured Output block.
