# Rate-limit all inbound surfaces

**Status:** Absolute rule
**Domain:** Backend resilience / resource protection
**Applies to:** `backend-engineering`

---

## Why this exists

An API endpoint or queue consumer without a rate limit is an open door to resource exhaustion. A single misbehaving caller — whether a bug loop, a DDoS, or an over-eager retry — can saturate your thread pool, database connections, or downstream quota and take every other tenant down with them. Rate limiting is a safety floor, not an optional enhancement; the cost of not having it is paid suddenly and at scale.

## How to apply

Apply limits at two layers: at the edge (gateway / reverse proxy) for coarse protection, and in the service itself for per-resource / per-tenant granularity the gateway cannot reason about.

```
# Example: Redis token bucket per caller (pseudo-code)
key = "rate:<tenant>:<endpoint>"
allowed = redis.incr(key)  # atomic increment
if allowed == 1:
    redis.expire(key, window_seconds)
if allowed > limit:
    raise TooManyRequestsError(retry_after=redis.ttl(key))
```

Return `429 Too Many Requests` with a `Retry-After` (seconds or date) header. Advertise the limit, remaining tokens, and reset time in `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset` response headers so clients can self-throttle.

**Do:**
- Set limits per-caller (tenant/user/IP), not just global.
- Apply limits before expensive work (auth, DB queries, external calls).
- Log limit-hit events at WARN; alert on sustained high rates.
- Return `429` (not `503`) — `429` tells the client to back off, `503` signals a transient service fault.

**Don't:**
- Silently drop requests instead of returning a structured `429`.
- Set the same limit for every endpoint — a search endpoint is cheaper than a file-upload endpoint.
- Forget queue consumers; an uncapped consumer can overwhelm a downstream database.

## Edge cases / when the rule does NOT apply

Internal service-to-service calls on a private mesh with a circuit breaker already capping concurrency may not need a per-request token bucket — but still need bulkhead concurrency limits. Batch/ETL pipelines that run on a schedule with a known single caller can substitute a concurrency limit for a rate limit.

## See also

- [`../agents/backend-reliability-engineer.md`](../agents/backend-reliability-engineer.md) — owns resource-consumption limits and resilience patterns.
- [`./use-circuit-breakers-for-downstream-dependencies.md`](./use-circuit-breakers-for-downstream-dependencies.md) — complements rate limiting: limits your inbound; circuit breakers protect your outbound.

## Provenance

Codifies `backend-reliability-engineer`'s resource-consumption defence posture and mirrors OWASP API4 (unrestricted resource consumption) applied at the service layer. Standard practice across high-traffic backend systems.

---

_Last reviewed: 2026-06-05 by `claude`_
