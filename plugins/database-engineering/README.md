# Database Engineering

The **database-engineering** plugin — designing and operating the transactional data layer well — relational schema and normalization, indexing and query performance, safe zero-downtime migrations, and connection/transaction reliability — distinct from the analytics/ELT layer.

## Agents

- **`schema-architect`** — Logical and physical schema design: normalization to 3NF and deliberate denormalization, keys and constraints (PK/FK/UNIQUE/CHECK/NOT NULL), data types, relationships, and the model that keeps data correct
- **`query-performance-engineer`** — Query and index tuning: reading EXPLAIN/ANALYZE plans, choosing the right index type (B-tree/partial/composite/covering/GIN), fixing slow queries, killing N+1 at the SQL level, and partitioning large tables
- **`migration-engineer`** — Safe schema evolution: expand/contract (parallel-change) migrations, zero-downtime ALTERs, backfills, online index creation, migration tooling and ordering, and reversibility
- **`db-reliability-engineer`** — Operational reliability: connection pooling, transaction/isolation discipline, replication and read replicas, backup/restore (tested), failover/HA, vacuum/bloat management, and observability of the database

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install database-engineering@ravenclaude
```

## Seams

- **Analytics warehouse, ELT pipelines, and embedded BI** → `data-platform`; this team owns the OLTP/transactional store, that one owns OLAP. The litmus: serves the app's reads/writes → here; feeds dashboards → there.
- **The dbt transformation layer on top of the warehouse** → `analytics-engineering`.
- **The application's ORM usage, data-access layer, and N+1 in app code** → `backend-engineering` (we own the schema/index/plan; they own how the app calls it).
- **Provisioning the managed database (RDS/Cloud SQL/Azure DB), HA topology, parameter groups** → the cloud plugin; we own logical design + tuning.
- **Schema migrations as part of a progressive rollout** → coordinate with `devops-cicd/release-engineer` (expand/contract sequences with the deploy).

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`.
