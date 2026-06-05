# Use Circuit Breakers for Downstream Dependencies

**Status:** Absolute rule
**Domain:** backend resilience
**Applies to:** `backend-engineering`

---

## Why this exists

A slow or failing downstream dependency will hold your threads, exhaust your connection pool, and cascade into total service failure unless the circuit opens and fast-fails. Without a circuit breaker, a single degraded dependency can take down every consumer in the call graph. The pattern separates "dependent is down" from "we are down."

## How to apply

Wire a circuit breaker around every outbound call to an external service, database, or third-party API. The breaker tracks failure rate over a rolling window; once the threshold is crossed it opens and rejects calls immediately, giving the dependency time to recover while returning a fast degraded response to callers.

```python
# pseudocode — circuit breaker around an HTTP call
breaker = CircuitBreaker(
    failure_threshold=0.5,   # open at 50% failure rate
    recovery_timeout=30,     # try half-open after 30 s
    expected_exception=RequestException,
)

@breaker
def call_payments_service(payload):
    return http.post("https://payments/charge", json=payload, timeout=2)

# call site
try:
    result = call_payments_service(payload)
except CircuitBreakerOpen:
    return degraded_response()   # fast path, no thread held
```

**Do:**
- Set distinct breakers per downstream; one slow dep shouldn't open the breaker on another.
- Define the degraded response before you wire the breaker — never silently swallow failures.
- Expose breaker state in an internal health/metrics endpoint so on-call can see which circuit is open.
- Pair with a timeout so the breaker window actually accumulates real failures, not hanging ones.

**Don't:**
- Use a single global breaker for all outbound calls — you lose fault isolation.
- Set a recovery timeout so short (under 5 s) that the breaker flaps open/half-open/open continuously.
- Let the circuit open silently; log and alert when state transitions to open.

## Edge cases / when the rule does NOT apply

Internal in-process calls (within the same service, same process) don't need a circuit breaker — only network or IPC hops that can hang. Very low-volume internal admin jobs where a held thread is acceptable may skip the breaker, but must have a hard timeout instead.

## See also

- [`../agents/backend-reliability-engineer.md`](../agents/backend-reliability-engineer.md) — owns the resilience patterns including circuit breakers, bulkheads, and retries.
- [`./timeout-and-bounded-retry.md`](./timeout-and-bounded-retry.md) — the required companion; a breaker without a timeout may not accumulate failures correctly.

## Provenance

Codifies the `backend-reliability-engineer` opinion from CLAUDE.md §2 rule 6: "Fail fast and degrade gracefully. … circuit breakers." Standard resilience engineering practice (Martin Fowler's Circuit Breaker pattern, Netflix Hystrix lineage).

---

_Last reviewed: 2026-06-05 by `claude`_
