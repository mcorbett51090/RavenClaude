---
name: caching-and-data-access
description: "Own the data-access layer: queries behind a repository, short explicit transaction boundaries (never across HTTP), kill ORM N+1 by eager-loading/batching, and cache-aside with a defined invalidation trigger plus stampede (single-flight) protection."
---

# Caching & Data Access

## Repository layer
Persistence behind a repository; no raw ORM in controllers. Transaction boundaries live here — **short**, never spanning an external HTTP call.

## Kill N+1
The #1 ORM perf bug. Eager-load/join/batch what you iterate; detect in tests. SQL-level tuning -> `database-engineering`.

## Cache-aside
Read-through; write invalidates/updates; TTL as a safety net. **No invalidation story = stale-data generator.**

## Stampede
On a hot-key miss, **single-flight**/lock so a thousand misses don't all hit the DB.
