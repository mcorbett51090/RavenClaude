---
name: idempotency-key-design
description: "Playbook for designing safe-to-retry POST and PATCH operations using Idempotency-Key — covers key format, dedup window, stored-response replay, conflict handling, and OpenAPI declaration."
---

# Idempotency-Key Design

## When to Use This Skill

Any `POST` or `PATCH` that has a side effect the caller must not repeat: charge a card, create an order, send a notification, initiate a transfer. If the client retries on a network timeout, the operation must not execute twice.

## 1. The Contract

```
POST /orders
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json

{ "items": [...], "total": 99.95 }
```

- The header name is `Idempotency-Key` (title-case, per the IETF draft — `[verify-at-build]` on draft status).
- Value: a **client-generated** UUID v4 (or ULID). The server treats it as opaque.
- The server stores the key + response for the dedup window; re-submitting the same key returns the stored response without re-executing.

## 2. Server-Side Design Checklist

| Step | Detail |
|---|---|
| Parse and validate | If header absent on a non-idempotent-by-design endpoint → 422 or proceed without dedup (document which). If header present but malformed → 400. |
| Lock the key | Atomically: check-and-set the key in a store (Redis SETNX, DB upsert). If key already locked and processing → 409 `in-progress`. |
| Execute or replay | Key absent → execute normally, store `(key, status, response_body, expires_at)`. Key present + complete → return stored response with original status. |
| Dedup window | Minimum 24 hours, typically 7 days. Beyond the window, treat as a new request. Document the TTL. |
| Scope | Key is scoped to the **authenticated caller** + **endpoint**. The same key from a different user is a different request. |

## 3. Storage Schema (minimal)

```sql
CREATE TABLE idempotency_keys (
  key         TEXT        NOT NULL,
  user_id     UUID        NOT NULL,
  endpoint    TEXT        NOT NULL,
  status      SMALLINT    NOT NULL,
  response    JSONB       NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at  TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (key, user_id, endpoint)
);
```

## 4. Response Behaviour Table

| Scenario | Status returned | Notes |
|---|---|---|
| First request, succeeds | 201 or 200 | Store response |
| Retry with same key, completed | Same as first (201/200) | Return stored body |
| Retry with same key, still processing | 409 `in-progress` | `Retry-After` header |
| Key expired, resubmitted | Treat as new request | Document TTL |
| Wrong user submitting same key | Normal processing (different scope) | Keys are user-scoped |
| Key reused for different payload | 422 `idempotency-key-reuse` | Detect via payload hash if desired |

## 5. OpenAPI Declaration

```yaml
/orders:
  post:
    operationId: createOrder
    parameters:
      - name: Idempotency-Key
        in: header
        required: true
        schema:
          type: string
          format: uuid
        description: |
          Client-generated UUID v4. Safe to retry within 7 days.
          Re-submitting the same key returns the stored response.
    responses:
      "201":
        description: Order created
      "409":
        description: Key in progress or payload mismatch
        content:
          application/problem+json:
            schema:
              $ref: "#/components/schemas/Problem"
```

## 6. Client Retry Algorithm

```
1. Generate key = UUID v4; store locally.
2. POST with Idempotency-Key header.
3. On network error or 5xx: wait (exponential backoff + jitter), retry with SAME key.
4. On 409 in-progress: wait Retry-After seconds, retry with SAME key.
5. On 2xx: success.
6. On 4xx (not 409): do NOT retry — fix the request.
```

## Pitfalls

- Using a server-generated key instead of a client-generated one — the client can't retry if the first response never arrived
- Setting a dedup window under 24 hours — not sufficient for mobile clients on spotty networks
- Scoping the key globally (not per-user) — one user can accidentally collide with another
- Not storing the full response body — on replay the server must return identical status + body, not regenerate
- Making `GET` idempotent with this mechanism — `GET` is already safe; only unsafe methods need it

## See Also

- [`../../agents/api-implementation-engineer.md`](../../agents/api-implementation-engineer.md) — HTTP semantics and unsafe-retry patterns
- [`../../agents/api-security-engineer.md`](../../agents/api-security-engineer.md) — resource-consumption limits (API4)
- [`../../CLAUDE.md`](../../CLAUDE.md) — house opinion: unsafe retries need an Idempotency-Key
