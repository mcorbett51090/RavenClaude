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


## Decision Tree: Star schema or one-big-table for this mart?

Choose the mart shape by who queries it and how, not by dogma.

```mermaid
graph TD
  A[A business-facing mart] --> B{Consumer is a governed semantic layer / BI modeling tool?}
  B -- Yes --> C[Star schema: conformed fct_/dim_ - reuse dims, avoid drift]
  B -- No --> D{Many independent metrics sharing the same dimensions?}
  D -- Yes --> C
  D -- No, one denormalized analytical surface --> E{Query engine columnar + cost-OK with wide scans?}
  E -- Yes --> F[One-big-table: fewer joins, simpler for ad-hoc/notebook consumers]
  E -- No --> C
  C --> G[Conform dimensions once; never redefine a dim per mart]
  F --> H[Document the grain + accept update/storage cost of denormalization]
```

_Star schema buys reuse and conformed dimensions; OBT buys join-free simplicity. Name the trade; don't default to OBT to dodge dimensional modeling._

## Decision Tree: Is the source fresh enough to build?

Gate the build on freshness so stale or partial loads don't ship as complete.

```mermaid
graph TD
  A[Scheduled dbt run] --> B{Source freshness check passes within SLA?}
  B -- No, stale --> C{Source is a hard dependency for these marts?}
  C -- Yes --> D[Fail the build: error, alert - do NOT serve stale as current]
  C -- No, optional/lagging-ok --> E[Warn, build with last-known + flag staleness]
  B -- Yes --> F{Partial load detected row-count/watermark anomaly?}
  F -- Yes --> D
  F -- No --> G[Build proceeds]
```

_Freshness is the boundary check on ingestion (data-platform's lane): if upstream didn't deliver, fail loudly, don't fabricate a confident wrong answer._

## Decision Tree: Where should this metric be defined?

A metric belongs in the semantic layer once, not re-derived per dashboard.

```mermaid
graph TD
  A[A business metric e.g. revenue, active user] --> B{Already defined in the semantic/metrics layer?}
  B -- Yes --> C[Reference the governed definition - never re-derive in a mart or BI calc]
  B -- No --> D{Is it a reusable business KPI multiple consumers will use?}
  D -- Yes --> E[Define once as metrics-as-code: explicit grain + filters -> semantic-layer-engineer]
  D -- No, a one-off model-local aggregate --> F{Could it drift into a KPI later?}
  F -- Yes --> E
  F -- No --> G[Compute in the mart, document the grain]
  E --> H[Every BI tool consumes the one definition]
```

_The moment two dashboards compute the 'same' metric differently, trust in all of them is gone. Definition lives in the semantic layer; the mart provides the grain-correct base._

## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| dbt Core / Cloud | GA | staging/intermediate/marts; tests; docs |
| dbt Semantic Layer / MetricFlow | GA | metrics-as-code; one definition |
| dbt model contracts | GA | enforce names/types at boundaries |
| Incremental strategies | GA (merge/insert_overwrite/append) | warehouse-dependent |
| Snowflake/BigQuery/Redshift/Databricks | GA | warehouse-neutral modeling; mind cost model |
| Source freshness | GA | gate stale data |
