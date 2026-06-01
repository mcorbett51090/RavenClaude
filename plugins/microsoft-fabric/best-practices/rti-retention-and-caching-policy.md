# Eventhouse retention + caching policy — the first-order cost/latency lever in RTI

**Status:** Primary diagnostic — when an Eventhouse is over-budget on capacity or queries are slower/more-expensive than expected, check the caching (hot) and retention policies before tuning queries.

**Domain:** Real-Time Intelligence / cost & performance

**Applies to:** `microsoft-fabric`

---

## Why this exists

The two existing RTI rules cover *where* streaming data lands (`rti-eventhouse-for-streaming-not-lakehouse`) and *shaping at ingest* (`rti-shape-at-ingest-with-update-policies`) — but not the policy pair that most directly sets an Eventhouse's cost and query latency: **hot-cache** and **retention**. An Eventhouse (KQL database) keeps recent data in a hot cache (fast, memory/SSD-backed, billed) and older data in cold storage (cheaper, slower); retention controls when data is dropped entirely. Leave these at defaults and you either pay to hot-cache months of data nobody queries, or you under-cache the recent window every dashboard hits. This is the RTI equivalent of right-sizing storage mode — a first-order lever, not a micro-optimization.

## How to apply

**Set the caching (hot-window) policy to the actual query pattern.** Cache only the recent window queries actually touch — if 95% of queries hit the last 7 days, hot-cache 7–14 days, not 90.

```kql
.alter database MyEventhouse policy caching hot = 14d
.alter table Telemetry policy caching hot = 7d   // per-table override for a hot table
```

**Set retention to the real keep-requirement** (compliance + analytical need), separately from cache:

```kql
.alter table Telemetry policy retention softdelete = 90d
```

**Separate the two concepts deliberately:** retention = *how long data exists*; caching = *how much of it is fast*. They're independent — you can retain 1 year but hot-cache only 14 days.

**Use materialized views / update policies for pre-aggregation** so dashboards query a small rollup, not the raw firehose — this cuts both hot-cache pressure and query cost (and pairs with the shape-at-ingest rule).

**Do:** size hot-cache to the query window; set retention to the keep-requirement; override per-table for skewed-hotness tables; pre-aggregate with materialized views; revisit when query patterns or cost change.

**Don't:** leave default retention/caching on a high-volume table and absorb the bill; conflate retention with caching; hot-cache data only batch/archival jobs read.

## Edge cases / when the rule does NOT apply

A low-volume Eventhouse (small telemetry, dev) may never need tuning — defaults are fine until cost or latency says otherwise. Data that must be queried fast for its *entire* retention (rare, e.g. a regulatory always-hot requirement) legitimately hot-caches the full window — make it a conscious, costed choice. Exact policy syntax, default windows, and the cache-billing model are version-sensitive — `[verify-at-build]`.

## See also

- [`./rti-eventhouse-for-streaming-not-lakehouse.md`](./rti-eventhouse-for-streaming-not-lakehouse.md) — why streaming lands in an Eventhouse at all
- [`./rti-shape-at-ingest-with-update-policies.md`](./rti-shape-at-ingest-with-update-policies.md) — update policies + materialized views that reduce hot-cache pressure
- [`../agents/realtime-intelligence-engineer.md`](../agents/realtime-intelligence-engineer.md) — owns RTI
- [Kusto/Eventhouse caching & retention policies](https://learn.microsoft.com/fabric/real-time-intelligence/) — authoritative

## Provenance

Surfaced by the two-panel + tiebreak coverage campaign (2026-06-01): two RTI rules existed but neither covered hot-cache/retention — a first-order Eventhouse cost/perf lever absent from both the rules and the agent. (Note: the proposed RTI *alerting* tree was CUT by Panel 3 — the Activator condition→action flow is already agent prose with no real branch; this retention/caching BP is the kept RTI item.) Grounded in Kusto policy docs. Syntax + defaults are `[verify-at-build]`.

---

_Last reviewed: 2026-06-01 by `claude`_
