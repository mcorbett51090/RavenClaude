---
name: error-handling-and-result-modeling
description: "Playbook for modeling and propagating errors in backend services — typed result/error envelopes, failure classification, HTTP status mapping, error translation at layer boundaries, and client-safe vs internal error separation. Prevents exception-driven spaghetti and accidental information leakage."
---

# Error Handling and Result Modeling

## 1. Classify Before You Handle

Every failure belongs to exactly one category. The category drives the handling strategy.

| Category | Meaning | Retry? | Expose to client? |
|---|---|---|---|
| **Validation** | Caller sent bad input | No | Yes — full detail |
| **Not found** | Requested resource absent | No | Yes — safe message |
| **Conflict** | State mismatch (optimistic lock, duplicate) | No | Yes — safe message |
| **Unauthorized / Forbidden** | Auth failure | No | Minimal detail |
| **Downstream** | Dependency failed or timed out | Yes (idempotent) | Opaque `service_unavailable` |
| **Bug / unexpected** | Unhandled code path | No | Opaque `internal_error` |

## 2. Typed Result Envelope (the Pattern)

Avoid throwing exceptions across use-case/service boundaries. Return a typed result:

```typescript
// TypeScript example — adapt to your language
type Ok<T> = { ok: true; value: T };
type Err<E> = { ok: false; error: E };
type Result<T, E> = Ok<T> | Err<E>;
```

```python
# Python example using dataclasses
@dataclass
class Ok(Generic[T]):
    value: T

@dataclass
class Err(Generic[E]):
    error: E

Result = Ok[T] | Err[E]
```

Rules:
1. Use-case methods return `Result<DomainValue, DomainError>` — never throw for expected failures.
2. Reserve exceptions for **truly unexpected** paths (bugs, unrecoverable state).
3. Domain errors are value objects that carry enough context for the handler to decide — not raw exception messages.

## 3. Layer Boundary Translation

```
HTTP handler
    └── Use-case / service  (returns Result<T, DomainError>)
            └── Repository / client  (returns Result<T, InfraError>)
```

**At each boundary, translate inward-facing errors to the layer's vocabulary:**

```
InfraError.DbConnectionFailed → DomainError.ServiceUnavailable
InfraError.UniqueConstraintViolated → DomainError.Conflict(entity, key)
```

The HTTP handler is the only layer that maps `DomainError` → HTTP status + JSON body.

## 4. HTTP Status Mapping Table

| DomainError category | HTTP status | When |
|---|---|---|
| Validation | 400 | Bad request body/params |
| Not found | 404 | Resource absent |
| Conflict | 409 | Duplicate / stale update |
| Unauthorized | 401 | Missing / invalid credential |
| Forbidden | 403 | Authenticated but not allowed |
| Downstream | 503 | Dependency unreachable |
| Bug / unexpected | 500 | Anything else |

## 5. Client-Safe Error Body

```json
{
  "error": {
    "code": "PAYMENT_METHOD_EXPIRED",
    "message": "The payment method has expired.",
    "details": [{ "field": "card.expiry", "issue": "past_expiry" }]
  }
}
```

**Rules:**
- `code` is a stable machine-readable slug — don't change it after release.
- `message` is English prose safe to display (no stack traces, no internal state).
- `details` is optional; present only for validation errors with field-level specifics.
- Never include stack traces, SQL errors, or internal service names in 4xx/5xx responses.

## 6. Logging Strategy

| Error category | Log level | What to include |
|---|---|---|
| Validation / not found | DEBUG or omit | High-volume, expected — log at trace if needed |
| Downstream (retried, eventually ok) | WARN | Attempt count, dependency name, duration |
| Downstream (exhausted) | ERROR | Full context, trace ID, retries attempted |
| Bug / unexpected | ERROR + alert | Stack trace, request ID, all context |

## Pitfalls

- Throwing exceptions for validation failures — forces callers into try/catch chains and hides intent.
- Returning `{ error: null, data: null }` — ambiguous; force the caller to pick a branch.
- Using HTTP 500 for validation errors — clients can't distinguish "your fault" from "our fault".
- Leaking `psycopg2.OperationalError: ...` or `ECONNREFUSED` in the response body — exposes topology.
- Re-throwing the same raw exception across layers — the HTTP handler ends up doing domain logic.
- Not logging the trace/correlation ID — makes cross-service debugging impossible.
