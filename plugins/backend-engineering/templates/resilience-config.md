# Resilience config (per outbound dependency)

| Dependency | Timeout | Retries (idempotent?) | Backoff | Breaker | Degraded mode |
|---|---|---|---|---|---|
| payment API | 3s | 2, idempotent | expo+jitter | 5 fails/30s | queue + notify |
| search | 1s | 0 | — | 10 fails/10s | cached results |

Workers: idempotent consumer + DLQ + bounded queue (backpressure).
