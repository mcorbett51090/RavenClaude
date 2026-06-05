# Index foreign key columns on the referencing side

**Status:** Absolute rule
**Domain:** Schema design / query performance
**Applies to:** `database-engineering`

---

## Why this exists

PostgreSQL (and most databases) automatically create an index on the referenced column (the PK side of a FK). They do not create an index on the referencing column (the FK side). Every `DELETE` on the parent table causes PostgreSQL to check all child rows for the FK — and without an index on the child column, this requires a full sequential scan of the child table. On a large child table, deleting a single parent row can take minutes and hold locks that cascade through dependent queries.

## How to apply

```sql
-- Bad: FK column without an index
CREATE TABLE order_items (
  id BIGSERIAL PRIMARY KEY,
  order_id BIGINT NOT NULL REFERENCES orders(id),  -- no index on order_id
  product_id BIGINT NOT NULL REFERENCES products(id),
  quantity INT NOT NULL
);

-- Good: index every FK referencing column
CREATE TABLE order_items (
  id BIGSERIAL PRIMARY KEY,
  order_id BIGINT NOT NULL REFERENCES orders(id),
  product_id BIGINT NOT NULL REFERENCES products(id),
  quantity INT NOT NULL
);

CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
-- These also speed up: JOIN order_items ON orders.id = order_items.order_id
```

**Do:**
- Add a B-tree index on every FK referencing column as a default convention.
- Script a check that flags FK columns without a corresponding index in CI or schema review.
- Verify the indexes are actually used in EXPLAIN output for your typical JOIN and DELETE queries.

**Don't:**
- Assume the database creates both sides of the FK index automatically — it only creates the PK side.
- Skip the index on "small tables" — a 100k-row order_items table joined to users without an index already produces slow deletes.
- Create redundant indexes where the FK column is already the leftmost column of a composite index.

## Edge cases / when the rule does NOT apply

A many-to-many join table where the composite primary key is `(left_id, right_id)` already has an index on `left_id` (the leftmost column). You still need a separate index on `right_id` alone unless queries always include `left_id` in the predicate.

## See also

- [`../agents/schema-architect.md`](../agents/schema-architect.md) — owns FK and constraint design.
- [`../agents/query-performance-engineer.md`](../agents/query-performance-engineer.md) — will surface missing FK indexes as sequential scans in EXPLAIN plans.

## Provenance

PostgreSQL documentation on foreign keys and indexing. Standard schema best practice; commonly overlooked during schema authoring. Codifies `schema-architect`'s constraint and index conventions.

---

_Last reviewed: 2026-06-05 by `claude`_
