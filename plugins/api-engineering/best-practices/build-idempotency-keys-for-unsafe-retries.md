# Idempotency keys for unsafe retries

**Status:** Absolute rule (for money/orders) — a non-idempotent POST with no idempotency design double-charges on retry.

**Domain:** API build / reliability

**Applies to:** `api-engineering`

---

## Why this exists

Networks retry. A client sends `POST /charges`, the response is lost to a timeout, the client retries — and without protection you've charged the card twice. `POST` is not idempotent by HTTP semantics, so you make *this* operation idempotent explicitly with an **`Idempotency-Key`**: the client sends a unique key, the server stores key → result, and a repeat of the same key replays the stored response instead of acting again. (The `Idempotency-Key` HTTP header is an **active IETF draft, not yet an RFC** — follow the draft; many APIs already ship this convention.)

## How to apply

Accept the key, store the outcome under it, replay on repeat, handle in-flight.

```http
POST /charges
Idempotency-Key: 8f1d...client-generated-uuid
{ "amount": 5000, "currency": "USD", "source": "card_x" }
```

```
On receipt of (idempotency-key, request-fingerprint):
  - key unseen      -> process; persist key -> {status, response, fingerprint}; return result
  - key seen, same fingerprint, completed -> return the STORED response (replay)
  - key seen, still in-flight             -> 409 Conflict (or 425) — "request in progress"
  - key seen, DIFFERENT fingerprint       -> 422 — key reused for a different request
Expire stored keys after a defined window (e.g. 24h).
```

**Do:**
- Scope keys per endpoint/account; fingerprint the request so a reused key with a different body is rejected.
- Document the dedup window; make `GET`/`PUT`/`DELETE` rely on their native idempotency instead.

**Don't:**
- Assume "the client won't retry"; store only the key without the response (you can't replay); keep keys forever.

## Edge cases / when the rule does NOT apply

Naturally-idempotent operations (`PUT` to a known URI, `DELETE`) don't need a key — their semantics already are. Read-only `GET`s never need one. The dedup window is a trade between safety and storage — pick it deliberately.

## See also

- [`./build-use-http-status-codes-and-methods-correctly.md`](./build-use-http-status-codes-and-methods-correctly.md)
- [`./build-optimistic-concurrency-with-etags.md`](./build-optimistic-concurrency-with-etags.md)
- [draft-ietf-httpapi-idempotency-key-header](https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/) — authoritative (IETF draft) `[verify-at-build]`

## Provenance

Codifies house opinion #6 (CLAUDE.md §3). The `Idempotency-Key` header is draft-ietf-httpapi-idempotency-key-header (~v07, 2025-10), not yet an RFC — web-verified 2026-06-04.

---

_Last reviewed: 2026-06-04 by `claude`_
