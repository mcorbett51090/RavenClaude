# Liquid Clustering over static partitioning — and never high-cardinality partition columns

**Status:** Pattern — Liquid Clustering / Z-order is the strong default for silver/gold file skipping; static partitioning is reserved for a low-cardinality, high-volume case with a written reason.

**Domain:** Delta layout / file skipping

**Applies to:** `microsoft-fabric`

---

## Why this exists

Static Hive-style partitioning was the old way to get file skipping, but it has a failure mode that hurts Fabric specifically: a **high-cardinality partition column explodes into thousands of tiny Parquet files**, and Direct Lake transcoding is *less* efficient with many small files and row groups than with fewer large ones. Worse, framing can outright **fail if a Delta table exceeds the guardrails — e.g. more than 10,000 Parquet files**. Liquid Clustering (and Z-order on older paths) delivers file skipping *without* the directory-per-value explosion, so you get the read benefit and keep the large-file shape Direct Lake needs. This is house opinion #12.

## How to apply

Cluster on the columns you filter/join by; do not partition on anything high-cardinality.

```sql
-- Silver/gold: liquid clustering on the common filter/join keys (low-to-moderate cardinality).
ALTER TABLE silver.orders CLUSTER BY (order_date, region);

-- Then compact so clustering produces large, skip-friendly files.
OPTIMIZE silver.orders;
```

- **Cluster keys** = the columns queries filter or join on most (a date key + a dimension key is the common pair). Keep the count small (≈ up to 4).
- **Avoid partitioning by** anything high-cardinality (customer ID, GUID, timestamp-to-the-second). If you partition at all, partition only **high-volume bronze** by a coarse, low-cardinality key (e.g. ingest date) and only if it genuinely helps incremental loads.
- **Target large files** (gold 400 MB–1 GB) so skipping operates on fat row groups, not slivers.

**Do:**
- Use Liquid Clustering on silver/gold; cluster by the real query predicates.
- Watch the **file count** — a table drifting toward 10,000 Parquet files is a framing-failure risk; `OPTIMIZE` it down.
- Re-evaluate cluster keys when query patterns shift; clustering keys are query-driven, not schema-driven.

**Don't:**
- Partition by a high-cardinality column — it shreds the table into tiny files and degrades Direct Lake transcoding (and can break framing past the guardrail).
- Stack static partitioning *and* clustering hoping for more skipping; pick clustering for new silver/gold tables.

## Edge cases / when the rule does NOT apply

- **Small Delta tables** don't need clustering *or* partitioning for incremental framing — the small-file/skipping problem is a large-table concern.
- **A genuinely low-cardinality, high-volume bronze table** where partition pruning materially speeds incremental loads — coarse partitioning can be defensible; write down why.
- **Eventhouse/KQL** has its own time-based partitioning policy — this rule is about lakehouse/warehouse Delta, not KQL extents.

## See also

- [`shape-gold-for-direct-lake.md`](./shape-gold-for-direct-lake.md) — the large-file targets clustering should preserve
- [`directlake-stay-under-guardrails.md`](./directlake-stay-under-guardrails.md) — the file-count / row-group guardrails partitioning can blow past
- [`../knowledge/medallion-on-onelake.md`](../knowledge/medallion-on-onelake.md) — the per-layer layout column
- [`../agents/lakehouse-engineer.md`](../agents/lakehouse-engineer.md)

## Provenance

Codifies house opinion #12 ("Liquid Clustering / Z-order over static partitioning") from [`../CLAUDE.md`](../CLAUDE.md) §3, grounded in [Understand Direct Lake query performance](https://learn.microsoft.com/fabric/fundamentals/direct-lake-understand-storage) ("Avoid high cardinality partition columns…", "prefer large column segments") and [How Direct Lake works](https://learn.microsoft.com/fabric/fundamentals/direct-lake-how-it-works) (framing may fail past ~10,000 Parquet files) — Microsoft Learn, retrieved 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
