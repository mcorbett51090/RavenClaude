# Optimistic concurrency with ETags and If-Match

**Status:** Pattern — strong default; last-write-wins is silent data loss.

**Domain:** API build / concurrency

**Applies to:** `api-engineering`

---

## Why this exists

Two clients read the same resource, both edit, both `PUT`. Without concurrency control, the second write silently overwrites the first — a lost update, with no error and no record. Optimistic concurrency uses an **`ETag`** (a version fingerprint) plus a conditional **`If-Match`** so a write only succeeds if the client is editing the version it last saw; a stale write gets `412 Precondition Failed` instead of clobbering.

## How to apply

Return an `ETag` on reads; require `If-Match` on updates; reject stale writes with `412`.

```http
GET /documents/42
200 OK
ETag: "v7"
{ "id": 42, "title": "Draft", ... }

PUT /documents/42
If-Match: "v7"
{ "title": "Final" }
  -> 200 OK, ETag: "v8"     (current version was v7 — applied)
  -> 412 Precondition Failed (current version is v9 — client is stale; re-read and retry)
```

**Do:**
- Use `If-None-Match: *` on create to prevent overwriting an existing resource; use `If-Match` on update/delete.
- Derive the ETag from a version column or content hash; return the new ETag on success.

**Don't:**
- Accept unconditional `PUT`/`PATCH` on contended resources; treat a missing `If-Match` as "force write" without a deliberate decision.

## Edge cases / when the rule does NOT apply

Single-writer resources, append-only logs, and idempotent full replaces with no concurrent editors don't need ETags. ETags also power HTTP caching (`If-None-Match` → `304 Not Modified`) — the same header, a different use. Pessimistic locking is the alternative when conflicts are frequent and retries expensive.

## See also

- [`./build-idempotency-keys-for-unsafe-retries.md`](./build-idempotency-keys-for-unsafe-retries.md)
- [`./build-use-http-status-codes-and-methods-correctly.md`](./build-use-http-status-codes-and-methods-correctly.md)
- [RFC 9110 §13 — Conditional Requests](https://www.rfc-editor.org/rfc/rfc9110.html#name-conditional-requests) — authoritative

## Provenance

Grounded in RFC 9110 conditional-request semantics (`ETag`/`If-Match`/`412`). Retrieved/verified 2026-06-04.

---

_Last reviewed: 2026-06-04 by `claude`_
