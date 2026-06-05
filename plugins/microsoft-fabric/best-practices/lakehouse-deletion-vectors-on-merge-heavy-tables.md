# Enable deletion vectors on merge-heavy Delta tables to avoid full-file rewrites

**Status:** Absolute rule
**Domain:** Lakehouse / Delta optimization
**Applies to:** `microsoft-fabric`

---

## Why this exists

Without deletion vectors, a Delta `MERGE`, `UPDATE`, or `DELETE` operation must **rewrite the entire Parquet file** that contains a modified or deleted row — even if only one row changed. On a merge-heavy SCD-2 pattern or a high-frequency CDC load, this produces write amplification: a 1 GB file is rewritten to change 10 rows. Write amplification degrades write throughput, inflates CU consumption, and fragments the Delta log. Deletion vectors (enabled via `delta.enableDeletionVectors`) mark deleted or updated row positions in a small sidecar file instead of rewriting the Parquet — the old file remains; the sidecar says which rows are stale. Rewrites (via `OPTIMIZE`) happen on a controlled cadence, not on every DML.

## How to apply

Enable deletion vectors at table creation or with an `ALTER TABLE`:

```python
# At creation
spark.sql("""
  CREATE TABLE silver.orders
  USING DELTA
  TBLPROPERTIES ('delta.enableDeletionVectors' = 'true')
""")

# On an existing table
spark.sql("""
  ALTER TABLE silver.orders
  SET TBLPROPERTIES ('delta.enableDeletionVectors' = 'true')
""")
```

Check that deletion vectors are active:

```python
from delta.tables import DeltaTable
dt = DeltaTable.forName(spark, "silver.orders")
props = dt.detail().select("properties").first()["properties"]
print(props.get("delta.enableDeletionVectors"))  # Should print 'true'
```

**Do:**
- Enable deletion vectors on **silver and gold** tables that receive MERGE/UPDATE/DELETE operations.
- Schedule `OPTIMIZE` + `VACUUM` on the normal cadence (see `delta-optimize-vacuum-cadence.md`) — deletion vectors accumulate and need periodic compaction.
- Verify compatibility: deletion vectors require Delta Lake 2.0+ (Fabric Runtime 1.2+) and are fully supported on Runtime 1.3/2.0.

**Don't:**
- Enable deletion vectors on **bronze/append-only** tables — they add overhead with no benefit on pure-append workloads.
- Skip `OPTIMIZE` after enabling deletion vectors on an existing table — the first `OPTIMIZE` will compact pre-existing Parquet files and apply pending deletion vector marks.
- Assume Direct Lake framing is unaffected — deletion vector sidecar files are read transparently by Direct Lake, but very large deletion vector accumulations before an `OPTIMIZE` can slow framing. Keep compaction current.

## Edge cases / when the rule does NOT apply

Insert-only Bronze tables (raw landing zone, append-only Eventstream sink) gain no benefit from deletion vectors and should leave the property unset to avoid the small overhead on each transaction.

## See also

- [`../agents/lakehouse-engineer.md`](../agents/lakehouse-engineer.md) — owns Delta table configuration and optimization
- [`./delta-optimize-vacuum-cadence.md`](./delta-optimize-vacuum-cadence.md) — the cadence discipline that keeps deletion vector accumulation under control

## Provenance

Codifies CLAUDE.md house opinion #13 ("deletion vectors on merge-heavy tables — avoid full-file rewrites on MERGE/UPDATE/DELETE"); Delta Lake 2.0 deletion vectors specification.

---

_Last reviewed: 2026-06-05 by `claude`_
