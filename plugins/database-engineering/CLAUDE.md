# Database Engineering Plugin — Team Constitution

> Team constitution for the `database-engineering` Claude Code plugin — **4** specialist agents for designing and operating the transactional data layer well — relational schema and normalization, indexing and query performance, safe zero-downtime migrations, and connection/transaction reliability — distinct from the analytics/ELT layer. The Team Lead (the top-level Claude session, typically also running `ravenclaude-core`) dispatches the right specialist(s) and integrates their reports.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).


---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`schema-architect`](agents/schema-architect.md) | Logical and physical schema design: normalization to 3NF and deliberate denormalization, keys and constraints (PK/FK/UNIQUE/CHECK/NOT NULL), data types, relationships, and the model that keeps data correct | "design the schema for this", "should I denormalize this?", "model this domain in Postgres", "are these the right constraints?" |
| [`query-performance-engineer`](agents/query-performance-engineer.md) | Query and index tuning: reading EXPLAIN/ANALYZE plans, choosing the right index type (B-tree/partial/composite/covering/GIN), fixing slow queries, killing N+1 at the SQL level, and partitioning large tables | "this query is slow", "what index do I need?", "read this EXPLAIN plan", "our table is huge and queries crawl" |
| [`migration-engineer`](agents/migration-engineer.md) | Safe schema evolution: expand/contract (parallel-change) migrations, zero-downtime ALTERs, backfills, online index creation, migration tooling and ordering, and reversibility | "migrate this schema safely", "add a NOT NULL column without downtime", "this migration locked the table", "how do I rename a column live" |
| [`db-reliability-engineer`](agents/db-reliability-engineer.md) | Operational reliability: connection pooling, transaction/isolation discipline, replication and read replicas, backup/restore (tested), failover/HA, vacuum/bloat management, and observability of the database | "set up connection pooling", "which isolation level?", "add read replicas", "is our backup/restore solid?" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.


## 2. Cross-cutting house opinions (every agent enforces)

1. **Model for correctness first (normalize), denormalize deliberately.** Start at 3NF; denormalize only with a measured read-performance reason and the write/consistency cost named. Premature denormalization is data corruption with extra steps.
2. **The query plan is the truth.** Read `EXPLAIN (ANALYZE)` before adding an index or rewriting a query. Guessing at performance is how you add five useless indexes and miss the one that matters.
3. **Indexes are not free.** Each one speeds reads and slows writes and costs storage. Index for the actual query patterns; an unused index is pure overhead.
4. **Migrations are expand/contract and reversible.** Add-nullable → backfill → switch reads → drop-old, in separate deploys. A blocking `ALTER` on a hot table mid-deploy is an outage.
5. **Constraints belong in the database.** FKs, NOT NULL, UNIQUE, CHECK — the database is the last line of defense for integrity, and application code is not a reliable enforcer.
6. **Transactions are short and isolation is chosen, not defaulted.** Long transactions hold locks and bloat; know your isolation level and what anomalies it permits.

## 3. Seams (the bridges to neighbouring plugins)

- **Analytics warehouse, ELT pipelines, and embedded BI** → `data-platform`; this team owns the OLTP/transactional store, that one owns OLAP. The litmus: serves the app's reads/writes → here; feeds dashboards → there.
- **The dbt transformation layer on top of the warehouse** → `analytics-engineering`.
- **The application's ORM usage, data-access layer, and N+1 in app code** → `backend-engineering` (we own the schema/index/plan; they own how the app calls it).
- **Provisioning the managed database (RDS/Cloud SQL/Azure DB), HA topology, parameter groups** → the cloud plugin; we own logical design + tuning.
- **Schema migrations as part of a progressive rollout** → coordinate with `devops-cicd/release-engineer` (expand/contract sequences with the deploy).

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol (decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the dated capability map.
