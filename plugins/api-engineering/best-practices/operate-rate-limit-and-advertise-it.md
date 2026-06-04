# Rate-limit at the edge, and advertise it

**Status:** Pattern — a rate limit you don't advertise is a surprise 429; one you don't enforce is a cost leak.

**Domain:** API operations / availability

**Applies to:** `api-engineering`

---

## Why this exists

Rate limiting is both a cost/availability control and a security control (OWASP API4). But a limit clients can't *see* just produces mysterious `429`s and retry storms. The `RateLimit` and `RateLimit-Policy` response header fields (an **active IETF draft**, not yet an RFC) let the server advertise the quota and remaining budget so well-behaved clients self-throttle before they're cut off — turning enforcement into cooperation.

## How to apply

Enforce per the most specific subject; advertise with the headers; return `429` + `Retry-After` on breach.

```http
GET /orders
200 OK
RateLimit: limit=100, remaining=42, reset=30        # draft field — current budget
RateLimit-Policy: 100;w=60                           # 100 requests per 60s window

# on breach:
429 Too Many Requests
Retry-After: 30
Content-Type: application/problem+json
{ "type": ".../problems/rate-limited", "title": "Rate limit exceeded", "status": 429 }
```

**Do:**
- Limit by key > user > IP (most specific stable subject); pair a short-window rate with a longer-window quota tier.
- Emit the `RateLimit` headers and a Problem Details body on `429`; express the policy independent of the gateway product.

**Don't:**
- Throttle silently with a bare `429`; rate-limit by IP when you have an authenticated key; hard-code the policy to one gateway.

## Edge cases / when the rule does NOT apply

Internal trusted traffic may run at higher ceilings. The `RateLimit` header field names are draft and have evolved across draft versions (`[verify-at-build]`) — implement to the current draft and note it; some teams still ship the older `X-RateLimit-*` de-facto headers for client compatibility.

## See also

- [`./secure-limit-resource-consumption.md`](./secure-limit-resource-consumption.md)
- [`../knowledge/api-security-decision-trees.md`](../knowledge/api-security-decision-trees.md) — rate-limit/quota tree
- [draft-ietf-httpapi-ratelimit-headers](https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/) — authoritative (IETF draft) `[verify-at-build]`

## Provenance

Pairs OWASP API4 with the IETF `RateLimit` headers draft (draft-ietf-httpapi-ratelimit-headers, ~v11, 2026 — not yet an RFC). Web-verified 2026-06-04.

---

_Last reviewed: 2026-06-04 by `claude`_
