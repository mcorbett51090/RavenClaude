# Pre-aggregate recurring high-frequency KQL patterns into materialized views before optimizing raw queries

**Status:** Pattern
**Domain:** Real-Time Intelligence / Eventhouse
**Applies to:** `microsoft-fabric`

---

## Why this exists

In an Eventhouse, a KQL query that re-parses and re-aggregates a raw high-rate stream on every dashboard refresh is the single most common cause of hot-cache exhaustion and capacity burst. A materialized view pre-aggregates the stream continuously in the background — queries against the view hit the pre-computed result set instead of the raw table, slashing CPU and memory per query by an order of magnitude on common aggregations. Engineers who optimize the raw query (add filters, tune `project`, split the pipeline) get diminishing returns when the structural problem is that the aggregation is being recomputed on every render.

## How to apply

Identify candidates: any KQL query that appears on a dashboard at < 5-minute refresh AND applies the same `summarize` (count, avg, percentile, min, max, dcount) to the same raw table.

```kusto
// Instead of this on every dashboard tick:
RawEvents
| where EventType == "Sensor"
| summarize AvgTemp = avg(Temperature) by bin(Timestamp, 1h), DeviceId

// Create a materialized view:
.create materialized-view with (backfill=true) HourlySensorAvg on table RawEvents
{
    RawEvents
    | summarize AvgTemp = avg(Temperature) by bin(Timestamp, 1h), DeviceId
}

// Dashboard query becomes:
HourlySensorAvg
| where Timestamp > ago(24h)
```

**Do:**
- Use `backfill=true` on creation to populate historical data — without it the view starts empty and only covers data ingested after creation.
- Pair the materialized view with a **retention policy** on the raw table: once the view covers the historical window, the raw table retention can be shorter.
- Monitor view materialization lag with `.show materialized-view HourlySensorAvg details` — a lag exceeding the refresh rate means the raw-ingest rate exceeds materialization throughput.

**Don't:**
- Create materialized views for queries that run infrequently (< once per hour) — the continuous pre-aggregation is wasted work if queries are rare.
- Use `dcount` in a materialized view over very high cardinality columns — `hll()` + `dcount_hll()` is the approximation-aware alternative.
- Assume a materialized view automatically replaces the raw query — update dashboards and reports to point at the view.

## Edge cases / when the rule does NOT apply

For ad-hoc forensic queries (incident response, one-time analysis) that run once, raw query optimization is appropriate. Do not create a materialized view for a one-time query shape.

## See also

- [`../agents/realtime-intelligence-engineer.md`](../agents/realtime-intelligence-engineer.md) — owns Eventhouse / KQL design
- [`./rti-shape-at-ingest-with-update-policies.md`](./rti-shape-at-ingest-with-update-policies.md) — the complementary pattern for shaping data at ingest time

## Provenance

Codifies the Eventhouse performance principle from CLAUDE.md §3 #3 ("medallion or justify its absence") applied to the KQL surface; Microsoft Learn Fabric materialized-views documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
