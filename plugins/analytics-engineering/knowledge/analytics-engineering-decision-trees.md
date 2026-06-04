# Analytics Engineering — Decision Trees

_Decision trees + a dated capability map. Capability rows are `[verify-at-build]` — re-check against the vendor before quoting. Last reviewed: 2026-06-04._

Traverse before choosing a materialization or a model layer.

## Decision Tree: dbt materialization choice

Match the materialization to read frequency, size, and rebuild cost.

```mermaid
graph TD
  A[A dbt model] --> B{Large fact, mostly appends?}
  B -- Yes --> C{Reliable unique key + load window?}
  C -- Yes --> D[Incremental]
  C -- No --> E[Table - fix the key before going incremental]
  B -- No --> F{Read often / needs fast query?}
  F -- Yes --> G[Table]
  F -- No, cheap or rarely read --> H{Light logic on one source?}
  H -- Yes --> I[View]
  H -- No --> G
```

_A broken incremental silently drops/dups rows — only go incremental with a reliable unique key._

## Decision Tree: Which model layer does this belong in?

Keep transformations layered; don't smear logic across one mega-model.

```mermaid
graph TD
  A[Some transformation] --> B{Cleaning/renaming/casting ONE source?}
  B -- Yes --> C[staging/]
  B -- No --> D{Business-facing fact/dimension a consumer queries?}
  D -- Yes --> E[marts/ - fct_/dim_]
  D -- No, composing/joining staging models for reuse --> F[intermediate/]
  C --> G[ref it downstream; never query raw sources outside staging]
```


## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| dbt Core / Cloud | GA | staging/intermediate/marts; tests; docs |
| dbt Semantic Layer / MetricFlow | GA | metrics-as-code; one definition |
| dbt model contracts | GA | enforce names/types at boundaries |
| Incremental strategies | GA (merge/insert_overwrite/append) | warehouse-dependent |
| Snowflake/BigQuery/Redshift/Databricks | GA | warehouse-neutral modeling; mind cost model |
| Source freshness | GA | gate stale data |
