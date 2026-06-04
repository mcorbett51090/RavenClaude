---
description: "Fix data-access issues: kill N+1, set transaction boundaries, add cache-aside with invalidation + stampede protection, outbox."
argument-hint: "[data-access pain]"
---

You are running `/backend-engineering:optimize-data-access`. Use `backend-data-access-engineer` + the `caching-and-data-access` skill.

## Steps
1. Put queries behind a repository; set short transaction boundaries.
2. Kill N+1 (eager-load/batch); route SQL-level tuning to database-engineering.
3. Add cache-aside with an invalidation trigger + single-flight (`templates/cache-aside.md`).
4. Emit + Structured Output block.
