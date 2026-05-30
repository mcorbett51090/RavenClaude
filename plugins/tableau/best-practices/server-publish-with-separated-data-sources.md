# Publish data sources separately from workbooks; don't embed an extract per workbook

**Status:** Pattern — separated published data sources are the strong default; an embedded per-workbook extract is the deviation you justify.

**Domain:** Server / ALM

**Applies to:** `tableau`

---

## Why this exists

When a workbook embeds its own extract, the data model, the extract refresh, and the connection string all live *inside the workbook file*. Promote that workbook and you drag a dev connection into prod; refresh it and you refresh one copy while nine others go stale; fix a join and you fix it once and miss the rest. Separating the data source — publish it on its own, and have workbooks **connect to the published source** — decouples the three concerns: the data source has its own refresh schedule, its own connection (remapped cleanly per environment on promotion), and one model that every workbook inherits. This is the structural precondition for governed promotion and centralized RLS: you can't remap a connection that's baked into a `.twbx`, and you can't put RLS once on a source that's been copied into every workbook.

## How to apply

Publish the data source first; build workbooks against the *published* source, not raw tables.

```
# 1. Publish the data source by itself (with its model + extract refresh schedule):
#    Desktop: Data → <source> → Publish to Server…  (publishes the .tdsx)
#    or REST: POST /api/3.x/sites/{site-id}/datasources

# 2. Build/repoint the workbook to the PUBLISHED data source:
#    Desktop: Data → Replace Data Source → choose the published (Tableau Server) source
#    The workbook now carries only a REFERENCE, not an embedded copy.

# 3. Schedule the extract refresh on the DATA SOURCE (once), not per workbook:
POST /api/3.x/sites/{site-id}/schedules/{schedule-id}/datasources
{ "task": { "extractRefresh": { "datasource": { "id": "{datasource-id}" } } } }
#    → one refresh feeds every workbook built on it.
```

**Do:**
- Publish data sources **separately** and connect workbooks to the published source.
- Schedule extract refresh on the **data source**, once — every workbook on it inherits fresh data.
- Let the published data source own the connection so promotion can remap it cleanly per environment.
- Put the model (relationships, calcs, RLS) on the published source so workbooks inherit, not duplicate.

**Don't:**
- Embed a private extract per workbook for shared/governed content — it fragments refresh, model, and RLS.
- Schedule N refreshes for N workbooks that all read the same data — schedule one on the source.
- Bake a dev connection into a `.twbx` you intend to promote — it can't be remapped cleanly.

## Edge cases / when the rule does NOT apply

- **Personal / one-off workbooks** — a private embedded extract is fine for a sandbox that will never be shared or promoted.
- **Workbook-specific shaping** — a workbook may add local calcs on top of a published source; the *source* stays shared, the local additions stay local.
- **Live published sources** — separation applies to live connections too; the published live source is still the shared, remappable object.

## See also

- [`./server-promote-content-dont-rebuild.md`](./server-promote-content-dont-rebuild.md) — separated sources are what make connection remapping on promotion clean
- [`./gov-certified-data-sources-and-governance.md`](./gov-certified-data-sources-and-governance.md) — certify the separated published source
- [`./data-relationships-before-joins.md`](./data-relationships-before-joins.md) — model the source correctly before publishing it
- [`../agents/tableau-admin.md`](../agents/tableau-admin.md) — owns this rule
- Tableau Help, "Best practices for published data sources" `[verify-at-build]`

## Provenance

Codifies the `tableau-admin` discipline #4 ("Publish with separated, certified data sources"). Grounded in Tableau's published-data-source model and extract-refresh scheduling — re-verify REST endpoints and replace-data-source behavior against current Tableau Help.

---

_Last reviewed: 2026-05-30 by `claude`_
