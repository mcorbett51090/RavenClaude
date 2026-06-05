# backend-engineering — best-practice docs

Named, citable rules for the `backend-engineering` plugin's specialists. Each file is **one rule**.

---

## Index

_26 rules across domain modeling, data access, resilience, async workers, and observability._

| Doc | Status | Use when |
|---|---|---|
| [`modular-monolith-first.md`](./modular-monolith-first.md) | Absolute rule | Starting a service — default to a single deployable and split only when there's a concrete need. |
| [`bounded-contexts-own-their-data.md`](./bounded-contexts-own-their-data.md) | Absolute rule | Designing service/module boundaries — each owns its data, shares nothing via a shared DB. |
| [`service-layer-owns-business-logic.md`](./service-layer-owns-business-logic.md) | Absolute rule | Structuring a service — logic lives in use-case/service classes, not in controllers or models. |
| [`validate-at-the-boundary-not-in-the-core.md`](./validate-at-the-boundary-not-in-the-core.md) | Absolute rule | Input arrives from outside the service — validate and parse at the edge before it enters the core. |
| [`model-errors-explicitly.md`](./model-errors-explicitly.md) | Pattern | Returning errors — model them as first-class types, not thrown exceptions caught by accident. |
| [`config-and-secrets-from-the-environment.md`](./config-and-secrets-from-the-environment.md) | Absolute rule | Any configuration value — inject from the environment; never hard-code or commit. |
| [`own-the-data-access-layer.md`](./own-the-data-access-layer.md) | Absolute rule | Any database interaction — queries belong behind a repository/data layer, not scattered through business code. |
| [`keep-transactions-short-and-off-the-network.md`](./keep-transactions-short-and-off-the-network.md) | Absolute rule | Opening a database transaction — keep it short, local, and free of outbound I/O. |
| [`never-cache-without-invalidation.md`](./never-cache-without-invalidation.md) | Absolute rule | Adding a cache — define the invalidation trigger and TTL before writing the caching code. |
| [`idempotency-for-retried-operations.md`](./idempotency-for-retried-operations.md) | Absolute rule | Any retried operation (webhooks, payments, async workers) — carry a dedup key so a retry is a no-op. |
| [`use-the-outbox-for-write-then-publish.md`](./use-the-outbox-for-write-then-publish.md) | Absolute rule | Writing to the DB and publishing an event — use the outbox pattern to avoid dual-write loss. |
| [`queues-need-backpressure-and-a-dlq.md`](./queues-need-backpressure-and-a-dlq.md) | Absolute rule | Adding a message queue — bound concurrency and configure a DLQ before deploying. |
| [`dead-letter-queues-are-mandatory.md`](./dead-letter-queues-are-mandatory.md) | Absolute rule | Deploying a consumer — a DLQ is not optional; poison messages must not bounce indefinitely. |
| [`never-block-the-event-loop-or-pool.md`](./never-block-the-event-loop-or-pool.md) | Absolute rule | Async/event-loop runtimes — never put synchronous blocking I/O on the main loop or thread pool. |
| [`timeout-and-bounded-retry.md`](./timeout-and-bounded-retry.md) | Absolute rule | Every outbound call — set a timeout; retry with exponential backoff + jitter, idempotent calls only. |
| [`use-circuit-breakers-for-downstream-dependencies.md`](./use-circuit-breakers-for-downstream-dependencies.md) | Pattern | A downstream dependency that is flaky or slow — wrap it in a circuit breaker to fail fast. |
| [`rate-limit-all-inbound-surfaces.md`](./rate-limit-all-inbound-surfaces.md) | Absolute rule | Any API endpoint or queue consumer — apply per-caller rate limits to prevent resource exhaustion. |
| [`bulkhead-isolate-resource-pools.md`](./bulkhead-isolate-resource-pools.md) | Pattern | Multiple independent downstream dependencies — isolate thread/connection pools so one can't starve others. |
| [`domain-events-not-anemic-models.md`](./domain-events-not-anemic-models.md) | Pattern | Modeling business behavior — encode intent in domain methods and named past-tense events, not scattered logic. |
| [`graceful-degradation-not-total-failure.md`](./graceful-degradation-not-total-failure.md) | Pattern | Any optional downstream dependency — define the degraded fallback before shipping. |
| [`worker-heartbeats-and-lease-timeouts.md`](./worker-heartbeats-and-lease-timeouts.md) | Absolute rule | Long-running background workers — renew a lease with heartbeats so stuck jobs are detected and requeued. |
| [`read-write-separation-at-the-app-layer.md`](./read-write-separation-at-the-app-layer.md) | Pattern | Adding read replicas or a read model — route reads and writes explicitly at the repository layer. |
| [`health-endpoints-for-every-service.md`](./health-endpoints-for-every-service.md) | Absolute rule | Any deployed service — expose `/health/live` and `/health/ready` so the orchestrator can route correctly. |
| [`structured-logging-with-correlation-ids.md`](./structured-logging-with-correlation-ids.md) | Absolute rule | Any request or job — emit structured JSON logs with a correlation ID on every log line. |
| [`avoid-distributed-transactions-prefer-eventual.md`](./avoid-distributed-transactions-prefer-eventual.md) | Absolute rule | Writing across multiple services — design for eventual consistency; avoid distributed transactions. |
| [`pagination-for-every-list-endpoint.md`](./pagination-for-every-list-endpoint.md) | Absolute rule | Any list endpoint — paginate and cap the result size; never return an unbounded set. |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — plugin team constitution.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs.
