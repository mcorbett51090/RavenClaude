# DBRE 2026 reference (dated — verify at use)

> **Retrieval date: 2026-07-15.** Engine HA feature matrices, managed-service SLAs
> and RPO/RTO guarantees, tool flags, and version-specific migration hazards move
> fast. Every figure carries a re-verify-at-use rider per ravenclaude-core's Claim
> Grounding protocol. The *methods* in
> [`dbre-decision-trees.md`](dbre-decision-trees.md) are durable; the *facts* below
> are snapshots. When a claim gates an irreversible action (a failover, a migration,
> a retention change), re-verify against the engine/provider's current docs first.

## 1. HA & replication by engine family (verify per version)

Concepts are durable; exact feature names/flags are version-specific — check your
engine's current docs.

| Engine family | Replication | Automatic failover options | Notes |
| --- | --- | --- | --- |
| **PostgreSQL** | Streaming (async/sync), logical | Patroni, repmgr, pg_auto_failover, or managed (RDS/Aurora/Cloud SQL) | Sync replication protects RPO at write-latency cost; quorum commit available |
| **MySQL / MariaDB** | Async, semi-sync, Group Replication | Orchestrator, Group Replication/InnoDB Cluster, MHA, or managed | Semi-sync bounds data loss; GTIDs simplify failover |
| **MongoDB** | Replica sets (built-in) | Automatic within a replica set (elections) | Write concern `majority` bounds RPO; read concern for staleness |
| **Redis / Valkey** | Async replication | Sentinel, or Cluster mode | Replication is async — data loss on failover is possible by design |
| **Distributed SQL** (CockroachDB, Spanner, Yugabyte, TiDB) | Raft/Paxos quorum, built-in | Automatic (consensus) | Survives node/AZ/region loss by design; different consistency/latency tradeoffs |

**Durable rule (not dated):** whatever the engine, a replica in the same failure
domain is not HA, and a failover path never exercised will fail when it counts.

## 2. Managed-service reliability features (verify current SLAs)

Managed offerings (RDS/Aurora, Cloud SQL/AlloyDB, Azure Database) typically provide
automated backups + PITR, multi-AZ failover, and read replicas — **but the exact
RPO/RTO, failover time, and SLA are provider- and tier-specific and change.** Never
quote a specific RTO/RPO from memory; read the current SLA. The managed-vs-self
tradeoff (dbre-architect §managed-vs-self-hosted) turns on *your on-call capacity*,
not just the feature list.

## 3. Backup & PITR mechanisms (durable) with dated tool notes

- **Continuous archiving + PITR** — base backup + WAL (Postgres) / binlog (MySQL)
  streaming to restore to any point in time. The gold standard for near-zero RPO.
- **Snapshot backups** — storage/volume snapshots; fast but crash-consistent unless
  coordinated with the engine.
- **Logical dumps** (`pg_dump` / `mysqldump`) — portable, slow to restore at scale;
  fine for small DBs and schema-only, not a primary strategy for large ones.
- **Tools (names date — verify):** pgBackRest / Barman (Postgres), Percona XtraBackup
  (MySQL), and managed snapshot systems. Pick at build time and pin versions.

**Durable rule:** a backup is unverified until a restore is tested; store backups
in a separate, immutable, encrypted failure domain; measure actual restore time
against RTO.

## 4. Online-migration tooling (verify current versions)

- **Postgres:** additive changes + `CREATE INDEX CONCURRENTLY`; expand-contract for
  everything else; watch `lock_timeout` and long-lock hazards on hot tables.
- **MySQL:** `ALGORITHM=INPLACE`/instant DDL where supported, or external tools like
  gh-ost / pt-online-schema-change for large hot-table changes.
- **Backfills:** batched + throttled + idempotent regardless of engine; pace against
  replication lag.

Version-specific DDL hazards (which operations take which lock) change between
releases — **verify against the target version's docs**, dated.

## 5. Connection pooling (durable)

- **Why:** each DB connection costs memory/backends; unbounded app connections cause
  connection storms. A pooler (PgBouncer/ProxySQL, or app-side pools) caps this.
- **Modes:** transaction pooling (highest reuse, some feature limits) vs session
  pooling (fewer limits, less reuse). Choose per workload.
- **Sizing:** total app pool must stay under the DB's connection ceiling with
  headroom for admin + replicas.

## 6. Key DB SLIs to instrument (durable)

Availability (successful-connection + query-success rate), query latency
percentiles (p50/p95/p99), replication lag (seconds behind), connection saturation
(active vs max), disk/IOPS/CPU headroom, and backup-verification freshness. Alert
thresholds distinguish *page* from *ticket*; tie SLOs to the reliability targets,
not vanity metrics.

## 7. Cross-plugin seams (stable)

| Need | Plugin |
| --- | --- |
| Schema design, indexing, query optimization, data modeling | `database-engineering` |
| App-level SRE, service SLOs, alerting platform, incident command | `observability-sre` |
| Provisioning (IaC), networking, storage classes | `terraform-iac`, `aws-cloud` / `gcp-cloud` / `azure-cloud` |
| Data pipelines / ETL / orchestration | `data-orchestration` |
| Access control, encryption, auditing, secrets | `security-engineering`, `auth-identity` |
| Security incident on the DB (breach, ransomware) | `incident-response-dfir` |
