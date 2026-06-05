---
scenario_id: 2026-06-05-server-to-cloud-extract-refresh-deadend
contributed_at: 2026-06-05
plugin: tableau
product: tableau-cloud
product_version: "Migration SDK 2025.x; Tableau Cloud 2025.2"
scope: version-specific
tags: [server-to-cloud, migration-sdk, content-migration-tool, extracts, tableau-bridge, refresh-schedule]
confidence: medium
reviewed: false
---

## Problem

A Server→Cloud migration "succeeded" — workbooks rendered in Tableau Cloud — but every
**extract refresh failed** the next morning, and several published data sources were stuck at
the migration-day snapshot. The content moved; the **refresh pipeline didn't**, because the
extracts were embedded in workbooks and the on-prem source had no path to Cloud.

## Permissions context

- Site admin on both the source Server site and the target Cloud site.
- The on-prem data sources sat behind the corporate firewall — Tableau Cloud cannot reach them
  directly; a refresh path requires **Tableau Bridge**.
- Advanced Management / licensing posture for the chosen tooling was assumed, not verified up
  front (this bit us — see Attempts).

## Attempts

- Tried: **Content Migration Tool (CMT)** as the primary Server→Cloud mover → wrong tool for
  this direction. Tableau's own guidance is that **CMT is not recommended for Server→Cloud
  migration; use the Tableau Migration SDK** for that path `[verify-at-build]`. CMT is for
  site-to-site / project-to-project content management.
- Tried: letting embedded extracts refresh on Cloud directly → they can't. **Tableau Bridge
  only refreshes *separately published* data sources**, not extracts embedded inside a workbook.
- Tried: re-pointing connections by hand after migration → drifted connection strings and
  partially worked, but it's the hand-republish anti-pattern (breaks the audit chain) and didn't
  scale past a handful of workbooks.
- **Worked:** (1) use the **Migration SDK** for the Server→Cloud move; (2) as part of the
  migration, **separate embedded extracts into published data sources** (the SDK / CMT
  transformation that converts embedded → published connections); (3) attach **Tableau Bridge**
  to those published data sources and schedule the refresh on Cloud.

## Resolution

**Server→Cloud is a Migration SDK job, and the refresh path is Bridge over *published* data
sources — separate the extracts before you migrate, not after.** Leaf in
[`../knowledge/governance-embedding-decision-trees.md`](../knowledge/governance-embedding-decision-trees.md)
(*Content promotion* tree) + the freshness-pipeline trees in
[`../knowledge/data-freshness-pipeline-decision-trees.md`](../knowledge/data-freshness-pipeline-decision-trees.md)
+ the [`/automate-content-promotion`](../commands/automate-content-promotion.md) command.
Durable lessons:

- **Pick the migration tool by *direction*, not by familiarity.** Site↔site / project
  reorganization → Content Migration Tool. Server→Cloud → **Migration SDK**. Reaching for CMT
  on a Server→Cloud move is the canonical dead-end here. `[verify-at-build]` the current
  tool-selection guidance — Tableau has shifted this recommendation.
- **"The workbooks render" is not "the migration is done."** The refresh pipeline is a separate,
  silently-failing surface. A migration's definition-of-done includes *a successful scheduled
  refresh of every published data source on the target*, verified the next cycle.
- **Embedded extracts have no Cloud refresh path** — convert them to **published** data sources
  and put them behind **Tableau Bridge** for any on-prem source. Also re-check what CMT/SDK
  does **not** carry: **embedded credentials, subscriptions, and custom views** migrate manually
  `[verify-at-build]`.

Cross-reference: the operational complement is the *Content promotion* decision tree and the
content-promotion runbook skill; this note surfaces the *symptom* (renders fine, refresh dies)
so the next engagement plans the refresh path and the tool choice up front.

**Sources (verified 2026-06-05):**
- [Pre-Migration Checklist — Tableau Migration SDK](https://help.tableau.com/current/api/migration_sdk/en-us/docs/how_to_migrate.html)
- [Migration Limitations — Tableau Content Migration Tool](https://help.tableau.com/current/server/en-us/cmt-migration_limitations.htm)
- [Using Tableau Bridge with Content Migration Tool — Salesforce Help](https://help.salesforce.com/s/articleView?id=001458678&type=1)
