# Make ingestion incremental and idempotent — own the watermark, don't reload the world

**Status:** Pattern — incremental, idempotent loads with explicit watermark/control-table state are the strong default for pipeline-based ingestion; full reloads on every run are an anti-pattern outside small/initial loads.

**Domain:** Data Factory / ingestion / pipelines

**Applies to:** `microsoft-fabric`

---

## Why this exists

When the data-movement decision tree lands on **Copy job** or **Pipeline** (i.e. you're past Mirroring/auto-mirror and own the movement), the next failure mode is reloading the entire source on every run. Full reloads burn background CUs, lengthen the load window (which collides with framing and smoothing), and — if the pipeline retries or double-fires — duplicate rows. Two disciplines fix it: **incremental** (move only what changed since the last successful run, via a watermark) and **idempotent** (re-running the same load produces the same result, via MERGE-on-key rather than blind append). Copy job gives you native incremental + CDC without scaffolding; pipelines make you own the watermark state explicitly in a control table.

## How to apply

Prefer the lower-ceremony method; when you build a pipeline, own the watermark and write idempotently.

```text
Need incremental/CDC, no pipeline to build?  → COPY JOB (native watermark + CDC, 50+ connectors).
Need orchestration / control flow / code?     → PIPELINE: Lookup last watermark → Copy delta →
                                                 MERGE into target → update control table.
```

```sql
-- Idempotent target write: MERGE on the business key (re-runnable, no duplicates).
MERGE INTO bronze.orders t
USING staging.orders_delta s ON t.order_id = s.order_id
WHEN MATCHED THEN UPDATE SET ...
WHEN NOT MATCHED THEN INSERT ...;
```

- **Watermark in a control table** — `Lookup` the last successful high-water value, copy rows `> watermark`, then update the control table **only after** the load commits (so a failed run re-pulls the same delta).
- **MERGE on the business key**, not blind `INSERT` — re-runs and retries must not duplicate.
- **Schedule with smoothing in mind** — heavy loads are background CU consumers; ride the 24-h window, don't fire them into the interactive peak (see [`capacity-isolate-noisy-workloads.md`](./capacity-isolate-noisy-workloads.md)).
- **Reframe the Direct Lake model as the final step** if the load feeds one (see [`directlake-frame-deliberately.md`](./directlake-frame-deliberately.md)).

**Do:**
- Reach for **Copy job** before building a pipeline when you just need incremental/CDC.
- Persist watermark state in a control table; advance it only on success.
- Write to the target with MERGE-on-key so loads are idempotent.

**Don't:**
- Truncate-and-reload a large source every run — it wastes CUs and widens the load window.
- Blind-append without a key — retries and double-fires duplicate rows.
- Update the watermark before the load commits — a mid-load failure then skips data.

## Edge cases / when the rule does NOT apply

- **Initial / one-time backfill** is legitimately a full load — incremental starts on run two.
- **Mirroring / auto-mirror** already handle incremental/CDC for you — don't rebuild that as a pipeline (house opinion #1: prefer the earlier, lower-ceremony leaf).
- **Small reference/lookup tables** where a full reload is cheaper than tracking deltas — full refresh is fine; say so.

## See also

- [`../knowledge/fabric-data-movement-decision-tree.md`](../knowledge/fabric-data-movement-decision-tree.md) — the method choice (Mirroring/Copy job/pipeline/Dataflow/Eventstream)
- [`../knowledge/fabric-decision-trees.md`](../knowledge/fabric-decision-trees.md) — the ingestion-method decision tree
- [`one-copy-shortcut-before-copying.md`](./one-copy-shortcut-before-copying.md) — don't copy what a shortcut serves
- [`capacity-isolate-noisy-workloads.md`](./capacity-isolate-noisy-workloads.md) · [`directlake-frame-deliberately.md`](./directlake-frame-deliberately.md)
- [`../agents/data-factory-engineer.md`](../agents/data-factory-engineer.md)

## Provenance

Grounded in [Choose a data movement strategy](https://learn.microsoft.com/fabric/data-factory/decision-guide-data-movement) (Copy job native incremental + CDC; pipelines own incremental state via watermark + control table) and [Data Factory overview](https://learn.microsoft.com/fabric/data-factory/data-factory-overview) — Microsoft Learn, retrieved 2026-05-30. Supports house opinions #1 and #5.

---

_Last reviewed: 2026-05-30 by `claude`_
