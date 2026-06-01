# Warehouse dimensional loads — surrogate keys, SCD type-2, idempotent MERGE

**Status:** Pattern — strong default for Fabric Warehouse dimensional ELT; deviate only with a written reason.

**Domain:** Warehouse / dimensional modeling

**Applies to:** `microsoft-fabric`

---

## Why this exists

The Fabric **lakehouse** has a stack of best-practices (V-Order, medallion boundaries, clustering, non-destructive merge); the **warehouse** persona had none — its dimensional-ELT craft lived only in the `warehouse-engineer` agent's prose. That asymmetry is an accident of build order, not a design choice. A senior warehouse engineer loading dimensions hits the same recurring decisions every time — surrogate keys, slowly-changing dimensions, idempotent upserts — and there was no citable rule. Getting these wrong produces duplicate dimension rows on re-run, lost history, or a load that isn't safe to retry after a partial failure.

## How to apply

**Surrogate keys, not business keys, as the dimension PK.** Generate a warehouse-owned surrogate (identity or a hash of the business key) so facts join on a stable integer/hash and the business key can change without breaking history.

**SCD type-2 for dimensions whose history matters** (customer tier, territory, status):

- Keep `BusinessKey`, `SurrogateKey`, `EffectiveFrom`, `EffectiveTo`, `IsCurrent`.
- On change: close the current row (`EffectiveTo = now`, `IsCurrent = 0`) and insert a new current row. Type-1 (overwrite) only where history is genuinely irrelevant.

**Idempotent MERGE — the load must be safe to re-run.** A dimension/fact load that runs twice (retry, backfill) must not duplicate. Use `MERGE` keyed on the business key (dim) or the natural grain (fact); `WHEN MATCHED` update / close, `WHEN NOT MATCHED` insert.

```sql
-- SCD-2 dimension upsert (sketch): close changed current rows, then insert new versions
MERGE dim.Customer AS tgt
USING staging.Customer AS src ON tgt.BusinessKey = src.BusinessKey AND tgt.IsCurrent = 1
WHEN MATCHED AND (tgt.Tier <> src.Tier OR tgt.Territory <> src.Territory)
  THEN UPDATE SET EffectiveTo = SYSUTCDATETIME(), IsCurrent = 0;
-- second statement inserts the new current version for the changed/new keys
```

**Batch the load in one transaction boundary** so a mid-load failure rolls back cleanly (Fabric Warehouse supports multi-table transactions) — don't leave dimensions half-updated.

**Do:** surrogate keys; SCD-2 with effective-dating where history matters; MERGE keyed on business key/grain; wrap a load batch in a transaction; stage then merge.

**Don't:** join facts on raw business keys; overwrite (type-1) a dimension whose history a report needs; write an `INSERT`-only load that duplicates on re-run.

## Edge cases / when the rule does NOT apply

A small, static reference dimension (currencies, a fixed status list) may be fine as a truncate-and-reload — SCD-2 is for dimensions that *change over time and whose past matters*. Very high-volume facts may use partition-swap/insert patterns instead of row-level MERGE for performance — measure first. Fabric Warehouse T-SQL surface area vs SQL Server (some commands unsupported) is version-sensitive — `[verify-at-build]`.

## See also

- [`./warehouse-security-rls-cls-masking.md`](./warehouse-security-rls-cls-masking.md) — securing the warehouse you just modeled
- [`./lakehouse-vs-warehouse-choose-from-the-tree.md`](./lakehouse-vs-warehouse-choose-from-the-tree.md) — when the warehouse is the right engine at all
- [`./lakehouse-nondestructive-merge-for-framing.md`](./lakehouse-nondestructive-merge-for-framing.md) — the lakehouse-side merge sibling
- [`../agents/warehouse-engineer.md`](../agents/warehouse-engineer.md) — owns warehouse ELT
- [Fabric Warehouse — tables, transactions, T-SQL surface](https://learn.microsoft.com/fabric/data-warehouse/) — authoritative

## Provenance

Surfaced by the two-panel + tiebreak coverage campaign (2026-06-01): the warehouse persona had zero best-practices vs the lakehouse's seven — an accident of build order both panels agreed was a real gap. Grounded in Fabric Warehouse + dimensional-modeling (Kimball SCD) guidance. T-SQL surface area is `[verify-at-build]`.

---

_Last reviewed: 2026-06-01 by `claude`_
