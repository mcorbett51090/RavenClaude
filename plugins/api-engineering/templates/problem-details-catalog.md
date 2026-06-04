# Problem Details catalog (RFC 9457) — `<API name>`

> Copy and fill in. This is the registry of stable `type` URIs your API returns in
> `application/problem+json` bodies. A `type` URI is a **contract identifier** — once
> published, its meaning never changes. Clients branch on `type`, humans read `title`/`detail`.
> See [`../best-practices/build-one-error-model-rfc9457-problem-details.md`](../best-practices/build-one-error-model-rfc9457-problem-details.md).

**Base URI for problem types:** `https://api.example.com/problems/`

| `type` (relative to base) | HTTP status | `title` | When it's returned | Extension members |
|---|---|---|---|---|
| `validation-error` | 422 | Your request body is invalid. | One or more fields failed semantic validation | `errors[]` (`pointer`, `detail`) |
| `unauthenticated` | 401 | Authentication is required. | Missing/invalid/expired token | — |
| `forbidden` | 403 | You may not perform this action. | Authenticated but not authorized (BFLA) | `requiredScope` |
| `not-found` | 404 | The requested resource was not found. | Resource missing, or hidden from an unauthorized caller (BOLA) | — |
| `conflict` | 409 | The request conflicts with the current state. | Duplicate, or an in-flight idempotent request | — |
| `precondition-failed` | 412 | The resource has changed since you last read it. | Stale `If-Match` (optimistic concurrency) | `currentEtag` |
| `idempotency-key-reused` | 422 | This idempotency key was used for a different request. | Same key, different request fingerprint | — |
| `rate-limited` | 429 | Rate limit exceeded. | Too many requests | `retryAfter` |
| `payload-too-large` | 413 | The request body is too large. | Body exceeds the size ceiling (API4) | `maxBytes` |
| `internal-error` | 500 | An unexpected error occurred. | Unhandled server error (NO stack trace in `detail`) | `traceId` |

## Example body

```http
HTTP/1.1 403 Forbidden
Content-Type: application/problem+json

{
  "type": "https://api.example.com/problems/forbidden",
  "title": "You may not perform this action.",
  "status": 403,
  "detail": "Scope 'orders:write' is required.",
  "instance": "/orders/9f2c",
  "requiredScope": "orders:write"
}
```

## Rules for maintaining this catalog

- **Never repurpose a `type`.** Add a new one instead — clients depend on the URI's meaning.
- **`status` in the body matches the HTTP status line.** They are redundant on purpose (proxies).
- **Never leak internals in `detail`** — no stack traces, SQL, internal hostnames. Use a `traceId` for correlation.
- **`type: "about:blank"`** is valid when the status code alone says everything (then `title` = the status phrase).
- Keep this catalog in the developer portal so consumers can code against the `type` set.
