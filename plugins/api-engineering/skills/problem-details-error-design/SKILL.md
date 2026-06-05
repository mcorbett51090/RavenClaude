---
name: problem-details-error-design
description: "Playbook for designing a consistent RFC 9457 Problem Details error model — type URIs, extension members, status code mapping, and a catalog template. Prevents per-endpoint bespoke error shapes."
---

# Problem Details Error Design (RFC 9457)

## When to Use This Skill

Apply at design time — before a single error response is coded — and when auditing an existing API for inconsistent error shapes.

## 1. Problem Details Shape

```json
{
  "type": "https://api.example.com/problems/order-not-found",
  "title": "Order Not Found",
  "status": 404,
  "detail": "Order ord_9f3c1a was not found or has been deleted.",
  "instance": "/orders/ord_9f3c1a"
}
```

| Field | Required | Notes |
|---|---|---|
| `type` | Yes | A stable URI that never changes; resolves to human-readable docs |
| `title` | Yes | Short, human-readable, consistent for the same `type` |
| `status` | Yes | Must match the HTTP response status code |
| `detail` | No | Instance-specific, safe to show end-users; never a stack trace |
| `instance` | No | URI identifying the specific occurrence — good for log correlation |

**Media type:** `Content-Type: application/problem+json` (never `application/json` for errors).

## 2. Type URI Design Rules

1. Use a stable base URL your team controls: `https://api.example.com/problems/`
2. Use kebab-case slugs that name the condition, not the HTTP status: `order-not-found`, `insufficient-inventory`, `rate-limit-exceeded`
3. Never reuse a URI for two different conditions
4. The URI should resolve to documentation — consumers bookmark them

```
https://api.example.com/problems/order-not-found        ← correct
https://api.example.com/problems/404                    ← wrong (status not condition)
https://api.example.com/problems/OrderNotFoundException ← wrong (Java exception name leaked)
```

## 3. Status Code to Problem Type Mapping

| HTTP Status | Typical `type` slug | Notes |
|---|---|---|
| 400 | `invalid-input` | Validation failure; add `errors` extension (see below) |
| 401 | `unauthenticated` | Missing/expired/invalid token |
| 403 | `forbidden` | Valid token, insufficient permission (BOLA/BFLA) |
| 404 | `{resource}-not-found` | Include the resource type in the slug |
| 409 | `{resource}-conflict` | Duplicate, state conflict |
| 422 | `unprocessable-entity` | Semantically invalid (e.g. future date in past-only field) |
| 429 | `rate-limit-exceeded` | Add `Retry-After` header and extension members |
| 500 | `internal-error` | Never leak detail or stack trace |

## 4. Extension Members for Validation Errors

```json
{
  "type": "https://api.example.com/problems/invalid-input",
  "title": "Invalid Input",
  "status": 400,
  "detail": "The request body failed validation.",
  "errors": [
    { "pointer": "/quantity", "detail": "Must be a positive integer." },
    { "pointer": "/shippingAddress/zip", "detail": "Invalid ZIP code format." }
  ]
}
```

`pointer` follows JSON Pointer (RFC 6901). This avoids per-field response envelopes.

## 5. Problem Catalog Template

Maintain a `problems.yaml` alongside the OpenAPI spec:

| Type slug | Status | Title | When emitted | Extension members |
|---|---|---|---|---|
| `order-not-found` | 404 | Order Not Found | Order ID absent from store | — |
| `invalid-input` | 400 | Invalid Input | Schema/constraint violation | `errors[]` |
| `insufficient-inventory` | 409 | Insufficient Inventory | Stock check fails | `available`, `requested` |
| `rate-limit-exceeded` | 429 | Rate Limit Exceeded | Quota burst | `retryAfterSeconds` |

## 6. OpenAPI Schema Declaration

```yaml
components:
  schemas:
    Problem:
      type: object
      required: [type, title, status]
      properties:
        type:
          type: string
          format: uri
          example: "https://api.example.com/problems/order-not-found"
        title:
          type: string
        status:
          type: integer
        detail:
          type: string
        instance:
          type: string
          format: uri
      additionalProperties: true
```

## Pitfalls

- Returning a 200 with an `{"error": "..."}` body — consumers cannot branch on status code
- Leaking exception class names, stack traces, or internal IDs in `detail`
- Using a different `title` for the same `type` URI across responses — title must be stable per type
- Defining the error schema inline per operation instead of `$ref`-ing a shared component
- Using `application/json` instead of `application/problem+json` — clients lose the semantic signal

## See Also

- [`../../agents/api-implementation-engineer.md`](../../agents/api-implementation-engineer.md) — HTTP semantics and status code mapping
- [`../../agents/api-design-architect.md`](../../agents/api-design-architect.md) — contract-first design and OpenAPI authoring
- [`../../CLAUDE.md`](../../CLAUDE.md) — house opinion: one error model across all endpoints
