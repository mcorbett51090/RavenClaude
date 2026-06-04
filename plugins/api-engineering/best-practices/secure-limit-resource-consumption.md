# Limit resource consumption (OWASP API4)

**Status:** Absolute rule — every unbounded input is a DoS and a cost vector; the verdict escalates to security-reviewer.

**Domain:** API security / availability

**Applies to:** `api-engineering`

---

## Why this exists

**Unrestricted Resource Consumption** (OWASP API4:2023) is the API that lets a caller ask for too much: `?limit=10000000`, a 500MB request body, a GraphQL query nested 40 levels deep, or simply 100,000 requests a second. Each unbounded dimension is a denial-of-service vector and — on metered infrastructure or paid downstreams — a direct cost-amplification attack. Bounding consumption is both a reliability and a security control.

## How to apply

Put a ceiling on every dimension a caller can inflate.

```
Rate/quota:   per-key short-window rate limit + a longer-window quota; 429 + Retry-After on breach
Page size:    cap server-side (e.g. max 100) regardless of requested limit
Payload:      max request body bytes (reject 413 Payload Too Large)
Query cost:   GraphQL depth + complexity limits; reject over-budget queries
Fan-out:      cap batch sizes, $expand depth, included relations
Timeouts:     bound execution time per request; cap concurrent requests per client
```

**Do:**
- Advertise the rate limit via the `RateLimit`/`RateLimit-Policy` headers (IETF draft) so clients self-throttle.
- Rate-limit by the most specific stable subject (key > user > IP).
- Apply GraphQL complexity/depth limits as a hard gate — GraphQL has no implicit ceiling.

**Don't:**
- Trust a client-supplied page size or batch size; allow unbounded request bodies; ship GraphQL with no cost limit.

## Edge cases / when the rule does NOT apply

Trusted internal service-to-service traffic may have higher (but still finite) ceilings. Bulk/import endpoints legitimately accept large payloads — bound them explicitly and stream rather than buffer. Limits are a tiering lever too (see the rate-limit/quota tree and the platform engineer).

## See also

- [`./build-cursor-pagination-over-offset.md`](./build-cursor-pagination-over-offset.md)
- [`./operate-rate-limit-and-advertise-it.md`](./operate-rate-limit-and-advertise-it.md)
- [OWASP API4:2023 — Unrestricted Resource Consumption](https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/) — authoritative

## Provenance

Codifies house opinion #9 (CLAUDE.md §3) and OWASP API4:2023. Web-verified 2026-06-04. **Verdict escalates to `ravenclaude-core/security-reviewer`.**

---

_Last reviewed: 2026-06-04 by `claude`_
