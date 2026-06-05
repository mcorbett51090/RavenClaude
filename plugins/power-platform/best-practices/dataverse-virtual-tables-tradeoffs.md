# Use Virtual Tables Only When the Data Must Stay External

**Status:** Pattern
**Domain:** Dataverse / data modeling
**Applies to:** `power-platform`

---

## Why this exists

Virtual tables (virtual entities) expose external data in Dataverse without copying it — they look like native tables but every read goes live to an OData or custom data provider. The appeal is "no sync," but the cost is real: no offline cache, no native rollup/calculated columns, no Dataverse auditing, no cascade behavior, no FLS, no plug-in PreValidation stage, and query performance is entirely at the mercy of the external endpoint. Teams reach for virtual tables because they sound "clean," ship an app, and then discover the external endpoint throttles at 100 concurrent users, the query-folding is minimal, and every form load is a round-trip they cannot cache.

## How to apply

**Decision rule** — a virtual table is correct when ALL three hold:
1. The data must live in the external system (regulatory, contractual, or operational — it is not yours to copy).
2. The read volume is bounded (infrequent lookups, not a grid that pages thousands of rows).
3. The external system has a reliable, low-latency endpoint (SLA ≥ 99.9%, p99 < 200 ms).

Otherwise, copy to Dataverse (import, sync via flow, or Dataverse-native table) and own the data.

```
Checklist before recommending a virtual table:
[ ] Data must stay external — confirmed with the data owner
[ ] Row volume per session is bounded (< ~200 rows per user interaction)
[ ] External endpoint has documented SLA and latency budget
[ ] No need for: auditing, FLS, rollup/calculated columns, cascade, plug-in PreValidation
[ ] Licensing: virtual tables need a connector/data-provider license (custom providers need Premium)
```

**Do:**
- Use virtual tables for SAP / legacy mainframe data that is contractually immovable.
- Add a `Refresh` button so users know the data is live (not cached) and can re-fetch.
- Set an explicit timeout in the data provider and surface a user-friendly error on timeout.
- Place the virtual table in a separate solution from the rest of your data model.

**Don't:**
- Use virtual tables for data you could easily sync or import — you're trading a sync job for per-query latency on every user interaction.
- Expect FLS, auditing, cascade, or rollup columns to work — they don't on virtual tables.
- Expose a virtual table directly in a canvas gallery with no row limit or delegation guard.
- Add a virtual table to a grid/subgrid that loads on form open if the form has high concurrency.

## Edge cases / when the rule does NOT apply

- If the external system provides a dedicated Dataverse virtual-table connector (e.g., SAP OData, Finance and Operations) that has known performance characteristics and the data genuinely must not be duplicated, a virtual table is the sanctioned path — document the SLA and volume assumption.
- Read-only lookup controls (a single-row "view this record in SAP" button on a form) are low-risk virtual-table use cases even without the three-point checklist.

## See also

- [`../agents/dataverse-architect.md`](../agents/dataverse-architect.md) — owns the data-modeling decision including virtual vs native
- [`./dataverse-choice-vs-lookup-vs-customer-column.md`](./dataverse-choice-vs-lookup-vs-customer-column.md) — column-type decisions for native tables
- [`./dataverse-bulk-operations-and-throttling.md`](./dataverse-bulk-operations-and-throttling.md) — service-protection limits that also affect virtual-table backends

## Provenance

Codifies `dataverse-architect`'s pattern of asking "does this data need to stay external?" before recommending virtual tables, plus the documented limitations of the virtual-table infrastructure (no auditing, no FLS, no cascade, no rollup) per Microsoft Learn *Create and edit virtual tables* (May 2026).

---

_Last reviewed: 2026-06-05 by `claude`_
