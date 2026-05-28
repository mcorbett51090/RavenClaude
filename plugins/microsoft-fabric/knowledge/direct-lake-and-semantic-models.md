# Direct Lake & semantic models on Fabric

**Last reviewed:** 2026-05-28 · **Confidence:** high (first-party Microsoft Learn, retrieved 2026-05-28).
**Owner:** `fabric-semantic-model-engineer`.
**Source:** [Direct Lake overview](https://learn.microsoft.com/fabric/fundamentals/direct-lake-overview), [How Direct Lake works](https://learn.microsoft.com/fabric/fundamentals/direct-lake-how-it-works), [Power BI semantic models in Fabric](https://learn.microsoft.com/fabric/data-warehouse/semantic-models), [Direct Lake in Power BI Desktop](https://learn.microsoft.com/fabric/fundamentals/direct-lake-power-bi-desktop).

## What Direct Lake is

A Power BI semantic-model **storage mode** that loads Delta tables straight from OneLake into the VertiPaq engine **on demand** — Import-class query speed with DirectQuery-class freshness, **without copying data at refresh**. "Refresh" is metadata **framing** (seconds): it points the model at the latest committed Delta files. Data prep moves to OneLake (Spark, T-SQL, Dataflows, pipelines), not to a model refresh.

The three storage modes:

| Mode | How | Trade-off |
|---|---|---|
| **Import** | copies data into VertiPaq at refresh | fastest queries; stale between refreshes; refresh is heavy |
| **DirectQuery** | federates each query to the source | always fresh; slower; depends on source |
| **Direct Lake** | reads Delta from OneLake into VertiPaq on demand; refresh = framing | Import-class speed + near-real-time freshness, no copy |

## The two Direct Lake modes — get this right (it's the #1 mistake)

There are **two** Direct Lake variants and they behave differently on fallback:

### Direct Lake on OneLake (the modern default)
- Reads schema, security, and data **via OneLake APIs**.
- **Does NOT fall back to DirectQuery.** If a table isn't framed/processed, queries **error** rather than silently falling back. Supports **composite models** (mixing Direct Lake with Import/DQ tables).
- Created in Power BI Desktop via **OneLake catalog → pick a Lakehouse/Warehouse** → live editing in the workspace.
- Gotchas: results respect **OneLake security** (RLS/CLS) so a misconfigured role yields *empty* results, not an error; **no gateway support**; after a shortcut's underlying data changes you may need a **manual reframe**.

### Direct Lake on SQL (the older path)
- Reads through the **SQL analytics endpoint**.
- **Falls back to DirectQuery** when it exceeds SKU guardrails or hits an unsupported feature, so report users continue uninterrupted. **SQL-endpoint OLS/RLS forces the fallback** (or fails if fallback is disabled).

> **House opinion #8 (rewritten):** know which Direct Lake mode you're on. On-OneLake = no fallback, design so every gold table is framed and OneLake-security roles are correct; on-SQL = fallback-aware, design gold to stay under guardrails and avoid features that force DirectQuery.

## Designing gold tables for Direct Lake (the lakehouse-engineer seam)

- **V-Order required** on gold Delta tables; target **400 MB-1 GB** files, **8M+ row groups** (see [`medallion-on-onelake.md`](medallion-on-onelake.md)).
- Direct Lake on OneLake can build on a **materialized lake view**, **not** a non-materialized SQL view.
- Keep cardinality and column count disciplined — VertiPaq memory limits per SKU drive on-SQL fallback.

## Enterprise dev workflow
- **PBIP** (Power BI Project) + **TMDL** (Tabular Model Definition Language) make the model git-deployable; **live editing** in Power BI Desktop writes to the remote model in the workspace; **publish via Fabric Git integration**, not Desktop's Publish. ([Direct Lake in PBIP](https://learn.microsoft.com/fabric/fundamentals/direct-lake-power-bi-project))
- **DAX query view** + **TMDL view** work against Direct Lake models.

## The power-platform/power-bi-engineer seam

> *If the question is about a measure, a visual, or a `.pbix` → `power-platform/power-bi-engineer`. If it's about the Delta tables, the OneLake storage mode, or why Direct Lake fell back → this plugin.* `fabric-semantic-model-engineer` owns the Direct Lake model + framing + gold-table shaping with `lakehouse-engineer`; **DAX measure authoring escalates to `power-platform/power-bi-engineer`** (it owns the pbix-mcp and Import/DirectQuery report craft).
