# Shape streaming data at ingest with update policies and materialized views — don't reshape at query time

**Status:** Pattern — transforming on ingest (update policies) and pre-aggregating (materialized views) is the strong default in an Eventhouse; reshaping the same raw stream on every query is the slow, expensive path.

**Domain:** Real-Time Intelligence / Eventhouse / KQL

**Applies to:** `microsoft-fabric`

---

## Why this exists

In an Eventhouse, a high-rate raw stream (free-text traces, semi-structured events) is cheap to *ingest* but expensive to *re-parse on every query*. KQL gives you two ingest-time mechanisms that move the cost from read-time to write-time:

- **Update policies** — automation triggered when new data lands: run a transform query and write the result to a **target table** (different schema/retention/policies than the source). The classic case: a high-rate free-text source table whose update policy parses well-structured lines into a typed target — this is the streaming analogue of bronze→silver.
- **Materialized views** — pre-aggregate (e.g. hourly rollups, `take_any` dedup) so dashboards read the *materialized part* instead of scanning raw extents.

Both consume CPU (they're a real cost driver), but they pay back many-fold when the alternative is every dashboard tile re-aggregating raw data. This is the RTI version of "shape gold, don't serve bronze."

## How to apply

Parse/route on ingest with update policies; pre-aggregate hot dashboard queries with materialized views.

```kusto
// Update policy: parse raw free-text into a typed target table on ingest (bronze→silver, streaming).
.alter table TracesParsed policy update
```[{ "IsEnabled": true, "Source": "TracesRaw", "Query": "TracesRaw | parse Message with ... | project Timestamp, Level, Code", "IsTransactional": true }]```

// Materialized view: pre-aggregate so dashboards read the materialized part, not raw extents.
.create materialized-view HourlyErrors on table TracesParsed { TracesParsed | summarize count() by bin(Timestamp,1h), Code }
```

- **Source and target must be in the same database**; the update-policy function schema must **match the target column types and order**.
- **Set retention per table/view** — the target table and the MV each have their own retention policy; keep raw source retention at least a few days with recoverability for replay (MV doesn't support zero-retention source).
- **Detect in place** — run anomaly detection (`series_decompose_anomalies`, `make-series`) against live KQL, don't export to detect (RTI house opinion).

**Do:**
- Parse/route raw streams into typed target tables with **update policies** at ingest.
- Pre-aggregate hot dashboard/alert queries with **materialized views**.
- Set retention deliberately per table/MV; keep raw retention long enough to replay.

**Don't:**
- Re-parse a free-text source on every query when an update policy could type it once at ingest.
- Point every dashboard tile at raw extents when a materialized view would serve the rollup.
- Set zero retention on a source table feeding a materialized view — it's unsupported.

## Edge cases / when the rule does NOT apply

- **Truly ad-hoc exploratory KQL** over raw data doesn't need an MV — MVs are for *known, repeated* aggregations.
- **Low-rate streams** may not justify the update-policy CPU — measure; these are real cost drivers.
- **Batch, not streaming** — if it isn't data-in-motion, it's a lakehouse/warehouse medallion concern, not an Eventhouse one (hand to `lakehouse-engineer`).

## See also

- [`rti-eventhouse-for-streaming-not-lakehouse.md`](./rti-eventhouse-for-streaming-not-lakehouse.md) — when streaming belongs in an Eventhouse at all
- [`../knowledge/fabric-store-decision-tree.md`](../knowledge/fabric-store-decision-tree.md) — Eventhouse/KQL DB as the streaming store
- [`lakehouse-medallion-layer-boundaries.md`](./lakehouse-medallion-layer-boundaries.md) — the medallion analogy (update policies are the KQL bronze→silver)
- [`../agents/realtime-intelligence-engineer.md`](../agents/realtime-intelligence-engineer.md)

## Provenance

Grounded in [Update policy overview](https://learn.microsoft.com/kusto/management/update-policy?view=microsoft-fabric) (triggered on ingest; transform to target table; same database; schema must match), [Materialized views](https://learn.microsoft.com/fabric/real-time-intelligence/materialized-view) + [materialized-view policies](https://learn.microsoft.com/kusto/management/materialized-views/materialized-view-policies?view=microsoft-fabric) (own retention/caching; non-zero source retention required), [Retention policy](https://learn.microsoft.com/kusto/management/retention-policy?view=microsoft-fabric), and [Eventhouse cost drivers](https://learn.microsoft.com/fabric/real-time-intelligence/pricing-cost-drivers) (update policies/MVs/partitioning are CPU cost drivers that improve efficiency) — Microsoft Learn, retrieved 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
