---
name: freshdesk-integration
description: "Freshdesk (Freshworks) support-ticket integration — BUY managed connector. Watermark caveat: `updated_since` silently skips tickets that have never been updated after creation. 300-page hard cap + 100 records/page = 30k-row ceiling per `updated_since` query; slide the watermark in day-range batches for high-volume tenants. First-class `is_escalated` boolean (unusual for the category). Plan-tiered rate limits 200–700 req/min. Planhat native integration caps initial sync at 16k records."
last_reviewed: 2026-06-04
confidence: high
---

# Freshdesk integration

> **Last reviewed:** 2026-06-04. Sources: Freshdesk Help Desk API v2 (developer.freshdesk.com), Freshworks Community threads on the 30k cap + 429s, Truto's 2026 engineering guide, Fivetran + Airbyte Freshdesk connector docs, Planhat Freshdesk integration. Refresh when: (a) the 300-page / 30k-row ceiling changes, (b) the `updated_since` semantics around never-updated tickets change, (c) plan rate-limit tiers shift, or (d) the Planhat initial-sync cap changes.

## Connector strategy — BUY (managed connector)

- **Fivetran** — first-party Freshdesk connector; admin privileges required during setup. `[verify-at-use — 2026-06-04]`
- **Airbyte** — Freshdesk source available.
- **Planhat** — native Freshdesk integration: initial manual sync of recent tickets capped at **16,000 records** `[verify-at-use — 2026-06-04]`, then continuous incremental. Tickets land in Planhat as Conversations of type "ticket".
- **Hightouch** — not enumerated as a first-party Freshdesk destination at last check; verify in Hightouch's destinations catalog before promising it.

**Verdict:** managed connector beats hand-rolled for typical CS dashboard work — the 300-page ceiling (see below) is a real pain to engineer around manually.

## API extraction pattern

### Endpoint + watermark

- **Endpoint:** `GET /api/v2/tickets` with `updated_since=<ISO8601>`.
- **Watermark caveat (silent-skip gotcha):** the `updated_since` parameter **only returns tickets that have been updated at least once during their lifespan**. Tickets with no updates after creation can be missed by an `updated_since` sweep. `[verify-at-use — 2026-06-04]`
- **Robust pattern:**
  1. Initial historical load via `updated_since=<epoch>` for the bulk of history.
  2. Ongoing changed-record sync on `updated_since`.
  3. **Periodic completeness check** — e.g., a daily `created_since` sweep for newly created tickets that haven't yet been touched, to backfill the never-updated cohort.

### Pagination — the 30k wall

| Constraint | Value | Notes |
|---|---|---|
| Default page size | **30** | `[verify-at-use — 2026-06-04]` |
| Max page size | **100** | `[verify-at-use — 2026-06-04]` |
| Hard page cap per query | **300 pages** | `[verify-at-use — 2026-06-04]` |
| **Effective ceiling per `updated_since` window** | **30,000 tickets** | 100/page × 300 pages |

**The 30k ceiling is the dominant scaling constraint.** Above this, the connector (or your loader) **must** slide the `updated_since` watermark into smaller windows — daily batches for large tenants, hourly for very-large tenants — and merge in the warehouse.

### Rate limits (2026)

| Plan tier | Limit | Notes |
|---|---|---|
| Free / Growth | **~200 req/min** | `[verify-at-use — 2026-06-04]` |
| Pro | mid-tier (typically ~400 req/min) | `[verify-at-use — 2026-06-04]` |
| Enterprise | **up to ~700 req/min** | `[verify-at-use — 2026-06-04]` |
| Per-endpoint sub-limits | yes | conversations / contacts / tickets are bucketed separately |

429s carry `Retry-After`; honor it.

### Include parameter (the perf lever)

- Freshdesk's ticket endpoint supports `include=requester,company,stats,description` to fold associated rows into the same response — reduces N+1 calls when pulling conversations/companies alongside tickets. `[verify-at-use — 2026-06-04]`

## Schema shape — entity → conformed-field map

| Conformed concept | Freshdesk entity | Key fields |
|---|---|---|
| Ticket | `tickets` | `id`, `subject`, `status` (Open/Pending/Resolved/Closed/+custom), `priority` (1–4 numeric), `source` (email/portal/phone/chat/feedback widget/etc.), `type`, `requester_id`, `responder_id` (agent), `company_id`, `group_id`, `tags[]`, `cc_emails[]`, `fr_due_by`, `due_by`, **`is_escalated`** (boolean — first-class), `created_at`, `updated_at` |
| Conversation event | `conversations` (sub-resource: `/tickets/{id}/conversations`) | `id`, `ticket_id`, `user_id`, `body_text`, `incoming`, `private`, `created_at` |
| Contact | `contacts` | `id`, `email`, `company_id` |
| Account bridge | `companies` | `id`, `name`, `domains[]`, custom fields |
| Tag | account-scoped strings on ticket | inline `tags[]` |
| SLA | `sla_policies` | per-policy targets by priority |

**`is_escalated` is a first-class boolean on the ticket** — uniquely convenient among support vendors (Zendesk, JSM, HubSpot, Help Scout, Front, Intercom all require derived escalation flags).

## Ticket-aging derivation

- `fr_due_by` = first-response SLA deadline.
- `due_by` = resolution SLA deadline.
- `created_at` → first agent-public conversation = first-response time.
- `created_at` → `updated_at` (when `status` flips to `Resolved`) = total resolution.
- Status-history changes available via the `/activities` endpoint (separate fetch).
- No widely adopted Fivetran dbt package for Freshdesk equivalent to `dbt_zendesk` exists at last check — expect to author your own metrics, or use the warehouse-vendor's helpdesk packages if available. `[verify-at-use — 2026-06-04]`

## SLA-breach detection

`fr_due_by` / `due_by` are *deadlines*. Breach = `now > fr_due_by AND first_response_at IS NULL` (or the resolution equivalent).

Freshdesk also lets admins configure an **escalation chain** that fires at violation — when that fires, `is_escalated=true` flips on the ticket. So in Freshdesk, an `is_escalated=true` row is a strong signal that an SLA broke (in addition to whatever other causes admins configure).

## Themes / tags & escalation

- Tag taxonomy: same alias-map + theme-rollup pattern as Zendesk.
- **Escalation flag is trivial — read `is_escalated`.** No derived logic required for the headline signal.

## Linking to SFDC Account / Planhat Company

Precedence:

1. **`companies.cf_sfdc_account_id`** (or whatever the custom-field convention is in the tenant) populated with the SFDC `Account.Id` → `match_method='external_id'`, confidence 1.0
2. **`companies.domains[]`** ↔ SFDC `Account.Website` / domain-extracted-from-email → `match_method='email_domain'`, confidence 0.8
3. Manual override via stewardship.

Planhat's native Freshdesk integration auto-bridges the company to the Planhat Company.

## Common gotchas

1. **The 300-page wall (30k records).** A single `updated_since` query returns ≤30,000 tickets; for large tenants you must slide the watermark in small windows or batch by day. Ignoring this silently drops records past page 300. `[verify-at-use — 2026-06-04]`
2. **"Never updated" tickets disappear under `updated_since`.** Pair with a `created_since` sweep or initial-load + delta pattern.
3. **Conversations are a sub-resource** — N+1 calls per ticket unless you batch with `include=`. Freshdesk supports `include=requester,company,stats,description`. `[verify-at-use — 2026-06-04]`
4. **Custom statuses** mean `Resolved` / `Closed` are not enumerable globally — fetch the status map from `/api/v2/admin/ticket_fields` and persist it as a slowly-changing dimension.
5. **Numeric priority (1–4)** — Freshdesk uses integer priority while most peers use named strings. Map to `priority_conformed` (low/normal/high/urgent) via a lookup, not by inference.
6. **Planhat initial-sync cap.** 16,000-record cap on Planhat's native initial sync — for tenants with deeper history, supplement with a warehouse-direct load.

## Recommended sync configuration

- **Cadence:** every 1–2 hours for tickets; daily for companies / contacts / sla_policies / ticket_fields.
- **Backfill strategy:** day-range batched `updated_since` windows for the initial load. Confirm the connector does this — if you're hand-rolling, plan day-by-day.
- **`include=` parameter:** always pull `requester,company,stats` to dodge the N+1 trap.
- **Status-map dimension:** fetch `/api/v2/admin/ticket_fields` daily and persist as an SCD2 to support custom-status historical reporting.

## Refresh triggers

- 300-page / 30k-row ceiling changes (any relaxation simplifies the loader meaningfully).
- `updated_since` semantics around never-updated tickets change.
- Plan rate-limit tiers shift.
- Planhat initial-sync cap changes.
- A canonical dbt package for Freshdesk emerges in `fivetran/dbt_*` or equivalent.

## References

All URLs accessed 2026-06-04.

- https://developer.freshdesk.com/api/v1/ — Help Desk API for Developers (Freshdesk)
- https://community.freshworks.com/api-and-webhooks-11406/load-of-tickets-more-than-30-000-using-freshdesk-rest-api-v2-26403 — 30k ceiling discussion
- https://community.freshworks.com/api-and-webhooks-11406/api-rate-limit-errors-429-35031 — 429 + per-plan limits
- https://truto.one/blog/how-to-integrate-with-the-freshdesk-api-2026-engineering-guide/ — Truto 2026 Freshdesk engineering guide
- https://support.freshdesk.com/support/solutions/articles/50000000041-support-metrics-in-freshdesk-analytics — Support metrics
- https://support.freshdesk.com/support/solutions/articles/37626-understanding-sla-policies — SLA policies
- https://fivetran.com/docs/connectors/applications/freshdesk/setup-guide — Fivetran Freshdesk setup
- https://airbyte.com/integrations/freshdesk — Airbyte Freshdesk source
- https://support.planhat.com/en/articles/4374425-setting-up-the-freshdesk-integration — Planhat Freshdesk integration
