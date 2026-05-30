# Update gold non-destructively — destructive rewrites kill incremental framing

**Status:** Primary diagnostic — when a Direct Lake model goes cold (slow) after every data load despite small changes, check whether the gold load pattern is destructive first.

**Domain:** Delta write patterns / Direct Lake framing

**Applies to:** `microsoft-fabric`

---

## Why this exists

Direct Lake's killer feature is **incremental framing**: when a Delta table changes, the semantic model drops only the *affected* column segments and keeps dictionaries and unchanged segments resident in memory — so a small data change causes a small reload, and queries stay near-warm. A **destructive update pattern** — `INSERT OVERWRITE`, a full table rewrite, dropping-and-recreating, or a `MERGE` that rewrites whole files unnecessarily — invalidates *everything*. The model goes fully **cold**: every dictionary must be re-transcoded on the next query. You can confirm a destructive load by querying `INFO.STORAGETABLECOLUMNSEGMENTS()` after a refresh — if a previously-warm model shows no resident segments, the load was destructive. The fix is to write so that unchanged data stays byte-stable.

## How to apply

Use append/merge patterns that touch only changed rows, and keep deletion vectors on merge-heavy tables so updates don't force full-file rewrites.

```sql
-- Non-destructive: MERGE only the changed keys; deletion vectors avoid full-file rewrites.
ALTER TABLE gold.dim_customer SET TBLPROPERTIES ('delta.enableDeletionVectors' = 'true');

MERGE INTO gold.dim_customer t
USING staging.customer_delta s ON t.customer_id = s.customer_id
WHEN MATCHED THEN UPDATE SET ...
WHEN NOT MATCHED THEN INSERT ...;
-- Avoid: INSERT OVERWRITE gold.dim_customer SELECT * FROM ...   (destructive — full cold reload)
```

- **Append-mostly** for fact tables; **MERGE on keys** for dimensions.
- **Deletion vectors on** for merge/update/delete-heavy tables (house opinion #13) so a changed row marks a tombstone instead of rewriting its whole file.
- After a load, **reframe** the model (scheduled or programmatic) — framing is the cheap metadata operation; the destructive *write* is what's expensive downstream.

**Do:**
- Prefer `MERGE` / append over `INSERT OVERWRITE` / drop-recreate for any table a Direct Lake model reads.
- Enable deletion vectors on merge-heavy gold/silver tables.
- Diagnose "cold after every load" with `INFO.STORAGETABLECOLUMNSEGMENTS()` — no resident segments after a small change ⇒ destructive pattern.

**Don't:**
- `INSERT OVERWRITE` or drop-and-recreate a large gold table on every batch — you forfeit incremental framing.
- Assume small Delta tables need this — incremental framing optimization is a large-table concern.

## Edge cases / when the rule does NOT apply

- **Small Delta tables** don't need to be optimized for incremental framing — a full rewrite of a tiny dimension is cheap.
- **A deliberate full reload** (schema change, backfill, correctness fix) is a legitimate one-time destructive op — expect a cold model after and let it re-warm.
- **Import-mode models** don't frame — this rule is Direct-Lake-specific.

## See also

- [`shape-gold-for-direct-lake.md`](./shape-gold-for-direct-lake.md) — the gold shape framing operates over
- [`delta-optimize-vacuum-cadence.md`](./delta-optimize-vacuum-cadence.md) — OPTIMIZE also evicts segments; run it infrequently for Direct Lake
- [`name-your-direct-lake-mode.md`](./name-your-direct-lake-mode.md) — on-OneLake errors (doesn't fall back) when a table isn't framed
- [`../agents/lakehouse-engineer.md`](../agents/lakehouse-engineer.md) · [`../agents/fabric-semantic-model-engineer.md`](../agents/fabric-semantic-model-engineer.md)

## Provenance

Grounded in [Understand Direct Lake query performance](https://learn.microsoft.com/fabric/fundamentals/direct-lake-understand-storage) ("Avoid destructive update patterns on large Delta tables to preserve incremental framing"; the `INFO.STORAGETABLECOLUMNSEGMENTS()` diagnostic; "If the model was warm before framing, this means the Delta table was updated using a destructive data loading pattern") and [How Direct Lake works — incremental framing](https://learn.microsoft.com/fabric/fundamentals/direct-lake-how-it-works) — Microsoft Learn, retrieved 2026-05-30. Supports house opinions #8/#13.

---

_Last reviewed: 2026-05-30 by `claude`_
