# Use HTTP status codes and methods correctly

**Status:** Absolute rule — the status line is part of the contract; a 200 with an error inside lies to every client library.

**Domain:** API build / HTTP semantics

**Applies to:** `api-engineering`

---

## Why this exists

HTTP status codes and methods are a shared vocabulary every client library, proxy, cache, and monitoring tool understands. Returning `200 OK` with `{"success": false}` defeats all of it — error-rate dashboards read green, retries don't trigger, clients can't branch on the status. Using `GET` for a mutation breaks caching and idempotency assumptions. Correct semantics are free reliability.

## How to apply

Map outcomes to the right code and method.

```
Methods:  GET/HEAD safe (no mutation)   PUT/DELETE idempotent   POST not idempotent   PATCH partial update

Success:  200 OK            general success with body
          201 Created       + Location header on resource creation
          202 Accepted      async accepted, not yet done (see 202+polling)
          204 No Content    success, no body (e.g. DELETE)

Client:   400 Bad Request   malformed syntax
          401 Unauthorized  no/invalid authentication
          403 Forbidden     authenticated but not allowed (authorization)
          404 Not Found      (or 404 to hide existence from unauthorized callers)
          409 Conflict       state conflict (e.g. duplicate, in-flight idempotency)
          412 Precondition Failed   stale If-Match
          422 Unprocessable Content semantic validation failure
          429 Too Many Requests     throttled (+ Retry-After)

Server:   500 Internal      unexpected (no stack trace in body)
          503 Service Unavailable   overloaded/down (+ Retry-After)
```

**Do:**
- Pair the status with a Problem Details body on errors; send `Location` on `201`, `Retry-After` on `429`/`503`.
- Use `403` vs `401` deliberately (authn vs authz); `422` vs `400` (semantic vs syntactic).

**Don't:**
- Return `200` for failures; use `GET` to mutate; invent non-standard codes.

## Edge cases / when the rule does NOT apply

Some teams deliberately return `404` instead of `403` to avoid confirming a resource exists to an unauthorized caller — a legitimate security trade. GraphQL returns `200` with an errors array by spec. `200` vs `201` vs `204` on create/update has minor legitimate variation — pick one and be consistent.

## See also

- [`./build-one-error-model-rfc9457-problem-details.md`](./build-one-error-model-rfc9457-problem-details.md)
- [`./design-model-resources-not-rpc-verbs.md`](./design-model-resources-not-rpc-verbs.md)
- [RFC 9110 — HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html) — authoritative

## Provenance

Grounded in RFC 9110 status-code and method semantics. Retrieved/verified 2026-06-04.

---

_Last reviewed: 2026-06-04 by `claude`_
