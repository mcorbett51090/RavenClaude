# Medallion architecture on OneLake (bronze / silver / gold)

**Last reviewed:** 2026-05-28 · **Confidence:** high (first-party Microsoft Learn, retrieved 2026-05-28).
**Owner:** `lakehouse-engineer` (+ `fabric-architect` for the layer-to-workspace topology).
**Source:** [Medallion on OneLake](https://learn.microsoft.com/fabric/onelake/onelake-medallion-lakehouse-architecture), [Cross-workload table maintenance and optimization](https://learn.microsoft.com/fabric/fundamentals/table-maintenance-optimization).

## The shape

Incrementally improve data quality across three layers, each its **own lakehouse/warehouse, ideally its own workspace** (control + governance at the layer boundary):

| Layer | Holds | Write pattern |
|---|---|---|
| **Bronze (raw)** | source data exactly as it arrives; immutable/append-only; original format or Delta | prioritize ingest speed |
| **Silver (curated)** | cleansed, deduped, conformed, joined, type-standardized | balance write + read |
| **Gold (business-ready)** | aggregated, denormalized, access-controlled data products for BI/ML | prioritize read |

Two deployment patterns:
- **Pattern 1** — every layer a Lakehouse; consumers read via the SQL analytics endpoint.
- **Pattern 2** — bronze + silver Lakehouses, **gold a Warehouse**; consumers read via the warehouse endpoint.

For bronze, keep source format or use Delta; **if the source is already in OneLake/ADLS/S3/GCS, create a shortcut instead of copying** (house opinion #1). Silver + gold are always Delta. Every Fabric engine writes Delta by default and applies **V-Order** for fast reads.

## Per-layer optimization (this is where engagements go wrong)

From [table maintenance and optimization](https://learn.microsoft.com/fabric/fundamentals/table-maintenance-optimization#medallion-architecture-recommendations):

| | Bronze | Silver | Gold |
|---|---|---|---|
| Priority | ingest speed | balance | read speed |
| V-Order | **No** (write overhead) | optional (on if SQL/Power BI consumption is significant) | **Required for Direct Lake**; beneficial for SQL endpoint |
| File size | small OK | 128-256 MB | 400 MB-1 GB |
| Layout | partition OK but discouraged for new | **Liquid Clustering / Z-order** | **Liquid Clustering** (file skipping) |
| Auto-compaction / optimize-write | optional | enable | required |
| Deletion vectors | enable for merge tables | enable for frequent updates | — |
| Scheduled `OPTIMIZE` | optional | aggressive | aggressive |

Gold tuning by consumer:

| Consumer | V-Order | Target file size | Row group |
|---|---|---|---|
| SQL analytics endpoint | Yes | 400 MB | 2M rows |
| **Power BI Direct Lake** | Yes | 400 MB-1 GB | 8M+ rows |
| Spark | optional | 128 MB-1 GB | 1-2M rows |

> **Do not serve bronze directly to the SQL analytics endpoint or Power BI Direct Lake** (house opinion #3).

## How to build the transforms — three options (`lakehouse-engineer` picks)

1. **Materialized lake views (MLV)** — declarative `CREATE MATERIALIZED LAKE VIEW`, dependency-ordered bronze→silver→gold refresh with built-in **data-quality constraints**; the lowest-ceremony medallion path. Direct Lake on OneLake **can** build on an MLV but **not** on a non-materialized SQL view. ([MLV tutorial](https://learn.microsoft.com/fabric/data-engineering/materialized-lake-views/tutorial))
2. **Spark/PySpark notebooks** — full control; the default when transforms are complex or need Python libraries. Use the **Native Execution Engine** (house opinion #11) and `MERGE` with partition filters for upserts.
3. **Dataflow Gen2** — low-code (300+ transforms) + Fast Copy for extract-load; good for analyst-led silver shaping. See [`fabric-data-movement-decision-tree.md`](fabric-data-movement-decision-tree.md).

## Performance defaults (house opinions #11-14)

- **#11 Native Execution Engine on by default** — Velox/Gluten vectorized engine, GA on **Runtime 1.3 (Spark 3.5)** and **Runtime 2.0 (Spark 4.1)**; the single biggest free perf/cost win for Spark. (Autotune is the *old* Runtime-1.2-only path — deprecated; do not recommend it.)
- **#12 Liquid Clustering / Z-order over static partitioning** on silver/gold — better file skipping without partition-explosion. Partition only high-frequency bronze if at all.
- **#13 Deletion vectors** on merge-heavy tables — avoids full-file rewrites on `MERGE`/`UPDATE`/`DELETE`.
- **#14 Schema-enabled lakehouses by default** — namespace hygiene and a **prerequisite for OneLake security data preview** (see [`onelake-security-and-governance.md`](onelake-security-and-governance.md)).

`ALTER TABLE … SET TBLPROPERTIES ('delta.autoOptimize.optimizeWrite'='true','delta.autoOptimize.autoCompact'='true')`; schedule `OPTIMIZE … VORDER` on gold. ([troubleshoot lakehouse](https://learn.microsoft.com/fabric/data-engineering/troubleshoot-lakehouse))
