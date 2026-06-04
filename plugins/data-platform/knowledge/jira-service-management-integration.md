---
name: jira-service-management-integration
description: "Atlassian Jira Service Management (JSM) support-ticket ingestion. Two REST surfaces — platform Jira REST (`/rest/api/3/`) for issues, JSM-specific REST (`/rest/servicedeskapi/`) for SLA + requestType + queue. The `/request/{id}/sla` payload is the authoritative breach signal (`ongoingCycle.breached`). `changelog` is the canonical history source — `expand=changelog`, cap 1,000 issues/batch, ≤10 fields filtered. Enhanced search via `nextPageToken` up to 5,000 issues/page."
last_reviewed: 2026-06-04
confidence: high
---

# Jira Service Management integration

> **Last reviewed:** 2026-06-04. Sources: Atlassian developer docs (platform Jira REST v3, JSM Cloud REST, JSM domain model, changelog), Airbyte Jira source guide, Planhat Jira integration. Refresh when: (a) Atlassian collapses or restructures the two REST surfaces, (b) the `/sla` payload shape changes, (c) the enhanced-search `nextPageToken` ceiling moves off 5,000, or (d) the changelog batch caps change.

## Connector strategy — BUY (managed) or BUILD a thin wrapper

- **Fivetran** — Jira connector covers Software + Service Management. `[verify-at-use — 2026-06-04]`
- **Airbyte** — Jira source.
- **Hightouch** — Jira destinations available; verify Service-Management-specific coverage before promising it.
- **Planhat ↔ Jira** — documented issue/comment sync.

**When to BUILD:** JSM-specific queues, request types, and the `/sla` payload aren't always first-class in managed connectors. Some teams keep the managed connector for the platform-Jira-issue base and supplement with a thin custom puller for `/rest/servicedeskapi/request/{id}/sla`.

## The two REST surfaces (the dominant gotcha)

| Surface | Base path | What it carries |
|---|---|---|
| **Platform Jira REST** | `/rest/api/3/` | issues, projects, users, comments, changelog — the universal Jira surface |
| **Jira Service Management REST** | `/rest/servicedeskapi/` | JSM-only: `request`, `requestType`, `serviceDesk`, `queue`, `organization`, **`/request/{requestId}/sla`** |

**The SLA payload lives ONLY on the JSM-specific REST**, not the platform REST. Older Jira integrations that hit only `/rest/api/3/` will have no native SLA detail. `[verify-at-use — 2026-06-04]`

## API extraction pattern

### Search + watermark

- **Search:** `/rest/api/3/search/jql` with a JQL filter `updated >= "-1h"` (or watermark-based equivalent) for incremental.
- **Pagination:**
  - Legacy: `startAt` / `maxResults` (pre-deprecation).
  - **Enhanced:** `nextPageToken` with up to **5,000 issues per page**. `[verify-at-use — 2026-06-04]` — prefer enhanced for incremental.
- **Watermark:** persist the max `updated` per source.

### Expand parameter (the perf lever)

- `expand=changelog,renderedFields,names,schema` — the **`changelog` expand is the canonical history source** for aging / status-time analysis.
- Up to **1,000 issues per changelog batch**, filterable by **≤10 field IDs**. `[verify-at-use — 2026-06-04]`

### `/sla` payload

- `GET /rest/servicedeskapi/request/{requestId}/sla` returns per-SLA `ongoingCycle` (with `goalDuration`, `elapsedTime`, `remainingTime`, **`breached`**, `paused`, `withinCalendarHours`) and full `completedCycles[]`.
- `[verify-at-use — 2026-06-04]`

### Rate limits

- Atlassian enforces **dynamic per-Cloud-tenant limits**; surfaced via `X-RateLimit-*` and `Retry-After` headers — the connector must honor them.
- **No documented hard number per minute.** Adaptive client required.

## Schema shape — entity → conformed-field map

| Conformed concept | JSM entity | Key fields |
|---|---|---|
| Ticket | `issue` (issuetype="Request" / via `serviceDesk`) | `id`, `key`, `fields.summary`, `fields.status.name`, `fields.priority.name`, `fields.assignee.accountId`, `fields.reporter.accountId`, `fields.created`, `fields.updated`, `fields.resolutiondate`, `fields.labels[]`, `fields.components[]`, `fields.customfield_10010` (request type), `fields.customfield_*` (SLA-specific fields) |
| Conversation event | `issue.changelog` + `comments` | per-change: `created`, `author`, `items[].field/from/to` |
| User | `users` (Atlassian `accountId` — opaque global ID) | `accountId`, `emailAddress` (often masked), `displayName` |
| Account bridge | `organization` (JSM-specific) | `id`, `name` — multi-tenant grouping; **NOT tied to SFDC by default** |
| Tag | `labels[]` on issue; `components[]` for product area | strings |
| SLA | `/request/{id}/sla` payload | per-policy `ongoingCycle` + `completedCycles` |

**Issue ID stability:** issue **keys are renumbered when projects move**, but the immutable `id` is stable. **Key on `id` in the warehouse; surface `key` for UX.** `[verify-at-use — 2026-06-04]`

## Ticket-aging derivation

- `fields.created` → `fields.resolutiondate` = total resolution.
- **First-response:** first change in `changelog` where `items.field = "status"` and `to = "In Progress"`, OR first `comment` by a non-reporter `accountId`.
- **Status-bucket aging:** `SUM(time between consecutive status changes)` from the changelog.
- Business-hours awareness: the `/sla` payload's `withinCalendarHours` flag tells you whether the timer is running.

## SLA-breach detection

- **Live:** `ongoingCycle.breached = true`.
- **Historical:** `completedCycles[].breached = true`.
- Business-hours respect is built into the payload via `withinCalendarHours` — no warehouse-side business-hours math required for the canonical breach flag.

## Themes / tags taxonomy

- `labels[]` — free-form.
- `components[]` — admin-defined product areas.
- `customfield_*` — organization-specific (request type, SLA, etc.).
- Same alias-map / theme-rollup pattern as Zendesk.

## Escalation flagging

No first-class `is_escalated` boolean. Derive from:

1. Status flip to "Escalated" / "Tier 2" (if the workflow includes it).
2. Priority bump to `Highest`.
3. Automation that reassigns to a specific group.
4. Any SLA `ongoingCycle.breached = true`.

## Linking to SFDC Account / Planhat Company

**JSM has no built-in customer-account concept beyond JSM `organization`** (multi-tenant grouping).

**Robust bridge:** **custom field on the issue** (`customfield_XXXXX = SFDC_Account_Id`), populated by the portal form or by a Salesforce↔JSM integration. Atlassian markets a Salesforce Service Cloud bidirectional integration for this. `[verify-at-use — 2026-06-04]`

Precedence:

1. `customfield_<sfdc_account_id>` populated → `match_method='external_id'`, confidence 1.0
2. JSM `organization.name` ↔ SFDC `Account.Name` (fuzzy) → stewardship review
3. Reporter `emailAddress` (when not masked) → domain match → `match_method='email_domain'`, confidence 0.8

## Common gotchas

1. **Two API surfaces, two doc trees.** The SLA payload lives only on JSM-specific REST. Older platform-only integrations miss SLA. `[verify-at-use — 2026-06-04]`
2. **`changelog` is expand-only.** Platform caps each call at 1,000 issues, ≤10 fields filtered. Plan call budgets accordingly. `[verify-at-use — 2026-06-04]`
3. **Issue keys are renumbered** when projects move (`SUPPORT-123` → `OPS-456`). The immutable `id` is the warehouse key.
4. **`accountId` is opaque** (GDPR-era change). Email is often masked unless your app has the right scope.
5. **Custom-field IDs vary per tenant.** Map them via `/rest/api/3/field` and persist as `dim_jira_field` — never hard-code `customfield_10010`.
6. **`organization` is NOT a customer-account concept by default.** It groups requesters within a service desk; do not auto-map it to SFDC Account without a configured integration.
7. **Adaptive rate-limiting.** No fixed req/min number — must honor `Retry-After` and `X-RateLimit-*` headers. Connectors that don't lose data under load.

## Recommended sync configuration

- **Cadence:** every 1–2 hours for issues (with `expand=changelog`); daily for projects / users / fields.
- **Backfill:** 12+ months for resolution-time distributions and SLA-attainment trend.
- **Pagination:** enhanced (`nextPageToken`) at 5,000/page where supported; fall back to `startAt` only on legacy endpoints.
- **SLA pull:** dedicated job hitting `/rest/servicedeskapi/request/{id}/sla` on currently-open requests (high frequency) + delta-updates on recently-closed (lower frequency).

## Refresh triggers

- Atlassian collapses or restructures the two REST surfaces.
- `/sla` payload shape changes.
- Enhanced-search `nextPageToken` page ceiling moves off 5,000.
- Changelog batch caps (1,000 issues, ≤10 fields) change.
- Atlassian publishes per-tenant rate-limit numbers.

## References

All URLs accessed 2026-06-04.

- https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/ — Platform Jira REST v3 (issues)
- https://developer.atlassian.com/cloud/jira/service-desk/rest/ — JSM Cloud REST
- https://developer.atlassian.com/cloud/jira/service-desk/changelog/ — JSM changelog
- https://developer.atlassian.com/cloud/jira/service-desk/exploring-the-jira-service-desk-domain-model-via-the-rest-apis/ — JSM domain model
- https://support.atlassian.com/jira-service-management-cloud/docs/integrate-with-salesforce-service-cloud/ — JSM ↔ Salesforce integration
- https://airbyte.com/data-engineering-resources/jira-api-get-issue — Airbyte Jira guide
- https://support.atlassian.com/jira-service-management-cloud/docs/use-advanced-search-with-jira-query-language-jql/ — JQL advanced search
- https://docs.airbyte.com/integrations/sources/jira-migrations — Airbyte Jira source
- https://support.planhat.com/en/articles/4750873-setting-up-the-jira-integration — Planhat Jira integration
