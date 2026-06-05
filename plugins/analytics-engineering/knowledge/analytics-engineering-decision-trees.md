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

## Decision Tree: Data quality failure triage — what broke and where is the fix?

**When this applies:** a dbt test fails in CI or production, OR a stakeholder reports a wrong number on a dashboard. Observable inputs: which test failed (schema vs freshness vs row-count), which layer the failing model lives in, and whether the failure is structural (wrong type/null) or statistical (wrong count/value).

**Last verified:** 2026-06-05 against `skills/data-quality-tests/SKILL.md` (analytics-engineering plugin).

```mermaid
flowchart TD
    START[Data quality failure or wrong number report] --> Q1{Was a dbt test the signal?}
    Q1 -->|YES| Q2{Which test type failed?}
    Q1 -->|NO - stakeholder spotted it| NOTEST[Coverage gap - add the test first then treat as a caught failure]
    Q2 -->|not_null or unique on a mart column| UPSTREAM[Trace the null/dup to staging or source - fix at origin not in mart]
    Q2 -->|relationships - FK mismatch| FK[Check dim for missing keys - late-arriving dim or source-delete not propagated]
    Q2 -->|source freshness| FRESH[Source load is late or paused - escalate to data-platform/etl-pipeline-engineer]
    Q2 -->|row-count drift| DRIFT{Is the drift in staging or marts?}
    DRIFT -->|Staging has normal count - mart is off| LOGIC[Logic error in intermediate or mart SQL - diff against last good build]
    DRIFT -->|Staging count is also low| PARTIAL[Partial source load - replay from cursor - connector-incremental BP]
    UPSTREAM --> HALT[Halt mart build - do NOT override the value in the mart]
    FK --> HALT
    FRESH --> HALT
    LOGIC --> HALT
    PARTIAL --> HALT
    NOTEST --> ADDTEST[Add the test - re-run - then apply the correct fix from this tree]
```

**Rationale per leaf:**
- *NOTEST* — if no test caught it, the coverage is the defect; add the test before fixing the value so the next occurrence is caught automatically.
- *UPSTREAM* — a not_null or unique failure in a mart means the problem is in the source or staging clean; patching the mart value is the wrong fix layer.
- *FK* — late-arriving or deleted dimension keys are the most common FK failure; the fix is in the dim load cadence or the soft-delete handling, not in the fact.
- *FRESH* — a freshness failure is data-platform's lane (the load didn't complete); the transform layer should halt, not build on stale data.
- *LOGIC* — if staging is correct but the mart count is wrong, the error is in the transform SQL — diff the mart build against the last passing run to isolate the change.
- *PARTIAL* — if both staging and mart counts are low, the source load itself was partial; the fix is a connector replay, not a dbt fix.
- *HALT* — in all branches, halt the mart build (don't serve the wrong number) until the root cause is fixed upstream.

**Tradeoffs summary:**

| Failure class | Fix layer | Correct action | Wrong action |
|---|---|---|---|
| not_null / unique | Source or staging | Fix at origin, replay | Override in mart |
| FK relationships | Dim load / source | Fix dim, re-run | Left-join around the null |
| Source freshness | Ingestion (data-platform) | Halt build, escalate | Build on stale data |
| Row-count drift (staging OK) | Transform SQL | Diff + fix the logic | Re-run until it "looks right" |
| Row-count drift (staging low) | Source load | Connector replay | Full-refresh the fact |

---

## Decision Tree: Incremental model — which strategy for this warehouse?

**When this applies:** a model is being converted from `table` to `incremental`, or an existing incremental model is producing wrong results (duplicate rows, missing updates). Observable inputs: warehouse dialect, whether records can be updated after insert, and the availability of a reliable unique key.

**Last verified:** 2026-06-05 against dbt Core docs (v1.8) and warehouse-specific incremental strategy support.

```mermaid
flowchart TD
    START[Adding or debugging an incremental model] --> Q1{Can records be updated after initial insert?}
    Q1 -->|YES - updates and inserts| Q2{Warehouse?}
    Q1 -->|NO - append-only events| APPEND[strategy: append - no unique_key needed]
    Q2 -->|Snowflake or BigQuery| MERGE[strategy: merge - unique_key required]
    Q2 -->|Redshift| INSERT_OVR[strategy: insert_overwrite - partition-key required]
    Q2 -->|Postgres| DELETE_INSERT[strategy: delete+insert - unique_key required]
    Q2 -->|Databricks Delta| MERGE
    MERGE --> KEY{Is the unique_key reliable - no NULLs - no late-arriving changes to key columns?}
    DELETE_INSERT --> KEY
    INSERT_OVR --> PART{Is the partition key a date or int - compatible with insert_overwrite?}
    KEY -->|YES| SHIP[Ship the incremental model]
    KEY -->|NO| TABLE[Stay table-materialized - fix the key first]
    PART -->|YES| SHIP
    PART -->|NO| TABLE
    APPEND --> SHIP
```

**Rationale per leaf:**
- *APPEND* — append-only event logs (clicks, webhook events) never update rows; no unique_key dedup is needed and `append` is the fastest strategy.
- *MERGE* — the standard strategy on Snowflake/BigQuery/Databricks; deduplicates on the unique_key using a MERGE statement.
- *INSERT_OVR* — Redshift performs better with partition-based overwrite than row-level MERGE; the partition key must align with the query filter.
- *DELETE+INSERT* — Postgres doesn't support MERGE natively (pre-15); delete matching rows then re-insert is the correct approach.
- *TABLE* — if the unique_key has NULLs or key columns can change (making the merge key unreliable), stay on `table` until the key is fixed; a broken incremental silently drops or duplicates rows.

**Tradeoffs summary:**

| Strategy | Warehouse | Unique key required | Update support | Use when |
|---|---|---|---|---|
| append | All | No | No | Append-only event streams |
| merge | Snowflake/BigQuery/Databricks | Yes | Yes | Standard updatable fact |
| insert_overwrite | Redshift | No (partition key) | Partition-level | Redshift date-partitioned facts |
| delete+insert | Postgres | Yes | Yes | Postgres updatable fact |

---

## Decision Tree: Semantic layer tool — dbt Semantic Layer or Cube?

**When this applies:** a project needs a governed metrics layer and must choose between dbt Semantic Layer / MetricFlow and Cube. Observable inputs: whether the project already uses dbt, whether a custom query API / pre-aggregations / multi-source joins are needed, and whether the BI tools in use have native MetricFlow integration.

**Last verified:** 2026-06-05 against dbt Semantic Layer GA docs and Cube OSS v0.35 docs.

```mermaid
flowchart TD
    START[Need a governed metrics layer] --> Q1{Is dbt Core or dbt Cloud already the transform tool?}
    Q1 -->|YES| Q2{Do BI tools need native MetricFlow integration - dbt Semantic Layer SDK?}
    Q2 -->|YES - Looker / Tableau / Hex / Evidence| DBTSL[dbt Semantic Layer with MetricFlow - metrics live with the models]
    Q2 -->|NO or BI tools access via REST API| Q3{Need pre-aggregations / multi-source cross-joins / custom REST API?}
    Q3 -->|YES| CUBE[Cube OSS - richer query API + pre-agg cache + securityContext]
    Q3 -->|NO - simple measure aggregation is enough| DBTSL
    Q1 -->|NO - no dbt in the stack| CUBE
    CUBE --> BOTH{Is Cube being added on top of an existing dbt project?}
    BOTH -->|YES| NODUP[Cube reads from dbt marts - do NOT re-define measures in both tools]
    BOTH -->|NO| CUBEFULL[Cube owns the full semantic model]
```

**Rationale per leaf:**
- *DBTSL* — when dbt is already the transform layer and BI tools have MetricFlow integration, keeping the metric definition alongside the model (in `schema.yml`) is the lowest-friction governance path.
- *CUBE* — pre-aggregations, complex multi-source joins, and a custom REST API are Cube's differentiated capabilities; MetricFlow does not support pre-aggregation caching.
- *NODUP* — adding Cube on top of dbt means Cube reads from dbt marts; never redefine the same measure in both tools or the single-definition principle breaks immediately.
- *CUBEFULL* — without dbt, Cube owns the full semantic model from the warehouse tables up.

**Tradeoffs summary:**

| Tool | Pre-aggregation cache | BI integrations | Co-location with dbt models | Use when |
|---|---|---|---|---|
| dbt Semantic Layer / MetricFlow | No | Native SDK integrations | Yes (schema.yml) | dbt stack + SDK-native BI tools |
| Cube OSS | Yes | REST / GraphQL / SQL | Via mart refs | Need pre-agg, custom API, or no dbt |
| Both (Cube reads dbt marts) | Yes | REST / GraphQL | Partial | Existing dbt project needing pre-agg |

---

## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| dbt Core / Cloud | GA | staging/intermediate/marts; tests; docs |
| dbt Semantic Layer / MetricFlow | GA | metrics-as-code; one definition |
| dbt model contracts | GA | enforce names/types at boundaries |
| Incremental strategies | GA (merge/insert_overwrite/append) | warehouse-dependent |
| Snowflake/BigQuery/Redshift/Databricks | GA | warehouse-neutral modeling; mind cost model |
| Source freshness | GA | gate stale data |
