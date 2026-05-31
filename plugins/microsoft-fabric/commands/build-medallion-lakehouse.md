---
description: Build a medallion lakehouse on OneLake — bronze raw/immutable, silver conformed, gold business-ready — with each layer's own write pattern, V-Order and file-shape tuned per layer, and gold shaped to the Direct Lake contract.
argument-hint: "[the source + consumer, e.g. 'sales data feeding a Direct Lake model']"
---

# Build a medallion lakehouse

You are running `/microsoft-fabric:build-medallion-lakehouse`. Build the bronze/silver/gold lakehouse for what the user described (`$ARGUMENTS`), following this plugin's `lakehouse-engineer` discipline — each layer keeps one job, and the optimization that helps one layer hurts another.

## When to use this

The store choice is Lakehouse (or Lakehouse+Warehouse) and you're building the Delta tables. If the store hasn't been chosen, run `/microsoft-fabric:design-fabric-topology` first. For a tiny throwaway POC a two-layer bronze→gold shape can be defensible — but write down that silver was deliberately skipped.

## Steps

1. **Keep the layer boundaries:** bronze = source-exact, append-only, immutable replay source; silver = cleansed/deduped/conformed; gold = aggregated/denormalized data products. Never build one "silver-gold" table that does both — you lose replayability and a clean star (`lakehouse-medallion-layer-boundaries.md`).
2. **Shortcut bronze when the source already lives in OneLake/ADLS/S3/GCS** rather than copying it in (`one-copy-shortcut-before-copying.md`).
3. **Match V-Order and file shape to the layer:** no V-Order on bronze (pure write overhead); V-Order required on gold for Direct Lake, 400 MB–1 GB files, 8M+ row groups (`shape-gold-for-direct-lake.md`). Never serve bronze to Direct Lake or the SQL endpoint.
4. **Use the Native Execution Engine** (Runtime 1.3/2.0) for the Spark transforms — the biggest free perf/cost win; autotune is the dead Runtime-1.2 path, don't use it (`shape-gold-for-direct-lake.md`, house opinion #11).
5. **Build gold with a materialized lake view** when you want declarative refresh — Direct Lake on OneLake can build on an MLV, not a non-materialized SQL view (`shape-gold-for-direct-lake.md`).
6. **Shape gold as a star** — facts + conformed dimensions, not one wide flat table — so VertiPaq compresses well and Direct Lake builds join indexes (`semantic-star-schema-over-flat.md`). Use the `templates/medallion-lakehouse-spec.md` shape.

## Guardrails

- Never mutate bronze in place — a corrected source row is a new bronze append + a silver re-derivation, not an `UPDATE` on raw.
- Never put V-Order on bronze, leave it off a gold table Direct Lake reads, or point Direct Lake on OneLake at a non-materialized SQL view.
- This plugin is advisory: emit the PySpark / T-SQL / `fab` snippets the consultant runs in their own tenant. The DAX/measure layer routes to `power-platform/power-bi-engineer`.
