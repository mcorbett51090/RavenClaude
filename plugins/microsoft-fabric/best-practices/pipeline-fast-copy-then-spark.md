# Fast Copy to land, Spark to reshape — don't make the mashup engine do heavy transforms

**Status:** Pattern — Dataflow Gen2 **Fast Copy** for extract-load and Spark/notebooks for heavy reshaping is the strong default; pushing complex transforms through the standard mashup engine is the slow path.

**Domain:** Data Factory / Dataflow Gen2 / transforms

**Applies to:** `microsoft-fabric`

---

## Why this exists

Dataflow Gen2 is the low-code (300+ transforms) ingestion path, and its **Fast Copy** is **up to 13–21× faster** than Gen1 because it **bypasses the mashup engine** for extract-load. But Fast Copy only kicks in for steps that meet its prerequisites — any **folding-breaking transform forces a fallback to the standard mashup engine**, and you silently lose the speedup. The trap: an analyst adds a heavy reshape (a wide unpivot, a non-foldable custom column, a messy merge) in the same dataflow, Fast Copy disengages, and a load that should take minutes takes hours. The discipline is to keep dataflows to **foldable extract-load** so Fast Copy stays engaged, and route **heavy reshaping to Spark/notebooks** where it belongs.

## How to apply

Split the work: Fast-Copy-friendly extract-load in the dataflow, heavy reshape in Spark.

```text
Extract + foldable filter/select/typing (analyst-led)   → DATAFLOW GEN2 with Fast Copy.
Heavy reshape: wide unpivot, complex joins, custom code  → SPARK / NOTEBOOK (Native Execution Engine).
```

- **Keep transforms foldable** in the dataflow so Fast Copy stays on — push filters/projections to the source, avoid steps that break folding.
- **Verify Fast Copy engaged** — check the [Fast Copy prerequisites](https://learn.microsoft.com/fabric/data-factory/dataflows-gen2-fast-copy); a fallback to the standard engine is the signal a step broke folding.
- **Hand heavy reshaping to Spark** with the **Native Execution Engine** on (house opinion #11) — the biggest free Spark perf win — rather than forcing it through the mashup engine.
- **Treat Fast Copy as the default for ingestion**; reserve dataflows for analyst-led silver shaping, not for the gold transform pipeline.

**Do:**
- Use Dataflow Gen2 + Fast Copy for foldable extract-load.
- Move heavy/non-foldable reshaping to Spark/notebooks with NEE enabled.
- Confirm Fast Copy is actually engaged before trusting the speedup.

**Don't:**
- Pile a non-foldable reshape into a Fast-Copy dataflow — it falls back to the slow mashup engine.
- Use a dataflow as the engine for a heavy gold transform when Spark is the right tool.
- Recommend **autotune** (deprecated Runtime-1.2 path) for the Spark side — use the Native Execution Engine (house opinion #11; the anti-pattern hook flags autotune).

## Edge cases / when the rule does NOT apply

- **Small, simple loads** where the mashup engine is fast enough — Fast Copy's edge is on volume; don't over-engineer a tiny feed.
- **An analyst-owned silver layer** with light shaping is a legitimate Dataflow Gen2 home — the rule targets *heavy* reshaping, not all transforms.
- **Pure orchestration / control flow** is a pipeline concern, not a dataflow one (see [`pipeline-orchestrate-idempotent-watermarks.md`](./pipeline-orchestrate-idempotent-watermarks.md)).

## See also

- [`../knowledge/fabric-data-movement-decision-tree.md`](../knowledge/fabric-data-movement-decision-tree.md) — Fast Copy benchmarks + the method tree
- [`pipeline-orchestrate-idempotent-watermarks.md`](./pipeline-orchestrate-idempotent-watermarks.md) — incremental/idempotent ingestion state
- [`../knowledge/medallion-on-onelake.md`](../knowledge/medallion-on-onelake.md) — the three transform options (MLV / notebook / Dataflow Gen2)
- [`../agents/data-factory-engineer.md`](../agents/data-factory-engineer.md) · [`../agents/lakehouse-engineer.md`](../agents/lakehouse-engineer.md)

## Provenance

Grounded in [Choose a data transformation strategy](https://learn.microsoft.com/fabric/data-factory/decision-guide-data-transformation) (Fast Copy 13–21× faster, bypasses mashup engine), [Fast Copy in Dataflow Gen2](https://learn.microsoft.com/fabric/data-factory/dataflows-gen2-fast-copy) (prerequisites; folding-breaking steps fall back), and house opinion #11 (Native Execution Engine) from [`../CLAUDE.md`](../CLAUDE.md) §3 — Microsoft Learn, retrieved 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
