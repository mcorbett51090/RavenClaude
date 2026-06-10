# DAX Patterns and Performance

> **The deep reference for measure *correctness* is [`../../../knowledge/dax-measure-accuracy.md`](../../../knowledge/dax-measure-accuracy.md)** — read it before authoring or reviewing any non-trivial measure. It covers evaluation context + context transition, the CALCULATE filter modifiers (KEEPFILTERS / ALL / ALLEXCEPT / ALLSELECTED / REMOVEFILTERS), VAR semantics, DIVIDE/BLANK, time intelligence, relationships, calculation groups, validation, the AI-DAX failure catalogue, a wrong→correct rewrite table, and a paste-ready accuracy checklist. This file is the short performance-oriented companion.

## Core principles

- **Put business logic in measures**, not duplicated across visuals or calculated columns. (On Direct Lake, push row-level derivation to the gold Delta table — see [`../../../../microsoft-fabric/knowledge/dax-measures-for-direct-lake.md`](../../../../microsoft-fabric/knowledge/dax-measures-for-direct-lake.md).)
- **Use `DIVIDE`, not `/`** — safe on zero/blank denominators and better-optimized than an `IF` guard.
- **Prefer a boolean column predicate over `FILTER(table)`** as a `CALCULATE` filter argument — it lets the engine push a column filter instead of materializing the whole table. Use `FILTER` only for genuine multi-column / measure-based row logic; wrap in `KEEPFILTERS` when you need intersect-not-replace.
- **Prefer variables (`VAR`)** for readability and to compute a sub-expression once — but remember a variable is a *constant* evaluated at its definition site (it does not recompute inside a later `CALCULATE`). See the deep file's §VAR semantics.
- **Avoid unnecessary context transition** — a measure reference inside a high-cardinality iterator transitions per row; sometimes required, often a hidden cost.
- **Use calculation groups** (via Tabular Editor) for measure families (time intelligence, currency conversion) instead of authoring N base × M variant measures — collapses the explosion and keeps the logic in one place.

## Performance tools

- **DAX Studio** — query plan, server timings, VertiPaq Analyzer; capture the visual's query from Performance Analyzer and run/modify it safely.
- **Tabular Editor** — Best Practice Analyzer, calculation groups, scripting; TE3 has a real DAX Debugger (step execution with visible filter context).
- **Performance Analyzer** in Power BI Desktop; the **DAX query view** for `EVALUATE`.
- **XMLA endpoint** for advanced diagnostics on large models; **`EVALUATEANDLOG`** for block-level inspection.

## Common patterns

- **Time intelligence** with a proper marked + contiguous date table (`TOTALYTD`, `SAMEPERIODLASTYEAR`, `DATEADD` — mind the contiguous-range requirement; see the deep file's §Time intelligence).
- **Role-playing dimensions** via `USERELATIONSHIP` (inactive relationships) or calculation groups; **`CROSSFILTER`** to change direction, not to activate a relationship.
- **Dynamic measures** with field parameters or calculation groups.
- **Incremental refresh + partitioning** for large Import fact tables.

## Validation

Test a measure against the live model with `EVALUATE SUMMARIZECOLUMNS(...)` (or `DEFINE MEASURE … EVALUATE`) at the grain the visual uses — never trust a measure that only "looks right" in the editor. Verify any `Col = "literal"` filter matches real data with `EVALUATE SUMMARIZE(T, T[Col], "n", COUNTROWS(T))`. Full discipline + the AI-DAX guardrails in [`../../../knowledge/dax-measure-accuracy.md`](../../../knowledge/dax-measure-accuracy.md).

## When to escalate

- Very large models or complex composite-model scenarios → architecture review with `dataverse-architect` (if Dataverse is involved) or the broader team.
- The Fabric storage layer under a Direct Lake model (Delta tables, OneLake storage mode, framing, fallback) → `microsoft-fabric/fabric-semantic-model-engineer`.
