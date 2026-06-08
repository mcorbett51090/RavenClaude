# Choose the data store by scale, security depth, surface, and ALM — before any table is built

**Status:** Pattern — strong default; choosing the store is the most expensive decision to reverse, because moving data + rewriting every app/flow against a new source is a re-platform, not a refactor.
**Domain:** Data platform selection (upstream of Dataverse modeling)
**Applies to:** `power-platform`

---

## Why this exists

"Should this be Dataverse, Dataverse for Teams, a SharePoint list, or just Excel?" is the first question on most engagements, and the wrong answer compounds: a SharePoint list chosen for a transactional app hits delegation cliffs and the large-list threshold; a Dataverse-for-Teams app chosen for an enterprise scenario can't get auditing, field-level security, or multi-environment ALM; a full Dataverse environment chosen for a five-person Teams tracker burns premium licensing for capability nobody needs. Microsoft frames the choice across four question categories — **Data** (types + volume + search), **Application** (surface, guests, builder skill, special capabilities), **Integration**, and **Admin/governance** (security/compliance, backup/restore) ([Microsoft Learn, *Comparing Microsoft Lists, Dataverse for Teams, and Dataverse*](https://learn.microsoft.com/en-us/power-apps/teams/compare-data-sources), `updated_at 2025-05-07`, retrieved 2026-06-08). This rule makes those categories actionable and is the **upstream** of [`dataverse-decision-trees.md`](../knowledge/dataverse-decision-trees.md), which assumes Dataverse is already chosen.

## How to apply

Walk the axes; the first hard requirement that only one store satisfies decides it.

| Axis | Microsoft Lists / SharePoint | Dataverse for Teams | Dataverse (full) |
|---|---|---|---|
| **Data shape** | Flat lists (File, Image) | **Relational** | Relational + Lake, Log, Virtual tables, Dataverse Search |
| **Capacity** | Up to **30M rows** (>100k needs indexing) | Up to **~1M rows** / 2 GB per team | **No specified row limit** (+ capacity add-ons) |
| **Security depth** | Owners/Members/Visitors roles + custom permissions | Owner/Member/Guest + Entra-group app share | **Roles, business units, auditing, CMK, hierarchical + field-level security** |
| **Surfaces (clients)** | Lists, Teams, custom code | **Teams only** | Teams, Power Apps, **Power Pages, Dynamics 365**, custom code |
| **ALM** | Package & deploy Lists | **One unmanaged solution per environment** | **Unlimited** managed-solution ALM, multi-environment |
| **Pro-dev / integration** | REST + Graph API | none | REST, SDK, **plug-ins**, Event Hub/Service Bus/Webhook, Export-to-Lake, SQL (TDS) |
| **Extra logic** | Calculations & rollups | none | **Business rules, business workflows**, calc/rollups, mobile offline |

(All rows from the first-party Learn comparison page, retrieved 2026-06-08. ~1M-row / 2 GB-per-team capacity and the one-environment-per-team model corroborated by [*Dataverse for Teams vs. Dataverse*](https://learn.microsoft.com/en-us/power-apps/teams/data-platform-compare), retrieved 2026-06-08.)

**Do:**
- Pick **full Dataverse** the moment any of these is required: auditing, field-level/hierarchical security, business units, > ~1M rows, managed-solution multi-environment ALM, plug-ins, or a surface beyond Teams (Power Pages, model-driven, Dynamics 365). Only full Dataverse lists those.
- Pick **Dataverse for Teams** for a relational, Teams-scoped app under ~1M rows where no premium Power Apps license is in play and one unmanaged solution per environment is acceptable.
- Pick **Lists/SharePoint** for lightweight team tracking of flat data, where SharePoint's own indexing/large-list discipline is respected.
- Upgrade Dataverse-for-Teams → Dataverse when you need "more granular control for security and governance, or capacity beyond the approximately 1 million rows" (first-party, retrieved 2026-06-08) — it's a supported in-place upgrade, so starting in Teams is not a dead end.

**Don't:**
- Use **Excel as a backend.** It is an import/export path, not a data source column in the comparison; a 50k-row workbook is a migration target, not a store (this plugin routes "migrate this 50,000-row Excel workbook" to `dataverse-architect` first — CLAUDE.md §2). `[Excel-as-backend exclusion is an inference from the comparison page's framing + this plugin's CLAUDE.md §4 anti-pattern, not a single quoted sentence.]`
- Use **SharePoint as a transactional database past a few thousand rows** (CLAUDE.md §4 anti-pattern) — delegation cliffs and the large-list threshold make it a perf/correctness hazard for write-heavy apps.
- Default to full Dataverse for a tiny Teams tracker — you're paying premium licensing + capacity for security/ALM depth nobody needs.

## Edge cases / when the rule does NOT apply

- **Existing system of record** — if the data already lives authoritatively in SQL/SAP/Salesforce, the question shifts to a Dataverse **virtual table** or a connector, not a fresh store (see [`./dataverse-virtual-tables-tradeoffs.md`](./dataverse-virtual-tables-tradeoffs.md)).
- **Licensing specifics are volatile** — `[verify-at-use]` against the Dataverse licensing FAQ the comparison page links before quoting license cost to a customer.
- **Guest/external access** — Lists and Dataverse-for-Teams have hard guest limits; external-user scenarios usually force full Dataverse + Power Pages.

## See also

- [`../knowledge/dataverse-decision-trees.md`](../knowledge/dataverse-decision-trees.md) — the trees that decide *within* Dataverse once it's chosen (this rule is upstream of them)
- [`../knowledge/datastore-and-integration-decision-trees.md`](../knowledge/datastore-and-integration-decision-trees.md) — `## Decision Tree: Data store — Dataverse vs Dataverse for Teams vs Lists vs Excel`
- [`./gov-environment-strategy-and-isolation.md`](./gov-environment-strategy-and-isolation.md) — environment placement once the store is Dataverse
- [`../agents/dataverse-architect.md`](../agents/dataverse-architect.md) — owns the store-selection call

## Provenance

Grounded in Microsoft Learn *Comparing Microsoft Lists, Dataverse for Teams, and Dataverse* (`power-apps/teams/compare-data-sources`, first-party, `updated_at 2025-05-07`) and *Dataverse for Teams vs. Dataverse* (`power-apps/teams/data-platform-compare`, first-party), both retrieved 2026-06-08; research persisted at `docs/research/2026-06-08-power-platform-best-practices/`. Makes this plugin's CLAUDE.md §4 "SharePoint as a transactional database" anti-pattern a positive, structured selection rule.

---

_Last reviewed: 2026-06-08 by `claude`_
