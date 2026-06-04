# Long-running operations: 202 + polling (or a callback)

**Status:** Pattern — a multi-second synchronous request is a timeout you haven't hit yet.

**Domain:** API build / async operations

**Applies to:** `api-engineering`

---

## Why this exists

Holding an HTTP request open while a 30-second (or 5-minute) job runs ties up server threads, hits client/proxy/gateway timeouts, and gives the client no way to recover if the connection drops mid-job. The async pattern accepts the work with `202 Accepted`, hands back an **operation resource** the client polls for status, and returns the result (or a link to it) when done — or pushes a webhook callback when the job finishes.

## How to apply

Accept with `202`, expose a status resource, poll to completion.

```http
POST /reports            { "type": "annual", ... }
202 Accepted
Location: /operations/9f2c
{ "id": "9f2c", "status": "pending" }

GET /operations/9f2c
200 OK
{ "id": "9f2c", "status": "running", "progress": 0.4 }
# ... later ...
{ "id": "9f2c", "status": "succeeded", "result": { "href": "/reports/551" } }
# or
{ "id": "9f2c", "status": "failed", "error": { /* Problem Details */ } }
```

**Do:**
- Model the operation as a real resource with `status` (pending/running/succeeded/failed), and a `Retry-After` hint on the poll.
- Offer a webhook callback as an alternative to polling for clients that can receive one.

**Don't:**
- Block the request for the whole job; return `200` before the work is actually done; make the client guess the poll interval.

## Edge cases / when the rule does NOT apply

Sub-second work stays synchronous — don't add an operation resource for a fast call. For streaming/incremental results, SSE or chunked responses (first-class in OpenAPI 3.2) may fit better than poll. gRPC has server-streaming for progressive results.

## See also

- [`./build-use-http-status-codes-and-methods-correctly.md`](./build-use-http-status-codes-and-methods-correctly.md)
- [`./build-one-error-model-rfc9457-problem-details.md`](./build-one-error-model-rfc9457-problem-details.md)
- [`../agents/api-implementation-engineer.md`](../agents/api-implementation-engineer.md)

## Provenance

Grounded in the long-running-operation / `202 Accepted` pattern common across mature APIs (Azure, Stripe, GitHub). Retrieved/verified 2026-06-04.

---

_Last reviewed: 2026-06-04 by `claude`_
