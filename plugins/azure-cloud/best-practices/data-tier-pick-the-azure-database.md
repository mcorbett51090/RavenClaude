# Pick the Azure data tier deliberately — relational, document, or wide-column by workload

**Status:** Primary diagnostic — when an app needs a managed database on Azure and someone reaches for "the one we always use," check the workload shape against this first.

**Domain:** Data tier / architecture

**Applies to:** `azure-cloud`

---

## Why this exists

`azure-architect` owns the non-Fabric application data tier (Azure SQL / Cosmos DB / PostgreSQL Flexible Server / Storage), but no rule backed that ownership — so the habitual answer ("Azure SQL, like last time" or "Cosmos, it's web-scale") drove the choice instead of the workload. The data engine is one of the hardest decisions to reverse: it shapes the data model, the query surface, the cost curve, and the scaling story. Picking by familiarity instead of by access pattern is a multi-quarter mistake. This rule is the deliberate pick.

## How to apply

Match the engine to the **dominant access pattern and consistency need**, not to team habit:

| Engine | Pick when | Watch out |
|---|---|---|
| **Azure SQL Database** | Relational, transactional, strong consistency; joins + reporting; an existing SQL Server app | Choose vCore (predictable) vs DTU (simple); serverless for spiky/dev; Hyperscale past ~1–4 TB |
| **Azure SQL Managed Instance** | Lift-and-shift of on-prem SQL Server needing instance-scoped features (SQL Agent, cross-DB queries, CLR) | Higher floor cost + longer deploy than SQL DB — only when you need instance features |
| **PostgreSQL Flexible Server** | Open-source relational, OSS portability, PG extensions (PostGIS, pgvector) | Flexible Server (not the retiring Single Server); pick zone-redundant HA for prod |
| **Cosmos DB** | Global distribution, single-digit-ms at scale, schemaless/document or key-value, massive write throughput | Partition-key choice is permanent and load-bearing; model for the query, provision RU/s deliberately (or autoscale); strong consistency costs RU + latency |
| **Azure Storage (Table/Blob)** | Cheap key-value at scale, blobs, append logs, archival | Not a query engine — no joins, no rich filter; pair with a real DB if you need to query |

**Decision order (cheapest correct fit first):**
1. Is it relational with transactions/joins? → **Azure SQL DB** (MI only if you need instance features; PostgreSQL if OSS/extensions matter).
2. Does it need global distribution or schemaless write-scale? → **Cosmos DB** (commit to the partition key carefully).
3. Is it really just blobs / key-value / archival? → **Storage** — don't pay for a database you won't query.

**Do:** pick by access pattern + consistency + scale; right-size the tier (serverless/autoscale for variable load); make every data plane private (see the private-by-default rule); use managed identity for app→DB auth (passwordless).

**Don't:** default to one engine for every app; use Cosmos for a small relational app (RU cost + modeling pain); use Storage Tables as a queryable database; pick Single Server PostgreSQL (retiring).

## Edge cases / when the rule does NOT apply

Analytics/warehouse workloads belong in **Fabric / Synapse**, not this app-data-tier rule — that's `microsoft-fabric`'s lane (house seam). Caching (Azure Cache for Redis) and search (Azure AI Search) are complements, not the system of record. Exact tier limits, the Single-Server retirement date, and per-SKU pricing are version-sensitive — `[verify-at-build]`.

## See also

- [`./private-by-default-paas-data-planes.md`](./private-by-default-paas-data-planes.md) — whichever engine, lock the data plane
- [`./passwordless-by-default.md`](./passwordless-by-default.md) — managed identity for app→DB auth
- [`./pick-compute-from-the-decision-tree.md`](./pick-compute-from-the-decision-tree.md) — the sibling "which compute" discipline
- [`../agents/azure-architect.md`](../agents/azure-architect.md) — owns the data-tier decision
- [Azure SQL vs Cosmos vs PostgreSQL — choose a data store](https://learn.microsoft.com/azure/architecture/guide/technology-choices/data-store-decision-tree) — authoritative (CAF/WAF)

## Provenance

Surfaced by the two-panel + tiebreak coverage campaign (2026-06-01): `azure-architect` is named six times as the data-tier owner across the compute trees, but no best-practice or tree backed it. Grounded in the Microsoft CAF/WAF "Choose a data store" guidance. Tier limits + PostgreSQL Single-Server retirement are `[verify-at-build]`.

---

_Last reviewed: 2026-06-01 by `claude`_
