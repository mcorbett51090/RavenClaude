# Shape gold for Direct Lake; never serve bronze

**Status:** Absolute rule — serving bronze to Direct Lake / the SQL endpoint is a bug; the gold-table optimization targets are the strong default.

**Domain:** Medallion / Direct Lake gold-shaping

**Applies to:** `microsoft-fabric`

---

## Why this exists

Direct Lake reads Delta tables straight from OneLake into VertiPaq on demand, so the **physical shape of the gold Delta table is the performance contract** — there's no refresh step to hide a badly-laid-out table behind. The optimization that helps reads (V-Order, large files, big row groups, file-skipping clustering) is exactly the optimization that *hurts* writes, which is why it belongs on **gold and not bronze**: V-Order on bronze is pure write overhead, and serving raw bronze to Direct Lake or the SQL analytics endpoint ships un-conformed, un-optimized data to a BI audience. The rule pairs a "where" (gold only) with a "what" (the per-consumer targets) so framing stays fast and queries stay in-engine.

## How to apply

Match the optimization to the layer, then tune gold to its consumer. From the Fabric table-maintenance guidance:

| | Bronze | Silver | Gold |
|---|---|---|---|
| Priority | ingest speed | balance | **read speed** |
| V-Order | **No** (write overhead) | optional | **Required for Direct Lake** |
| File size | small OK | 128–256 MB | **400 MB–1 GB** |
| Layout | partition discouraged | Liquid Clustering / Z-order | **Liquid Clustering** (file skipping) |
| Deletion vectors | enable for merge tables | enable for frequent updates | — |

Gold tuning by consumer: **Power BI Direct Lake → V-Order on, 400 MB–1 GB files, 8M+ row groups.** SQL analytics endpoint → V-Order on, 400 MB files, 2M rows.

```sql
-- Gold table: enable auto-optimize, then schedule V-Order OPTIMIZE
ALTER TABLE gold.sales SET TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact'   = 'true');
OPTIMIZE gold.sales VORDER;
```

**Do:**
- V-Order on **gold**; target 400 MB–1 GB files and 8M+ row groups for Direct Lake.
- Build gold with a **materialized lake view** when you want declarative refresh — Direct Lake on OneLake can build on an MLV, **not** a non-materialized SQL view.
- Use the **Native Execution Engine** (Runtime 1.3/2.0) for the Spark transforms — the biggest free perf win.

**Don't:**
- Serve **bronze** to Direct Lake or the SQL analytics endpoint (house opinion #3).
- Put V-Order on bronze (write overhead) or leave it off a gold table a Direct Lake model reads (house opinion #4).
- Point Direct Lake on OneLake at a **non-materialized SQL view** — it can't build on one.

## Edge cases / when the rule does NOT apply

- **Spark-only gold consumers** (not Direct Lake / SQL endpoint) tolerate optional V-Order and smaller 128 MB–1 GB files — tune to Spark, not to VertiPaq.
- **Silver consumed directly by significant SQL/Power BI** may justify V-Order on silver — it's "optional, on if consumption is significant," a judgment call, not a default.

## See also

- [`../knowledge/medallion-on-onelake.md`](../knowledge/medallion-on-onelake.md) — the full per-layer optimization matrix and the three transform options (MLV / notebook / Dataflow Gen2)
- [`name-your-direct-lake-mode.md`](./name-your-direct-lake-mode.md) — the mode choice this gold-shaping serves (framing on-OneLake, guardrails on-SQL)
- [`../agents/lakehouse-engineer.md`](../agents/lakehouse-engineer.md) · [`../agents/fabric-semantic-model-engineer.md`](../agents/fabric-semantic-model-engineer.md) — the gold-shaping ↔ model seam

## Provenance

Codifies house opinions #3 ("Medallion … never serve bronze to Direct Lake / the SQL endpoint") and #4 ("V-Order on gold for Direct Lake; not on bronze") from [`../CLAUDE.md`](../CLAUDE.md) §3, grounded in the per-layer and per-consumer optimization tables in [`../knowledge/medallion-on-onelake.md`](../knowledge/medallion-on-onelake.md) and [`../knowledge/direct-lake-and-semantic-models.md`](../knowledge/direct-lake-and-semantic-models.md) (Microsoft Learn table-maintenance guidance, retrieved 2026-05-28).

---

_Last reviewed: 2026-05-30 by `claude`_
