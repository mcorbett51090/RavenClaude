# Extract by default; choose live only against a named freshness requirement

**Status:** Pattern — a Hyper extract is the strong default; a live connection is the deviation you justify with a written freshness need.

**Domain:** Data modeling / Performance

**Applies to:** `tableau`

---

## Why this exists

A live connection re-queries the underlying source on every viz interaction, so a dashboard's responsiveness is hostage to a transactional database's query planner, its current load, and the network round-trip. A **Hyper extract** is a columnar, compressed, in-memory snapshot purpose-built for analytic queries — for the overwhelming majority of dashboards it is faster, cheaper on the source system, and unaffected by OLTP contention. Teams reach for live "to be safe" or "in case someone needs it fresh," and then pay query latency on every click for a freshness no stakeholder actually asked for. The discipline is to **name the freshness requirement** out loud: if you cannot state, in observable terms, why the data must be live, the answer is an extract.

## How to apply

State the freshness requirement first; let it pick the connection mode.

```
Default ............. EXTRACT (Hyper)        most dashboards; refresh on a schedule that meets the SLA
Go LIVE only if one of these is TRUE:
  • Operational / sub-minute   "the ops desk needs rows seconds old" (call-center queue, fraud)
  • Governance / no-copy        source PII must not be duplicated into an extract (legal/PII policy)
  • Source-enforced RLS         row security lives in the DB and an extract would bypass it
  • Extract-too-large           data volume genuinely exceeds the extract path's practical ceiling
Otherwise → EXTRACT, and set the refresh cadence to the stated SLA (e.g. hourly, 6×/day, nightly).
```

```
EXAMPLE — "sales dashboard, data must be current as of this morning"
  Freshness requirement: "yesterday's close, refreshed before 7am" → NOT sub-minute.
  Decision: EXTRACT, scheduled refresh 06:00 daily. Live would pay query latency all day
  for a freshness the requirement does not need.

EXAMPLE — "live call-queue monitor"
  Freshness requirement: "agents act on calls < 30s old" → genuinely sub-minute.
  Decision: LIVE to the operational store (or a streaming source). An extract cannot meet 30s.
```

**Do:**
- Write the freshness requirement as an observable sentence before choosing the mode.
- Default to an extract and set its **refresh schedule** to exactly the stated SLA — no tighter.
- Use live for sub-minute operational data, no-copy governance, or source-enforced RLS only.

**Don't:**
- Choose live because "they might want it fresh" — that is not a requirement.
- Run an extract refresh every 15 minutes to *simulate* live; if you need that, you needed live (or you over-stated the SLA).
- Forget that a live connection inherits the source's slow query — Tableau cannot out-tune a bad upstream view.

## Edge cases / when the rule does NOT apply

- **Initial data discovery / one-off analysis** — connecting live while exploring is fine; create the extract before you publish.
- **Already-fast star schema / cloud warehouse** — a well-modeled Snowflake/BigQuery source with result caching can serve a live connection acceptably; extract still usually wins, but the gap narrows. Measure rather than assume `[verify-at-build]`.
- **Write-back / parameterized actions** that must reflect a change immediately may need live for that surface.
- **Extract refresh windows that can't meet the SLA** — if the data is too large to refresh inside the freshness window, that is itself a reason to go live (or to redesign the extract with incremental refresh).

## See also

- [`./data-relationships-before-joins.md`](./data-relationships-before-joins.md) — the model that sits under either connection mode
- [`./data-extract-optimization.md`](./data-extract-optimization.md) — once you've chosen extract, shape it
- [`../knowledge/data-performance-decision-trees.md`](../knowledge/data-performance-decision-trees.md) — `## Decision Tree: Connection mode — extract vs live`
- [`../agents/tableau-data-architect.md`](../agents/tableau-data-architect.md) — the agent that owns this rule
- Tableau Help, "Extract your data" and "When to use a live vs. extract connection" `[verify-at-build]`

## Provenance

Codifies constitution house opinion #4 ("Extract by default for performance; live only when freshness demands it"). Hyper is Tableau's in-memory columnar data engine; its exact size/performance ceilings are version-sensitive and should be re-verified against current Tableau Help before quoting a hard limit to a client.

---

_Last reviewed: 2026-05-30 by `claude`_
