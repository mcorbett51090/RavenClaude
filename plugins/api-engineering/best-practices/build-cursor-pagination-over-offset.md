# Cursor (keyset) pagination over offset/page

**Status:** Pattern — strong default; offset is a deep-paging bug for any large or live collection.

**Domain:** API build / collections

**Applies to:** `api-engineering`

---

## Why this exists

`offset`/`page` pagination has two failure modes that don't show up in dev: it **drifts** (a row inserted or deleted before your current offset shifts the window, so you skip or duplicate items across pages) and it **degrades** (`OFFSET 100000 LIMIT 20` makes the database scan and discard 100,000 rows). Cursor/keyset pagination — "give me the next 20 after this sort key" — is stable under concurrent writes and stays fast at any depth because it seeks rather than scans.

## How to apply

Return an opaque `next` cursor encoding the keyset position; bound the page size.

```http
GET /orders?limit=20
200 OK
{
  "data": [ ... 20 orders, sorted by (created_at, id) ... ],
  "next": "eyJjcmVhdGVkX2F0IjoiMjAyNi0wNi0wNFQxMDowMCIsImlkIjoiMTIzIn0"
}

GET /orders?limit=20&cursor=eyJjcmVhdGVkX2F0Ijoi...
# server decodes the cursor -> WHERE (created_at, id) > (:ca, :id) ORDER BY created_at, id LIMIT 20
```

**Do:**
- Sort by a stable, unique key (often `(timestamp, id)`); the cursor is opaque — clients pass it back verbatim.
- Cap `limit` server-side (e.g. max 100) regardless of what the client asks (OWASP API4).

**Don't:**
- Expose offsets/page numbers as the default; trust an unbounded client `limit`; let clients craft cursors by hand.

## Edge cases / when the rule does NOT apply

When clients genuinely need to jump to an arbitrary page number or need a total count on a small, slowly-changing set, offset is acceptable — bound the max offset and accept the drift. Cursor pagination can't easily provide "page 7 of 50"; if the UI requires that, that's the offset trade.

## See also

- [`../knowledge/api-design-decision-trees.md`](../knowledge/api-design-decision-trees.md) — pagination tree
- [`./secure-limit-resource-consumption.md`](./secure-limit-resource-consumption.md)
- [`../agents/api-implementation-engineer.md`](../agents/api-implementation-engineer.md)

## Provenance

Codifies house opinion #5 (CLAUDE.md §3), grounded in keyset-pagination practice. Retrieved/verified 2026-06-04.

---

_Last reviewed: 2026-06-04 by `claude`_
