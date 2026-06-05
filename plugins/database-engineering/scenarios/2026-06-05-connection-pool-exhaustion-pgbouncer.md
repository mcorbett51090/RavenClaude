---
scenario_id: 2026-06-05-connection-pool-exhaustion-pgbouncer
contributed_at: 2026-06-05
plugin: database-engineering
product: pgbouncer
product_version: "1.21"
scope: likely-general
tags: [connection-pool, pgbouncer, max-connections, pool-mode, saturation]
confidence: high
reviewed: false
---

## Problem

A platform with ~30 application pods started throwing `FATAL: sorry, too many clients already` from Postgres and `pool timeout` from the app during traffic peaks. Each pod ran its own app-level pool of 20 connections directly to Postgres, so 30 × 20 = 600 connections aimed at a database whose `max_connections` was 200. The database wasn't slow — its CPU was moderate — but it was *out of connection slots*, and each connection it did hold cost ~5–10 MB of server RAM plus scheduler overhead. Raising `max_connections` to 1000 "fixed" it for a day, then made it worse: now 600+ active backends thrashed the 8-vCPU instance and every query slowed.

## Constraints context

- 30 pods, each with a fat app-side pool, talking **directly** to Postgres (no pooler in between).
- Postgres `max_connections = 200` on an 8-vCPU managed instance; raising it consumes RAM and adds context-switch overhead per backend.
- Workload is short web transactions — each request holds a connection for milliseconds, but the pool kept them checked out.
- Some endpoints used `SET search_path` and a few used session-level prepared statements.

## Attempts

- Tried: raising Postgres `max_connections` from 200 → 1000. Bought a day, then degraded *everything* — backend connections far exceed `(vCPU × 2 + disks)`, so the box spent its time context-switching instead of running queries. More connections than the CPU can serve is negative-yield.
- Tried: shrinking each pod's app pool from 20 → 7 (30 × 7 = 210, still over 200). Reduced the error rate but starved pods under burst and was a fragile manual balance that broke the moment the pod count changed (autoscaling did exactly that).
- Tried: putting **PgBouncer in transaction-pooling mode** between the app and Postgres. The app pools now connect to PgBouncer (cheap), and PgBouncer multiplexes them onto a small `default_pool_size` of real backends. 600 client connections → ~40 backend connections. Errors gone, DB RAM/CPU calm. This is the fix.

## Resolution

**Size the pool to the *database's* capacity, not the *app's* instance count — and put a transaction-mode pooler in front so app scale-out doesn't translate 1:1 into backend connections.** What worked:

1. **Introduce PgBouncer in `pool_mode = transaction`.** A connection is returned to the pool at *transaction end*, so thousands of short web transactions share a small set of backend connections. This is the right mode for short-transaction web apps; session mode gives no multiplexing benefit and statement mode breaks multi-statement transactions.
2. **Size `default_pool_size` to the database, not the fleet.** Backend connections rarely benefit beyond `(DB vCPU × 2) + spindles` — for an 8-vCPU box, ~20–40 backends, not 600. Set `max_client_conn` high (the cheap side) and `default_pool_size` to the small backend number.
3. **Resolve transaction-mode incompatibilities.** `SET search_path` is per-session and is lost at transaction end under transaction pooling — move it into the connection string / `options`. Disable server-side prepared statements in the driver (or use protocol-level prepared-statement support where PgBouncer supports it). `[verify-at-use]` — PgBouncer's prepared-statement handling has improved across versions; confirm against the deployed PgBouncer version.
4. **Guard `idle in transaction`.** Set `idle_in_transaction_session_timeout` so a leaked open transaction can't pin a backend connection (and hold locks) indefinitely.

The trap is reading `too many clients` as "the database needs more connections." It almost never does — it needs **fewer, multiplexed** ones. The connection count is an app-architecture symptom (N pods × a fat pool, no pooler), and the cure is a pooler plus right-sizing to DB capacity, not a bigger `max_connections`.

**Action for the next engineer:** when you see `too many clients` or pool timeouts with a database that isn't query-bound, count `app_pods × app_pool_size` against `max_connections` before touching anything. If it exceeds DB capacity, the answer is a transaction-mode pooler sized to DB vCPU — not a higher connection ceiling.

Cross-reference: canonical rules [`../best-practices/pool-connections.md`](../best-practices/pool-connections.md) and [`../best-practices/size-connection-pools-to-the-database-not-the-app.md`](../best-practices/size-connection-pools-to-the-database-not-the-app.md); the [`../skills/connection-pool-tuning/SKILL.md`](../skills/connection-pool-tuning/SKILL.md) playbook has the sizing formulas and `pgbouncer.ini` example. The app-side ORM session/transaction scope (how long a connection is held per request) is `backend-engineering`'s lane.
