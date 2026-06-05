---
name: connection-pool-tuning
description: "Playbook for sizing and configuring a database connection pool (PgBouncer or application-level) — calculating the right pool size, choosing the pooling mode, diagnosing pool exhaustion, and avoiding the common over-provisioning trap."
---

# Connection Pool Tuning

## When to invoke

Use when: connections are exhausted under load (`too many connections`, `connection refused`), p99 latency spikes without corresponding query slowness, you are scaling horizontally and haven't revisited the pool, or you are adding a new service that shares a database.

## Concepts

| Term | Meaning |
|---|---|
| `max_connections` | Postgres hard limit (server-side); each connection holds ~5–10 MB of server RAM |
| Pool size | Maximum connections the pool will open to the backend |
| Min idle | Connections held warm; trade-off between latency and resource |
| Checkout timeout | How long a caller waits before getting "pool exhausted" error |
| PgBouncer | External pooler — sits between app and Postgres; recommended for high-concurrency |

## Step 1 — Establish the capacity envelope

```sql
-- Current headroom
SHOW max_connections;
SELECT count(*) FROM pg_stat_activity WHERE state != 'idle';
SELECT count(*) FROM pg_stat_activity;
```

Reserve connections:
- `~3` for superuser (`superuser_reserved_connections`)
- `~2–5` for monitoring/admin tools
- Remaining: available to pool(s)

**Formula:** `available = max_connections - reserved`

For RDS/Aurora: `max_connections` is instance-class-based. `db.t3.medium` allows ~170; `db.r6g.large` allows ~1500. Check AWS docs for exact values — do not assume.

## Step 2 — Choose pooling mode (PgBouncer)

| Mode | When to use | Caveats |
|---|---|---|
| Session | Each client gets a dedicated backend connection for its lifetime | No multiplexing benefit; avoid for web apps |
| Transaction | Connection released back to pool at transaction end | **Recommended for most apps.** Breaks `SET` / prepared statements without `server_reset_query` |
| Statement | Connection released after each statement | Incompatible with multi-statement transactions |

**Default recommendation: transaction pooling.**

Incompatibilities to resolve in transaction mode:
- Disable `DISCARD ALL` and use `server_reset_query = DISCARD ALL` in PgBouncer
- Prepared statements: use named prepared statements per-session, or disable server-side prepared statements in the app driver

## Step 3 — Size the pool

```
Pool size = (# app instances) × (# threads/workers per instance) × (avg concurrent DB calls per thread)
```

Example: 10 app pods, 4 workers each, each worker holds 1 DB connection at a time → **40 connections needed**.

Rule of thumb: pool size per service rarely exceeds `(CPU cores on DB server) × 2 + num_disks`. More connections than this causes context-switch overhead and slows all queries.

**PgBouncer `pgbouncer.ini` example:**

```ini
[databases]
mydb = host=db.internal port=5432 dbname=mydb

[pgbouncer]
pool_mode = transaction
max_client_conn = 500        # app-side: total PgBouncer clients
default_pool_size = 40       # backend connections to Postgres per database+user pair
min_pool_size = 5
reserve_pool_size = 5
reserve_pool_timeout = 3
server_idle_timeout = 600
log_connections = 0          # set to 1 only during debugging
```

## Step 4 — Application-level pool (HikariCP / SQLAlchemy / pgx)

If using an app-level pool (no external pooler):

```python
# SQLAlchemy example
engine = create_engine(
    DATABASE_URL,
    pool_size=10,          # per process
    max_overflow=5,        # burst above pool_size; total max = 15
    pool_timeout=30,       # raise if no connection available after 30s
    pool_pre_ping=True,    # test connection health on checkout
    pool_recycle=3600,     # recycle connections older than 1 hour
)
```

`pool_pre_ping=True` is critical in containerized environments where TCP connections are silently dropped after idle periods.

## Step 5 — Diagnose pool exhaustion

```sql
-- Connection wait times and idle transactions
SELECT pid, state, wait_event_type, wait_event, query_start, now() - query_start AS duration, query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC;

-- Connections by application
SELECT application_name, state, count(*)
FROM pg_stat_activity
GROUP BY 1, 2 ORDER BY 3 DESC;
```

Check `pg_stat_activity` for:
- **`idle in transaction`** rows with long duration → application not committing; fix the ORM/transaction boundary.
- **`ClientRead` or `ClientActive`** exceeding pool size → pool is full and callers are queueing.

## Pitfalls

- **Over-sizing the pool** — 500 backend connections on a 4-core database causes lock contention and scheduler overhead that slows every query.
- **`pool_pre_ping=False` on long-lived pods** — stale TCP connections fail silently under load, causing cryptic "connection closed" errors.
- **Transaction pooling + `SET` commands** — settings like `SET search_path` are per-session; in transaction pooling they are lost at transaction end. Use `search_path` in the connection string instead.
- **Ignoring `idle in transaction`** — these hold locks and bloat. A 30-second idle-in-transaction limit (`idle_in_transaction_session_timeout = 30s`) is a safe guard.
- **Not accounting for migrations** — migration tools open their own connections outside the pool; subtract their concurrency from available headroom before sizing.
