# One error model — RFC 9457 Problem Details

**Status:** Absolute rule — a bespoke per-endpoint error shape is a defect; use `application/problem+json`.

**Domain:** API build / errors

**Applies to:** `api-engineering`

---

## Why this exists

When every endpoint invents its own error shape (`{"error": "..."}`, `{"message": ...}`, `{"code": 5, "errors": [...]}`), consumers write bespoke error handling per endpoint and break when it changes. **RFC 9457 — Problem Details for HTTP APIs** (which **obsoletes RFC 7807**, same wire format) is the standard, machine-readable error format: a stable `type` URI clients can branch on, a human `title`/`detail`, and extension members for specifics. One model, every endpoint, no stack traces leaked.

## How to apply

Return `application/problem+json` with stable `type` URIs from a catalog; map validation errors to it.

```http
HTTP/1.1 422 Unprocessable Content
Content-Type: application/problem+json

{
  "type": "https://api.example.com/problems/validation-error",
  "title": "Your request body is invalid.",
  "status": 422,
  "detail": "2 fields failed validation.",
  "instance": "/orders",
  "errors": [
    { "pointer": "/items/0/quantity", "detail": "must be >= 1" },
    { "pointer": "/currency",         "detail": "unsupported value 'XYZ'" }
  ]
}
```

**Do:**
- Keep a catalog of `type` URIs (see [`../templates/problem-details-catalog.md`](../templates/problem-details-catalog.md)); they're stable identifiers, not docs links that move.
- Set the `status` member to match the HTTP status; add typed extension members (`errors`, `balance`, `retryAfter`).

**Don't:**
- Return `200` with an error body; leak a stack trace or internal exception text in `detail`.
- Change a `type` URI's meaning once published (it's a contract).

## Edge cases / when the rule does NOT apply

GraphQL has its own errors array (in a `200`) by spec — Problem Details is for HTTP/REST. gRPC uses status codes + `google.rpc.Status`. For those, use the paradigm's native error model consistently. A `type` of `"about:blank"` is valid when the status code alone is the whole story.

## See also

- [`../templates/problem-details-catalog.md`](../templates/problem-details-catalog.md)
- [`./build-use-http-status-codes-and-methods-correctly.md`](./build-use-http-status-codes-and-methods-correctly.md)
- [RFC 9457 — Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc9457.html) — authoritative (obsoletes RFC 7807)

## Provenance

Codifies house opinion #4 (CLAUDE.md §3). RFC 9457 published 2023-07, obsoletes RFC 7807 — web-verified 2026-06-04.

---

_Last reviewed: 2026-06-04 by `claude`_
