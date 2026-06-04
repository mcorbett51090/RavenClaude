# Enhancement: Zendesk support-ticket ingestion knowledge file

**Target path:** `plugins/data-platform/knowledge/zendesk-integration.md`
**Status:** NEW file
**Purpose:** Per-vendor reference for the `etl-pipeline-engineer` + `support-ticket-normalization` skill on Zendesk Support — managed-connector landscape, dbt_zendesk conformed models, API extraction discipline, conformed-model field mapping.

---

```markdown
---
file: plugins/data-platform/knowledge/zendesk-integration.md
last_reviewed: 2026-06-04
sources:
  - "Zendesk Developer Docs — Incremental Exports (https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/)"
  - "Zendesk Developer Docs — Rate Limits (https://developer.zendesk.com/api-reference/introduction/rate-limits/)"
  - "Zendesk Developer Docs — Pagination (https://developer.zendesk.com/api-reference/introduction/pagination/)"
  - "Fivetran Zendesk Support schema + setup guide (https://fivetran.com/docs/connectors/applications/zendesk)"
  - "fivetran/dbt_zendesk + fivetran/dbt_zendesk_source (github.com/fivetran/dbt_zendesk)"
  - "Airbyte Zendesk Support source (docs.airbyte.com/integrations/sources/zendesk-support)"
  - "Planhat Zendesk integration (support.planhat.com/en/articles/1608933)"
refresh_triggers:
  - "Zendesk raises or retunes incremental-export rate limits (currently 10 req/min or 30 with High Volume add-on)"
  - "Cursor-based incremental coverage extends beyond tickets/users/custom-objects"
  - "Fivetran dbt_zendesk package adds/removes conformed models"
  - "Zendesk Support Pro+ requirement for business-hours math changes"
---

# Zendesk integration

> **Last reviewed:** 2026-06-04. Sources: Zendesk Developer Docs (incremental exports, rate limits, pagination), Fivetran Zendesk Support connector + dbt_zendesk package, Airbyte Zendesk Support source, Planhat Zendesk integration. Refresh when: (a) Zendesk changes rate-limit tiers or pagination model, (b) cursor-based incremental coverage extends beyond tickets/users/custom-objects, (c) the `fivetran/dbt_zendesk` package adds/removes conformed models, (d) the Support Pro+ requirement for business-hours math changes.

## Connector strategy — BUY (managed connector + dbt package)

Zendesk is the **best-supported** vendor in the support category. **BUY** the managed connector and **BUY** the dbt package. There is rarely a reason to hand-roll a Zendesk loader.

- **Fivetran** — first-party Zendesk Support connector, multithreaded parallel API requests during historical load. Pair with `fivetran/dbt_zendesk` (the canonical conformed-model package). `[verify-at-use — 2026-06-04]`
- **Airbyte** — separate sources for **Zendesk Support**, **Zendesk Chat**, and **Zendesk Talk**. Pull the ones you need; don't enable all three by default.
- **Planhat** — native Zendesk integration: initial manual sync of last 6 months of non-closed tickets, then incremental. Tickets land in Planhat as a **Conversation of type "ticket"**.
- **Hightouch** — supported as a **destination** (warehouse → Zendesk reverse-ETL).

**Cost note (2026):** Fivetran moved to **connector-level MAR pricing** in Mar 2025 + $5/connection minimum effective Jan 1, 2026 + **delete operations now count toward paid MAR**. `[verify-at-use — 2026-06-04]` On a busy support org this can shift the BUY math — re-quote before assuming the connector is cheap. See [`support-connector-build-vs-buy-2026.md`](./support-connector-build-vs-buy-2026.md).

## API extraction pattern

### Endpoint choice

- **Use:** `GET /api/v2/incremental/tickets/cursor` (cursor-based incremental). Zendesk explicitly recommends cursor-based over time-based.
- **Don't use:** `/api/v2/incremental/tickets` (time-based legacy) — kept for back-compat.

### Watermark discipline

- First call: `start_time=<unix_epoch>`. Subsequent calls: `cursor=<after>` from the prior page.
- **The 60-second floor:** `start_time` must be **>60s in the past** or records will be silently dropped. Always backfill from `now − 90s`. `[verify-at-use — 2026-06-04]`
- **Cursor is opaque** — never construct, never persist longer than necessary.

### Pagination & rate limits

| Constraint | Value | Notes |
|---|---|---|
| Page size | up to **1,000 records/page** | `[verify-at-use — 2026-06-04]` |
| Incremental export rate | **10 req/min** + separate **1 req/sec** ceiling | `[verify-at-use — 2026-06-04]` |
| With High Volume API add-on | **30 req/min** | Requires ≥10 agent seats, Suite Growth+. `[verify-at-use — 2026-06-04]` |
| Account-level rate | **200–2,500 req/min** by plan (Team → Enterprise Plus) | `[verify-at-use — 2026-06-04]` |
| Update Ticket endpoint | 30 updates / 10 min / user / ticket; 100 req/min/account (300 with HV) | `[verify-at-use — 2026-06-04]` |
| Offset pagination above page 1,000 | throttled to **10 req/min** since Sep 2021 | Use cursor-based to avoid this. |

**Cold-reload ceiling math:** 10 req/min × 1,000/page = **600k tickets/hr**. Plan 2–3 days for the largest tenants or buy High Volume.

### Side-loading (the dominant performance lever)

`include=metric_sets,users,groups,organizations,comment_count` on the incremental tickets endpoint folds associated rows into the same response. Without this, expect 2–3× call count.

### Cursor coverage caveat

Cursor-based incremental is **supported only for tickets, users, and custom-object records**. For organizations, groups, satisfaction ratings, tags, ticket fields, and SLA policies — use the standard list endpoints. `[verify-at-use — 2026-06-04]`

## Schema shape — entity → conformed-field map

| Conformed concept | Zendesk entity | Key fields |
|---|---|---|
| Ticket | `tickets` | `id`, `external_id`, `subject`, `status`, `priority`, `type` (question/incident/problem/task), `requester_id`, `submitter_id`, `assignee_id`, `organization_id`, `group_id`, `brand_id`, `tags[]`, `created_at`, `updated_at`, `due_at`, `via.channel` |
| Conversation event | `ticket_comments`, `ticket_audits` | `id`, `ticket_id`, `author_id`, `body`, `public`, `created_at` |
| User | `users` | `id`, `email`, `role`, `organization_id`, `external_id`, `tags[]` |
| Account bridge | `organizations` | `id`, `name`, `external_id`, `domain_names[]`, `organization_fields{}` |
| Tag dictionary | `tags` (account-scoped) | `name`, `count` |
| SLA | `sla_policies` + per-ticket `sla_policy_metrics` | policy IDs + per-policy targets; outcomes in `ticket_metrics` + audit events |

## The 4 conformed models from `fivetran/dbt_zendesk`

This is the path of least resistance — install the package, point it at the raw schema, get these models for free:

| Model | What it gives you |
|---|---|
| `zendesk__ticket_enriched` | Joins requester / assignee / org / group / tags onto each ticket |
| `zendesk__ticket_metrics` | Response times, resolution time, work time in **both calendar and business hours** |
| `zendesk__sla_policies` | Per-policy SLA outcomes (compliance + breach) in both clock modes |
| `zendesk__ticket_field_history` | Daily snapshot of status / priority / assignee changes — the canonical input for aging-bucket cohorts |

**Business-hours math requirement:** the package's business-hours computations rely on schedule data Zendesk only emits on **Support Professional+**. Calendar-hours computations work on any plan. `[verify-at-use — 2026-06-04]`

## Ticket-aging derivation

Definitions Zendesk uses (the dbt package adopts these):

- **First reply time** — first agent public comment minus ticket creation.
- **Next reply time** — each subsequent end-user-comment-to-agent-comment gap.
- **Requester wait time** — sum of all open-status durations facing the requester.
- **Agent work time** — sum of pending/hold durations.
- **Total resolution time** — ticket creation → first `solved`.

Six SLA target types ship out of the box: first-reply, next-reply, periodic-update, request-wait, agent-work, total-resolution.

## SLA-breach detection

Zendesk computes breach itself and surfaces it via `sla_policy_metrics` on the ticket + audit events for clock start/stop/breach. The dbt package surfaces this as `zendesk__sla_policies`.

**Near-breach alerting (80% clock consumed)** — derive in the warehouse: `(business_minutes_elapsed / target_business_minutes)` per open policy event.

## Themes / tags taxonomy

- `tags` are **account-scoped, free-form, agent-applied** → fold into a `dim_tag_alias` map → roll up to top-level themes (Billing / Bug / Feature / Onboarding / Outage).
- The `fivetran/dbt_zendesk_source` package emits a `ticket_tag` long-form table ideal for this.
- Round out categorical dimensions with `ticket.type`, `ticket.priority`, `ticket.via.channel`.

## Escalation flagging

**No first-class `is_escalated` on the ticket object.** Derive as **any of**:

1. `priority` raised to `urgent`
2. assigned to a group named like `Tier 2` / `Engineering` (account-specific allow-list)
3. `ticket_audit` shows status flip to `hold` or `pending` followed by reassignment
4. SLA-policy breach event fires

Compute in dbt against `zendesk__ticket_field_history` + `zendesk__sla_policies`.

## Linking to SFDC Account / Planhat Company (bridge)

Precedence ladder (matches the cross-system-identity-resolution skill):

1. **`zendesk.organizations.external_id`** populated with the SFDC `Account.Id` at integration time → `match_method='external_id'`, confidence 1.0
2. **Domain join** — `organizations.domain_names[]` ↔ `Account.Website` / domain-extracted-from-email → `match_method='company_domain'`, confidence 0.8
3. **Manual override** — only via stewardship surface

Planhat's native Zendesk integration handles this automatically and stores the imported ticket as a *Conversation of type "ticket"* on the matched Company.

## Common gotchas

1. **Cursor cap surprise.** 10 req/min × 1,000/page = 600k tickets/hr cold-reload ceiling — fine for most, but plan 2–3 days historical for the largest tenants (or buy High Volume).
2. **Side-load or die.** Without `include=metric_sets,users,organizations`, call count doubles or triples.
3. **Cursor is for tickets/users/custom-objects only.** Tags, satisfaction ratings, ticket fields, groups, sla_policies use ordinary list endpoints.
4. **The 60-second floor.** `start_time` within 60s of now silently drops records — backfill from `now − 90s`.
5. **Soft-deletes / merges.** Merged tickets keep IDs but flip `status=closed` with a merge-comment; deletes emit via deletion endpoints, *not* via the incremental cursor. Hook the audit-log endpoint to catch them.
6. **`solved` ≠ `closed`.** `solved` is "agent done, customer can reopen for 4 days"; `closed` is terminal. CS dashboards usually want `solved` for SLA, `closed` for inventory aging.
7. **Business-hours requires Support Pro+.** The dbt package's business-hours math depends on schedule data only emitted on Pro+. `[verify-at-use — 2026-06-04]`

## Recommended sync configuration

- **Cadence:** every 1–2 hours for tickets (CS dashboards refresh ≤ daily); daily for organizations / tags / sla_policies.
- **Backfill:** 12+ months for resolution-time distributions and SLA-attainment trend.
- **Incremental cursor:** cursor-based on tickets/users/custom-objects; `updated_at` filter on list endpoints for the rest.
- **Side-load:** always enable `include=metric_sets,users,organizations,comment_count`.

## Refresh triggers

- Zendesk re-tunes incremental-export rate limits (currently 10/min, 30/min with HV).
- Cursor-based incremental extends beyond tickets/users/custom-objects.
- `fivetran/dbt_zendesk` package adds/removes conformed models.
- Support Pro+ requirement for business-hours data changes.
- Pricing tier changes affecting Fivetran connector-MAR economics.
```
