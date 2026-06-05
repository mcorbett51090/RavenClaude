# Use stable, dereferenceable type URIs in Problem Details responses

**Status:** Absolute rule
**Domain:** API build craft / error model
**Applies to:** `api-engineering`

---

## Why this exists

RFC 9457 Problem Details requires a `type` URI that identifies the error category. Many teams comply by putting a random UUID, a generic `about:blank`, or a changing string in the `type` field — defeating its entire purpose. The `type` URI is a stable identifier that: (1) lets clients branch on error category programmatically, (2) should dereference to human-readable documentation, and (3) must not change once it is published (because clients hard-code comparisons to it). A `type` URI that changes breaks every client that checks it.

## How to apply

```json
// Bad — generic or unstable type
{
  "type": "about:blank",
  "title": "Validation Error",
  "status": 422
}

// Also bad — changing UUID
{
  "type": "urn:error:3f7a91b2-...",
  "title": "Not Found"
}

// Good — stable, dereferenceable, categorized URI
{
  "type": "https://api.example.com/errors/validation-failed",
  "title": "Validation Failed",
  "status": 422,
  "detail": "The 'email' field must be a valid email address.",
  "instance": "/users/create#email",
  "errors": [
    { "field": "email", "message": "Invalid email format" }
  ]
}
```

Rules for `type` URIs:
1. Use your API's domain: `https://api.example.com/errors/<slug>`.
2. The slug is a stable, kebab-case error category name, not a message.
3. The URI should dereference (a `GET` to it returns documentation in any format).
4. Document every `type` URI in your OpenAPI spec's `responses` section.

**Do:**
- Maintain a catalog of `type` URIs in a versioned document (your developer portal or a spec file).
- Return the same `type` URI for the same category of error, regardless of where in the codebase it originates.
- Use `instance` to point to the specific request or resource where the error occurred.

**Don't:**
- Change a published `type` URI — clients depend on exact-string matches.
- Use `about:blank` except when there is truly no better category (and even then, add `title`).
- Use HTTP status codes as the `type` URI (e.g., `https://httpstatuses.io/422`) — that's not a category, it's a code.

## Edge cases / when the rule does NOT apply

Internal-only APIs with a single known consumer may use a simpler enumeration if the consumer is co-owned and both sides agree. The requirement applies wherever the client is not co-owned.

## See also

- [`../agents/api-implementation-engineer.md`](../agents/api-implementation-engineer.md) — owns the error model and RFC 9457 implementation.
- [`./build-one-error-model-rfc9457-problem-details.md`](./build-one-error-model-rfc9457-problem-details.md) — the foundational rule this extends with the URI stability requirement.

## Provenance

RFC 9457 §4.2.1 ("The type Member"), the Problem Details registry guidance. Codifies `api-implementation-engineer`'s error-model discipline.

---

_Last reviewed: 2026-06-05 by `claude`_
