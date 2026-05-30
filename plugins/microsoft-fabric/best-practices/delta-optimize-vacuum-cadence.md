# OPTIMIZE to compact, VACUUM to reclaim — and never VACUUM below a framed Direct Lake commit

**Status:** Primary diagnostic — when a Delta table is slow or a Direct Lake model errors after maintenance, check the OPTIMIZE/VACUUM cadence first. The 7-day VACUUM floor is an **absolute rule**.

**Domain:** Delta maintenance / lakehouse

**Applies to:** `microsoft-fabric`

---

## Why this exists

`OPTIMIZE` (bin-compaction) and `VACUUM` solve **different** problems and people conflate them. `OPTIMIZE` merges many small Parquet files into fewer large ones — it tunes **reads**. `VACUUM` deletes unreferenced files older than a retention threshold — it reclaims **storage**, and on its own does nothing for query speed. The sharp edge: a **framed Direct Lake** semantic model pins a *specific Delta commit version*, and if `VACUUM` removes the Parquet files that version still references, queries **error** ("files no longer exist") until you reframe. That is why the default 7-day retention exists and why dropping below it is dangerous: small-file proliferation from streaming/CDC tempts people to over-VACUUM, and they take down a Direct Lake report doing it.

## How to apply

Run each command for its purpose, on the right cadence, and respect the floor.

```sql
-- Compact + apply V-Order on a gold table (tunes reads). Run after large ingestion
-- or when small files accumulate. Optimize INFREQUENTLY for Direct Lake — each
-- OPTIMIZE rewrites Parquet, invalidates VertiPaq segments, forces a cold retranscode.
OPTIMIZE gold.sales VORDER;

-- Reclaim storage. Default + safe retention is 7 days (168h). Keeps the last 7 days
-- of commits for time travel AND for any framed Direct Lake model pinned to them.
VACUUM gold.sales;                 -- uses the 7-day default
VACUUM gold.sales RETAIN 168 HOURS;-- explicit, same thing
```

- **Cadence:** `OPTIMIZE` after large batch ingestion or when small files pile up; for Direct Lake, **infrequently** (weekends / month-end) to avoid repeated cold retranscode — unless high-frequency small updates push the table toward the row-group/Parquet **guardrails**, then optimize daily-or-more. `VACUUM` on a regular weekly cadence after compaction.
- **`REORG TABLE … APPLY (PURGE)` is not routine** — `OPTIMIZE` auto-purges files where >5% of records are deletion-vector-referenced. Reserve `PURGE` for compliance/GDPR hard-deletes.
- **Before VACUUM-ing a Direct-Lake-served table:** reframe the model to the current commit *or* keep retention long enough that the framed commit's files survive.

**Do:**
- Treat `OPTIMIZE` and `VACUUM` as complementary, not interchangeable.
- Keep `VACUUM` retention at **≥ 7 days** (the default); it protects time travel *and* framed Direct Lake commits.
- Use partitioning by a **low-cardinality** date key to confine maintenance to a few partitions, preserving incremental framing.

**Don't:**
- `VACUUM … RETAIN 0 HOURS` (or any sub-7-day value) on a table a framed Direct Lake model reads — you will orphan the pinned commit and the report errors. (Fabric UI/API reject sub-7-day retention by default; overriding it needs `spark.databricks.delta.retentionDurationCheck.enabled=false` — a deliberate, documented act.)
- Expect `VACUUM` to speed up queries — that is `OPTIMIZE`'s job.
- `OPTIMIZE` a Direct-Lake table on every micro-batch — the cold-retranscode penalty outweighs the gain.

## Edge cases / when the rule does NOT apply

- **Sub-7-day retention for genuine storage/compliance pressure** is allowed *only* with the safety check disabled and *only* when no framed model or time-travel query needs the older commits — write down why.
- **Small Delta tables** don't need OPTIMIZE for incremental framing; the small-file problem is a large-table concern.
- **Streaming-into-lakehouse** tables need *frequent* OPTIMIZE to stay under guardrails — but the right home for true real-time is an Eventhouse, not a lakehouse Delta table.

## See also

- [`shape-gold-for-direct-lake.md`](./shape-gold-for-direct-lake.md) — V-Order + file/row-group targets `OPTIMIZE … VORDER` produces
- [`directlake-stay-under-guardrails.md`](./directlake-stay-under-guardrails.md) — the per-SKU Parquet/row-group guardrails OPTIMIZE keeps you under
- [`../knowledge/medallion-on-onelake.md`](../knowledge/medallion-on-onelake.md) — per-layer maintenance defaults
- [`../agents/lakehouse-engineer.md`](../agents/lakehouse-engineer.md) — owns Delta maintenance

## Provenance

Grounded in [Cross-workload table maintenance and optimization](https://learn.microsoft.com/fabric/fundamentals/table-maintenance-optimization), [VACUUM Delta tables](https://learn.microsoft.com/fabric/data-engineering/delta-lake-vacuum) (default retention 7 days / 168h), and [Understand Direct Lake query performance — Delta table maintenance](https://learn.microsoft.com/fabric/fundamentals/direct-lake-understand-storage) (framed model pins a commit; VACUUM that removes its files causes query errors) — Microsoft Learn, retrieved 2026-05-30. Supports house opinions #3/#4/#13.

---

_Last reviewed: 2026-05-30 by `claude`_
