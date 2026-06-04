---
name: dbt-modeling
description: "Model in dbt across staging -> intermediate -> marts layers, choose materialization (view/table/incremental) by the trade, write correct incremental models (reliable unique key, is_incremental filter, late-data strategy), and keep it DRY with refs/sources/macros."
---

# dbt Modeling

## Layers
**staging** (1 model/source: rename, cast, light clean) -> **intermediate** (compose, business logic) -> **marts** (business-facing fct/dim). Don't collapse into one giant model.

## Materialization
| Use | Choice |
|---|---|
| cheap / rarely read | **view** |
| fast read, rebuild ok | **table** |
| large append-mostly fact | **incremental** |

## Incremental correctly
Reliable **unique key** + `is_incremental()` window filter + late-arriving-data strategy. A broken incremental silently drops/dups rows.

## DRY
`ref()`/`source()` for lineage; macros for repeated logic. Never copy-paste SQL.
