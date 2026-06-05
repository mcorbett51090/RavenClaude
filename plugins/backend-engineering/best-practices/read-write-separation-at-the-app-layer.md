# Separate reads from writes at the application layer

**Status:** Pattern
**Domain:** Data access / performance
**Applies to:** `backend-engineering`

---

## Why this exists

Command (write) and query (read) paths have different performance profiles, consistency requirements, and scaling strategies. When the same code path is used for both, an optimization for reads (denormalized projections, eventual consistency) conflicts with an optimization for writes (normalized tables, strong consistency). Separating the paths — at minimum at the repository/service level, and optionally into separate read models — lets each evolve independently and makes it straightforward to route reads to a replica without touching the write path.

## How to apply

At minimum: split your repository methods into a clearly labeled read side and write side. Route read methods to the replica connection pool; route write methods to the primary.

```typescript
class OrderRepository {
  constructor(
    private readonly primary: DbPool,    // writes
    private readonly replica: DbPool     // reads (replica lag is acceptable)
  ) {}

  // Write side — primary only
  async save(order: Order): Promise<void> {
    await this.primary.query('INSERT INTO orders ...', order.toRow());
  }

  // Read side — replica, possibly a denormalized projection
  async findByCustomer(customerId: string): Promise<OrderSummary[]> {
    return this.replica.query('SELECT ... FROM order_summaries WHERE customer_id = $1', [customerId]);
  }
}
```

**Do:**
- Mark replica reads explicitly so future engineers can see the consistency tradeoff at the call site.
- Accept that replica reads may lag slightly — validate that each read use-case tolerates seconds of lag.
- Use the same split in cache-aside: writes invalidate the cache; reads can serve from cache first.
- For high-read services, build a denormalized read model (materialized view, event-sourced projection) that is populated by writes via a domain event.

**Don't:**
- Route writes to the replica — replica connections are read-only by design; this will fail.
- Route after-write confirmation reads to the replica — these need the primary or a quorum read.
- Conflate read/write separation with full CQRS — separate methods on one repository is the minimal form; a full event-sourced read model is an advanced extension.

## Edge cases / when the rule does NOT apply

A single-node database with no replica needs no routing split. Services where every read is a confirmation of a just-issued write (e.g., a checkout confirmation page) should read from the primary to avoid replica lag surprises.

## See also

- [`../agents/backend-data-access-engineer.md`](../agents/backend-data-access-engineer.md) — owns the data-access layer and replica routing.
- [`./own-the-data-access-layer.md`](./own-the-data-access-layer.md) — the broader rule about owning queries behind a repository; this rule adds the read/write dimension.

## Provenance

CQRS (Greg Young) and read/write splitting are standard data-access patterns. Codifies the `backend-data-access-engineer`'s responsibility for explicit consistency contracts at the data-access layer.

---

_Last reviewed: 2026-06-05 by `claude`_
