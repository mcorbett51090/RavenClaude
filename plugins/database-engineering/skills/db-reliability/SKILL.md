---
name: db-reliability
description: "Operate the database reliably: pool connections with sane limits, choose the isolation level deliberately (knowing its anomalies), keep transactions short, route replica reads carefully, and test restores — a backup is only real if you've restored it."
---

# Database Reliability

## Pool connections
A pooler (PgBouncer/built-in) with sized limits — an app opening a connection per request exhausts the DB under load.

## Isolation
Read Committed / Repeatable Read / Serializable each permit different anomalies (non-repeatable read, phantom, write skew). **Choose**, and handle what you allow.

## Short transactions
Long txns hold locks, block vacuum, bloat. Keep the critical section minimal.

## Recovery
Replicas are eventually consistent (route read-after-write carefully). **Test the restore** + PITR if RPO demands. A backup you've never restored is a hope.
