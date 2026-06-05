# Use UUIDs or ULIDs for distributed primary keys — avoid sequential integer hot spots

**Status:** Pattern
**Domain:** Schema design / performance
**Applies to:** `database-engineering`

---

## Why this exists

A sequential integer primary key (`SERIAL`, `BIGSERIAL`, `AUTO_INCREMENT`) inserts every new row at the rightmost leaf of the B-tree index, creating a write hot spot on that page. Under heavy insert load, this hot spot causes lock contention that limits write parallelism. On sharded or distributed databases, a sequential key also means all inserts route to the same shard. UUIDs (v4) distribute writes but sort randomly, degrading range scans. ULIDs and UUID v7 provide both distributed generation and time-ordered sortability — the correct default for new high-insert tables.

## How to apply

```sql
-- Bad: sequential BIGSERIAL hot-spots on write
CREATE TABLE events (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL,
  payload JSONB
);

-- Good: UUID v7 / ULID — time-ordered, globally unique, distributed-safe
-- Postgres 17+ has gen_random_uuid() v4; use an extension or app-layer for v7 [verify-at-build]
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),  -- or application-generated ULID stored as text/uuid
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  payload JSONB
);
```

In application code (Node.js example):
```typescript
import { ulid } from 'ulid';
const event = { id: ulid(), createdAt: new Date(), payload: data };
```

**Do:**
- Use UUID v7 or ULID for new tables that expect high insert volume or distributed generation.
- Store ULIDs as `CHAR(26)` or cast to UUID bytes for index efficiency.
- For internal admin/analytics tables with low insert volume, `BIGSERIAL` remains correct and is simpler.
- Create a `created_at` column alongside the UUID primary key for human-readable ordering.

**Don't:**
- Use UUID v4 as the primary key on a high-insert table without measuring the index fragmentation impact.
- Expose the UUID primary key in external APIs if it carries timing information from v7/ULID — consider a separate public token.
- Use sequential keys as a substitute for `created_at` to infer ordering — the sequence is implementation detail.

## Edge cases / when the rule does NOT apply

Low-volume tables (< 100k rows/day), lookup tables, and heavily-read/rarely-written tables work fine with sequential integers. Internal join tables (e.g., many-to-many) that are never directly queried by external callers also benefit from the simplicity of a composite primary key.

## See also

- [`../agents/schema-architect.md`](../agents/schema-architect.md) — owns schema design and key choices.
- [`../agents/query-performance-engineer.md`](../agents/query-performance-engineer.md) — owns index analysis; sequential hot spots appear as insert-lock waits in EXPLAIN.

## Provenance

B-tree hot-spot problem documented in PostgreSQL performance guides; ULID spec (github.com/ulid/spec); UUID v7 (RFC 9562). Codifies `schema-architect`'s key-design considerations.

---

_Last reviewed: 2026-06-05 by `claude`_
