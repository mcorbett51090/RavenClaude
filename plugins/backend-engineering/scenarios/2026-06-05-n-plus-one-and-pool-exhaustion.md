---
scenario_id: 2026-06-05-n-plus-one-and-pool-exhaustion
contributed_at: 2026-06-05
plugin: backend-engineering
product: postgres
product_version: "unknown"
scope: likely-general
tags: [n-plus-1, orm, connection-pool, latency, eager-load, transaction]
confidence: high
reviewed: false
---

## Problem

A list endpoint that rendered ~50 orders with their line items got slow under load and then started returning `connection pool timeout` errors. p99 latency went from 120 ms to 9 s, and the app logged `QueuePool limit ... connection timed out` while the database's own CPU sat near idle. Two distinct bugs wearing one costume: an N+1 query pattern **and** a connection pool that the N+1 was draining.

## Constraints context

- ORM-backed data access (the pattern is the same across SQLAlchemy / ActiveRecord / Hibernate / Prisma / Entity Framework).
- A modest connection pool (size 10, overflow 10) sized for the *expected* per-request query count, not the actual one.
- The serializer lazily accessed `order.line_items` while rendering each row, so the relationship loaded on access — inside the request, one query per order.
- The pool checkout was held for the whole request because the ORM session/transaction wrapped the entire handler.

## Attempts

- Tried: bumping the pool size from 10 to 50. Bought time, then failed louder — more concurrent N+1 storms, the DB now actually felt it, and the timeouts moved from the app to the DB. Raising the pool to hide an N+1 just moves the bottleneck.
- Tried: caching the rendered list. Hid the latency for cache hits but did nothing for cache misses or writes, and added an invalidation problem. Wrong layer for the fix.
- Tried: eager-loading the relationship (`JOIN`/`IN`-batch the children in one or two queries) so the 1+50 collapsed to 1+1. Latency dropped back under 150 ms and the pool stopped saturating. This is the fix.
- Tried (follow-up): shortening the transaction/session scope so a connection is checked out only for the query, not for the JSON serialization and the network write. Pool checkouts dropped further.

## Resolution

**Diagnose the N+1 first, then right-size the pool — never the reverse.** The order matters:

1. **Find the N+1.** Turn on query logging (or the ORM's echo) for one request and count queries. 1 parent query + N child queries that scales with row count is the signature. APM/trace waterfalls show the same as a staircase of identical short queries.
2. **Eager-load deliberately.** Use the ORM's batch/join load (`selectinload`/`joinedload`, `includes`, `JOIN FETCH`, Prisma `include`) so related rows load in one or two queries. Prefer an `IN`-batch (`selectinload`-style) over a giant `JOIN` when the children fan out, to avoid row multiplication.
3. **Then look at the pool.** A correctly-batched endpoint needs *far* fewer connections. Size the pool to `concurrent_requests × queries_held_concurrently`, not to the number of queries a buggy handler emits. A pool exhaustion is usually a symptom of a query bug or a too-long checkout, not a too-small pool.
4. **Keep transactions short and off the network** (this team's house rule). Don't hold a pooled connection across serialization, external calls, or user I/O. Open it late, commit early, release it back.

The trap is that the pool error is the *loud* symptom and the N+1 is the *quiet* cause, so the instinct is to raise the pool. That treats the alarm, not the fire — and a bigger pool lets the N+1 hit the database harder.

**Action for the next engineer:** when you see pool-timeout errors with a calm database, count the queries per request before touching the pool config. The fix is almost always "stop emitting N queries," not "allow N more connections."

Cross-reference: this is the field-note complement to [`../best-practices/own-the-data-access-layer.md`](../best-practices/own-the-data-access-layer.md) and [`../best-practices/keep-transactions-short-and-off-the-network.md`](../best-practices/keep-transactions-short-and-off-the-network.md). The schema/index/query-plan side belongs to `database-engineering`; the data-access *code* (eager-load, transaction scope, pool config) is this team's lane.
