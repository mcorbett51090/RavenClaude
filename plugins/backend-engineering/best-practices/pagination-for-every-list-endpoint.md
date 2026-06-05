# Paginate every list endpoint — never return an unbounded result set

**Status:** Absolute rule
**Domain:** API implementation / resource protection
**Applies to:** `backend-engineering`

---

## Why this exists

A list endpoint that returns every row grows with the data. What returns 10 rows in development returns 100,000 in production, serializes the entire table into memory, serializes it again into JSON, and sends it over the wire — all in one request. This crashes your service under large data sets and turns a well-intentioned query into a DoS vector. Pagination is not a feature you add later; it is a correctness requirement.

## How to apply

Use cursor (keyset) pagination by default. Reserve offset pagination for small, stable, admin-facing lists.

```typescript
// Cursor-based: stable under concurrent inserts/deletes
async function listOrders(afterCursor?: string, limit = 50): Promise<Page<Order>> {
  const decodedCursor = afterCursor ? decodeCursor(afterCursor) : null;

  const rows = await db.query<Order>(
    `SELECT * FROM orders
     WHERE ($1::uuid IS NULL OR id > $1::uuid)
     ORDER BY id ASC
     LIMIT $2`,
    [decodedCursor, Math.min(limit, 200)]  // cap the max page size
  );

  return {
    items: rows,
    nextCursor: rows.length === limit ? encodeCursor(rows[rows.length - 1].id) : null,
  };
}
```

**Do:**
- Cap the maximum page size server-side (e.g., 200) regardless of what the caller requests.
- Return a `nextCursor` (or `null` when exhausted) so clients can iterate without guessing.
- Apply the limit *before* any join or aggregation that would expand the row count.
- Use cursor pagination for live, append-only collections; offset only for small admin lists where page-N access is needed.

**Don't:**
- Return all rows if no limit parameter is supplied — default to a sensible page size (e.g., 50).
- Trust the caller's `limit` value without capping it.
- Use `SELECT *` plus application-layer pagination (filter rows in memory) — the database still fetches all rows.

## Edge cases / when the rule does NOT apply

Small, definitionally bounded result sets (e.g., the five steps of a workflow, the two linked accounts of a user) where the maximum row count is provably small and fixed may return all rows in a single response. Document that bound explicitly.

## See also

- [`../agents/backend-data-access-engineer.md`](../agents/backend-data-access-engineer.md) — owns query design and data-access patterns.
- [`./rate-limit-all-inbound-surfaces.md`](./rate-limit-all-inbound-surfaces.md) — rate limiting and pagination are complementary resource-consumption controls.

## Provenance

Standard web API best practice (also enforced by `api-engineering` for the contract side). Codifies `backend-data-access-engineer`'s data-access responsibility: no unbounded queries leave the data layer.

---

_Last reviewed: 2026-06-05 by `claude`_
