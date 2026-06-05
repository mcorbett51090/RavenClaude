# Size the connection pool to the database's capacity, not the app's demand

**Status:** Absolute rule
**Domain:** Database operations / connection management
**Applies to:** `database-engineering`

---

## Why this exists

Each PostgreSQL connection consumes ~5–10 MB of shared memory and a backend process. Setting `max_connections` high and letting every application instance open its own large pool produces N × pool_size connections — far exceeding the database's practical capacity. At saturation, connections queue and latencies spike. The correct mental model: the pool size should be sized to the number of concurrent in-flight queries the database can process efficiently (often 2–4× the number of vCPUs), not to the number of app instances or the concurrency the app can theoretically generate.

## How to apply

```
# Calculation guide
# PostgreSQL practical max useful connections ≈ (2 × vCPUs) to (4 × vCPUs)
# For a 4-vCPU RDS instance: ~8–16 connections for query execution
# PgBouncer pool_size per database = target DB connections (e.g., 20)
# App pool size per pod = PgBouncer pool_size / replica_count
# (so that all pods together don't exceed PgBouncer's pool)

# PgBouncer pgbouncer.ini
[databases]
myapp = host=db.internal port=5432 dbname=myapp

[pgbouncer]
pool_mode = transaction      # transaction pooling — most efficient
max_client_conn = 500        # app-side connections to PgBouncer
default_pool_size = 20       # PgBouncer → Postgres connections (size to DB capacity)
```

**Do:**
- Use a connection pooler (PgBouncer) in transaction mode between the app and Postgres.
- Set `default_pool_size` in PgBouncer to the number of connections the database can handle efficiently (2–4× vCPUs as a starting estimate).
- Monitor `pg_stat_activity` for idle connections and connection wait time; alert on prolonged waits.
- Use `max_client_conn` in PgBouncer to absorb app-side burst without growing the DB connection count.

**Don't:**
- Set `max_connections = 1000` in Postgres and let every app pod open 20 connections — the arithmetic doesn't hold.
- Tune pool sizes without measuring: run `SHOW max_connections; SELECT count(*) FROM pg_stat_activity;` first.
- Use session-mode PgBouncer with prepared statements unless you handle the statement cache carefully — transaction mode is simpler.

## Edge cases / when the rule does NOT apply

A small, low-traffic application where the total connection count across all instances never approaches Postgres's limit may not need a connection pooler — but the rule still applies to sizing the per-app pool conservatively.

## See also

- [`../agents/db-reliability-engineer.md`](../agents/db-reliability-engineer.md) — owns connection pool sizing and operational database reliability.
- [`./pool-connections.md`](./pool-connections.md) — the foundational pooling rule; this doc adds the sizing discipline.

## Provenance

PgBouncer documentation and the "Don't use a pool of 100" PostgreSQL community guidance. Codifies `db-reliability-engineer`'s connection-pool sizing responsibility from CLAUDE.md §2.

---

_Last reviewed: 2026-06-05 by `claude`_
