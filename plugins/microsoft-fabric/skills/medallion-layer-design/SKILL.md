---
name: medallion-layer-design
description: "Playbook for designing bronze/silver/gold medallion layers on OneLake — per-layer V-Order, file-size targeting, partitioning vs Liquid Clustering, deletion vectors, and materialized lake view decisions."
---

# Medallion Layer Design

## When to Use This Skill

Use when setting up a new Lakehouse or when auditing an existing one for performance, cost, or correctness issues in the medallion structure.

## 1. Layer Purpose and Constraints

| Layer | What it holds | Key constraints |
|---|---|---|
| **Bronze** | Raw, immutable ingested data — exact copy of source | Never alter; append-only; no V-Order; schema may be loose |
| **Silver** | Cleansed, conformed, deduplicated | V-Order optional (helps reads, costs writes); apply Liquid Clustering; deletion vectors for MERGE-heavy tables |
| **Gold** | Business-ready aggregates shaped for consumption | V-Order ON (required for Direct Lake); narrow schema; no PII; served to semantic models and SQL endpoint |

**Never serve bronze to Direct Lake or the SQL endpoint** — this is a hard rule (CLAUDE.md §3 #3).

## 2. V-Order Settings by Layer

```python
# Bronze — write raw, no optimization overhead
df.write.format("delta").option("delta.parquet.vorder.enabled", "false").save(bronze_path)

# Silver — optional; enable only if this table is read frequently without gold shaping
# (default is on in Fabric Runtime 1.3+; set explicitly to be intentional)

# Gold — always on; prerequisite for Direct Lake framing efficiency
df.write.format("delta").option("delta.parquet.vorder.enabled", "true").save(gold_path)
```

V-Order adds ~15% write overhead and reduces read cost — the trade pays off at gold where reads dominate.

## 3. File Size Targeting

| Layer | Target file size | Rationale |
|---|---|---|
| Bronze | 128–256 MB | Minimize small-file problem from streaming/micro-batch ingestion |
| Silver | 256–512 MB | Balance query parallelism vs file count |
| Gold | 128–256 MB | Smaller files suit Direct Lake framing (reads one file per column stripe) |

Use `OPTIMIZE` + `VACUUM` as a maintenance job — not inline in the ingestion notebook:

```sql
OPTIMIZE schema.gold_sales ZORDER BY (customer_id, order_date);
VACUUM schema.gold_sales RETAIN 168 HOURS;
```

## 4. Partitioning vs Liquid Clustering

| Scenario | Choice | Why |
|---|---|---|
| High-cardinality column (customer_id, order_id) | **Liquid Clustering** | Static partitions explode file count |
| Low-cardinality, time-based (year/month) + high daily volume | Static partition by `year`/`month` | Reduces scan on date-range queries |
| Mixed (date range + customer filter) | **Liquid Clustering** on both columns | Handles cross-dimension skipping |
| Direct Lake gold tables | **Liquid Clustering** preferred | Avoids over-partitioned directories that confuse framing |

```python
# Enable Liquid Clustering (Delta 3.1+ / Fabric Runtime 1.3+) [verify-at-build]
spark.sql("""
  ALTER TABLE schema.silver_orders
  CLUSTER BY (customer_id, order_date)
""")
```

## 5. Deletion Vectors

Enable on any silver or gold table with MERGE, UPDATE, or DELETE operations:

```python
spark.sql("""
  ALTER TABLE schema.silver_orders
  SET TBLPROPERTIES ('delta.enableDeletionVectors' = 'true')
""")
```

Without deletion vectors, a MERGE rewrites entire Parquet files. With them, only a small bitmap sidecar is written — dramatically reducing write amplification on CDC/upsert pipelines.

## 6. Materialized Lake View vs Notebook Gold Shaping

| Factor | Materialized Lake View (MLV) | Notebook gold |
|---|---|---|
| Refresh trigger | Defined cadence / on-demand | Pipeline-scheduled notebook |
| Compute cost | Fabric CU (no separate Spark job) | Spark session startup overhead |
| Complexity | Simple SELECT projections + aggregations | Full Spark/Python for complex logic |
| ALM | Git-tracked as workspace item | Notebook `.ipynb` in Git |

Choose MLV for straightforward projections of silver into gold. Choose a notebook for multi-step transformations, ML feature engineering, or complex business logic.

## 7. Layer Checklist

Bronze:
- [ ] Table is append-only; no UPDATE/DELETE
- [ ] Source schema preserved; no transformations
- [ ] Retention VACUUM ≥ 7 days (30 for audit requirements)

Silver:
- [ ] Duplicates removed or handled via MERGE with deletion vectors
- [ ] PII fields masked or hashed
- [ ] Liquid Clustering configured on the most-filtered columns

Gold:
- [ ] V-Order enabled
- [ ] No PII columns exposed
- [ ] Schema aligned to Direct Lake framing requirements (no spaces in column names)
- [ ] Served via SQL endpoint or Direct Lake — never raw bronze

## Pitfalls

- Serving bronze to a semantic model — query performance degrades and PII leaks
- Enabling V-Order on bronze — adds write overhead to append-heavy ingestion with no read benefit
- Static partitioning on a high-cardinality column — creates millions of directories; worse than no partitioning
- Skipping deletion vectors on a CDC table — MERGE rewrites entire files; cost spikes on high-frequency updates

## See Also

- [`../../agents/lakehouse-engineer.md`](../../agents/lakehouse-engineer.md) — Spark notebooks, Delta table maintenance, NEE
- [`../../agents/fabric-semantic-model-engineer.md`](../../agents/fabric-semantic-model-engineer.md) — gold shaping requirements for Direct Lake
- [`../../CLAUDE.md`](../../CLAUDE.md) — house opinions on medallion layers and V-Order
