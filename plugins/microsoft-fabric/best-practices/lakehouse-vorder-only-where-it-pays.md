# V-Order earns its keep on read-heavy gold — pay the write tax only where reads cash it in

**Status:** Pattern — V-Order on gold consumed by Direct Lake / SQL is the strong default; V-Order on bronze (or on write-heavy staging) is a write tax with no reader to pay it back.

**Domain:** Delta optimization / V-Order

**Applies to:** `microsoft-fabric`

---

## Why this exists

V-Order is a write-time optimization that reorders and compresses Parquet so VertiPaq (and the SQL engine) read it faster — Direct Lake loads V-Ordered data **measurably faster** because V-Ordering increases RLE compression quality, so the cold-load transcode is cheaper. But V-Order costs CPU on **every write**. Apply it to a high-churn bronze landing zone and you pay the tax thousands of times for data no interactive consumer ever queries directly (you don't serve bronze to Direct Lake — house opinion #3). The rule is a *placement* rule: V-Order belongs where the read benefit is realized, which is gold, and conditionally silver when silver is consumed directly by significant SQL/Power BI.

## How to apply

Match V-Order to who reads the layer:

| Layer | V-Order | Reason |
|---|---|---|
| **Bronze** | **No** | pure write overhead; no direct interactive consumer |
| **Silver** | optional | on only if SQL/Power BI consumption of silver is significant |
| **Gold (Direct Lake)** | **Required** | the read contract; V-Order quality drives cold-load transcode speed |
| **Gold (SQL endpoint)** | Yes | beneficial for the read-only SQL analytics endpoint |

```sql
-- Gold: V-Order is the default. Set write-side auto-optimize, then OPTIMIZE … VORDER.
ALTER TABLE gold.sales SET TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact'   = 'true');
OPTIMIZE gold.sales VORDER;

-- Bronze: keep V-Order OFF at the session/table level so high-rate ingest stays cheap.
SET spark.sql.parquet.vorder.default = false;   -- bronze ingestion notebook
```

**Do:**
- V-Order **gold** tables a Direct Lake or SQL-endpoint model reads; it's part of the read contract.
- Leave V-Order **off bronze** — the write tax buys nothing there.
- Treat silver's V-Order as a judgment call tied to whether silver is queried directly.

**Don't:**
- Disable V-Order on a gold table a Direct Lake model reads (house opinion #4; the anti-pattern hook flags this).
- Enable V-Order on bronze or on a write-heavy staging table that only Spark transforms read.

## Edge cases / when the rule does NOT apply

- **Spark-only gold** (no Direct Lake / SQL-endpoint consumer) tolerates V-Order *optional* — tune to Spark, not VertiPaq.
- **A gold table that is also a high-churn merge target** — keep V-Order but lean on deletion vectors and infrequent `OPTIMIZE … VORDER` so you're not re-V-Ordering on every micro-batch (see [`delta-optimize-vacuum-cadence.md`](./delta-optimize-vacuum-cadence.md)).
- **Pure compliance archive** in Delta that nobody queries interactively — V-Order is wasted; skip it.

## See also

- [`shape-gold-for-direct-lake.md`](./shape-gold-for-direct-lake.md) — the full gold physical-shape contract V-Order is one part of
- [`delta-optimize-vacuum-cadence.md`](./delta-optimize-vacuum-cadence.md) — when OPTIMIZE … VORDER runs vs how often
- [`../knowledge/medallion-on-onelake.md`](../knowledge/medallion-on-onelake.md) — the per-layer optimization matrix
- [`../agents/lakehouse-engineer.md`](../agents/lakehouse-engineer.md)

## Provenance

Codifies house opinion #4 ("V-Order on gold for Direct Lake; not on bronze") from [`../CLAUDE.md`](../CLAUDE.md) §3, grounded in [Understand Direct Lake query performance](https://learn.microsoft.com/fabric/fundamentals/direct-lake-understand-storage) ("Direct Lake performance is optimal on V-Ordered Parquet files because V-Ordering increases the quality of RLE compression") and the per-layer table in [Table maintenance and optimization](https://learn.microsoft.com/fabric/fundamentals/table-maintenance-optimization) (Microsoft Learn, retrieved 2026-05-30).

---

_Last reviewed: 2026-05-30 by `claude`_
