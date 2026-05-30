# Streaming and telemetry belong in an Eventhouse — don't force real-time into a lakehouse Delta table

**Status:** Pattern — Eventhouse/KQL DB is the strong default for data-in-motion (streaming, telemetry, logs, time-series); streaming into a lakehouse Delta table is the documented wrong-store anti-pattern (house opinion #2).

**Domain:** Real-Time Intelligence / store selection

**Applies to:** `microsoft-fabric`

---

## Why this exists

People reach for a lakehouse for everything because it's the general-purpose store — but **streaming into a lakehouse Delta table fights the format**. High-rate ingest produces a flood of tiny Parquet files, forcing *frequent* `OPTIMIZE` just to stay under guardrails, and Delta isn't auto-indexed or time-partitioned for the low-latency, high-granularity interactive queries telemetry needs. An **Eventhouse / KQL DB** is purpose-built for this: auto-index, partition-by-time, autoscale on usage, and KQL's windowing/`make-series`/anomaly operators run *in place*. The store-selection tree puts streaming on the Eventhouse branch for exactly this reason. If historical batch analytics *also* need the data, route the eventstream to a Lakehouse **in addition** — but the real-time home is the Eventhouse.

## How to apply

Send the right access pattern to the right store; route to a lakehouse only for the historical/batch tail.

```text
Streaming / telemetry / logs / time-series, low-latency interactive  → EVENTHOUSE / KQL DB.
   Eventstream  → Eventhouse (KQL DB)  → KQL queryset / Real-Time dashboard / Activator
                              └─(also)→ Lakehouse, when historical batch analytics need it.
Batch, structured, SQL/Spark medallion                                → Lakehouse / Warehouse.
```

- **Confirm it's data-in-motion** before choosing RTI — streaming/telemetry/log/high-granularity-interactive → Eventhouse; if it's batch, hand to `data-factory-engineer` / `lakehouse-engineer`.
- **Eventstream is the no-code low-latency path** (also does CDC initial-snapshot and content-based routing) — the only no-code streaming ingestion.
- **Route to a Lakehouse as well** when you need the historical tail for batch/ML — Eventhouse for the live view, Lakehouse for the long history.
- **An alert without an action is a missed alert** — wire **Activator** to turn a detected pattern into a Teams alert / Power Automate / pipeline trigger.
- **Mind cost:** KQL DB autoscales and bills on active vCore-seconds; all KQL ops are interactive — see [`capacity-isolate-noisy-workloads.md`](./capacity-isolate-noisy-workloads.md).

**Do:**
- Put streaming/telemetry/logs in an Eventhouse/KQL DB; query with KQL, detect anomalies in place.
- Route the eventstream to a Lakehouse *additionally* for historical batch analytics.
- Wire Activator so a real-time condition fires an action.

**Don't:**
- Stream high-rate data into a lakehouse Delta table — you'll fight small-file proliferation and miss auto-index/time-partition.
- Choose the store by habit ("we use the lakehouse for everything") — traverse the store tree (house opinion #2).

## Edge cases / when the rule does NOT apply

- **Low-frequency, batch-shaped "events"** (a nightly log file) aren't real-time — a lakehouse load is fine; Eventhouse is for genuine data-in-motion.
- **A lakehouse table needs the historical copy** — that's the *additional* route, not a replacement for the Eventhouse live view.
- **Eventhouse OneLake availability** lets KQL data appear as Delta in OneLake — so "Eventhouse vs Lakehouse" isn't always either/or; the live query engine is still KQL.

## See also

- [`rti-shape-at-ingest-with-update-policies.md`](./rti-shape-at-ingest-with-update-policies.md) — update policies + materialized views inside the Eventhouse
- [`../knowledge/fabric-store-decision-tree.md`](../knowledge/fabric-store-decision-tree.md) — the streaming → Eventhouse branch
- [`../knowledge/fabric-decision-trees.md`](../knowledge/fabric-decision-trees.md) — lakehouse vs warehouse vs KQL DB; which-ingestion trees
- [`../agents/realtime-intelligence-engineer.md`](../agents/realtime-intelligence-engineer.md) · [`../agents/fabric-architect.md`](../agents/fabric-architect.md)

## Provenance

Codifies house opinion #2 (pick the store from the tree) from [`../CLAUDE.md`](../CLAUDE.md) §3, grounded in [Choose the right data store](https://learn.microsoft.com/fabric/fundamentals/decision-guide-data-store) (Eventhouse/KQL DB for streaming/telemetry/time-series, auto-index + time-partition), [Real-Time Intelligence overview](https://learn.microsoft.com/fabric/real-time-intelligence/overview), and [Eventhouse OneLake availability](https://learn.microsoft.com/fabric/real-time-intelligence/event-house-onelake-availability) — Microsoft Learn, retrieved 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
