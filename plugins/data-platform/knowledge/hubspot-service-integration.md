---
name: hubspot-service-integration
description: "HubSpot Service Hub (ticket-grain) ingestion — extends the general HubSpot knowledge. Search API capped at **4 req/sec** is the BINDING constraint for incremental loads (not the 190 req/10s headline). Ticket pipelines + pipeline-stages are tenant-defined; `hs_pipeline_stage` is only unique within `hs_pipeline`. Pre-computed `time_to_first_agent_reply` / `time_to_close` available on Service Hub. SLA properties (`hs_sla_target`, `hs_sla_at_breach`) on Pro+. Date-based API versioning rollout 2026-03."
last_reviewed: 2026-06-04
confidence: high
---

# HubSpot Service Hub integration

> **Last reviewed:** 2026-06-04. **Specializes** [`hubspot-integration.md`](./hubspot-integration.md) for the Service-Hub ticket-grain shape. Sources: HubSpot dev docs (API usage limits, CRM Tickets API, default ticket properties, rate-limit changelog), Scopious's production rate-limit guide, Fivetran HubSpot setup. Refresh when: (a) the 4 req/sec Search API cap changes, (b) the date-based versioning rollover retires legacy paths, (c) pipeline-stage SLA property names shift, or (d) the Associations API burst limit relaxes.

## Connector strategy — BUY (managed)

- **Fivetran** — first-party HubSpot connector covering all CRM objects including Tickets. `[verify-at-use — 2026-06-04]`
- **Airbyte** — HubSpot source.
- **Hightouch** — HubSpot as a destination.
- **Planhat ↔ HubSpot** — documented native integration.

## API extraction pattern — the 4 req/sec Search ceiling

### Endpoints

- `GET /crm/v3/objects/tickets` — list (no rich filter; for full re-syncs)
- `POST /crm/v3/objects/tickets/search` — rich filters; **the incremental workhorse**
- `GET /crm/v3/objects/tickets/{id}/associations/{toObjectType}` — association traversal

### Date-based versioning (2026-03 rollover)

- HubSpot introduced **date-based versioning** with the 2026-03 release: paths shift from `/api-name/v3/resource` to `/api-name/2026-03/resource`. `[verify-at-use — 2026-06-04]`
- Legacy paths (`v1`/`v2`/`v3`) remain until end-of-life — pin to a known dated version in your connector and re-test on bumps.

### Watermark

- `hs_lastmodifieddate` filter on the Search endpoint:
  ```json
  {"filters": [{"propertyName": "hs_lastmodifieddate", "operator": "GTE", "value": <epoch_ms>}]}
  ```

### Pagination

- Cursor via `paging.next.after` field on responses.
- **Search caps at 10,000 records per query** — slide the watermark window if you exceed.

### Rate limits — the dominant binding constraint

| Surface | Limit | Notes |
|---|---|---|
| Private apps Free/Starter | **100 req/10s** | `[verify-at-use — 2026-06-04]` |
| Private apps Pro/Enterprise | **190 req/10s** | `[verify-at-use — 2026-06-04]` |
| With add-on | **250 req/10s** (stackable 2×) | `[verify-at-use — 2026-06-04]` |
| OAuth marketplace apps | **110 req/10s per installed account** | `[verify-at-use — 2026-06-04]` |
| **CRM Search API** | **4 req/sec across ALL search endpoints** | **The actual ceiling for incremental ingestion.** `[verify-at-use — 2026-06-04]` |
| Associations API | separate burst limit, intentionally below 190/10s | `[verify-at-use — 2026-06-04]` |

**Strategic implication:** the headline "190 req/10s" is misleading for ETL because **incremental ingestion lives on `/search`**, which is bound by the 4 req/sec cap. A wide watermark sweep will choke other warehouse jobs sharing the API budget. Plan against the 4/sec number, not the 190/10s number.

## Schema shape — entity → conformed-field map

Tickets in HubSpot are first-class CRM objects with properties + associations.

| Conformed concept | HubSpot entity | Key fields |
|---|---|---|
| Ticket | `tickets` | `hs_object_id`, `subject`, `content`, `hs_pipeline`, `hs_pipeline_stage`, `hs_ticket_priority` (LOW/MEDIUM/HIGH), `hs_ticket_category`, `source_type`, `hubspot_owner_id`, `createdate`, `hs_lastmodifieddate`, `closed_date`, `time_to_first_agent_reply`, `time_to_close`, `hs_resolution`, `hs_sla_at_breach`, `hs_sla_target` (Service Hub Pro+) |
| Conversation event | `engagements` (notes, emails, calls) associated with the ticket | `hs_object_id`, ticket associations |
| Contact | `contacts` | `hs_object_id`, `email`, `hubspot_owner_id` |
| Account bridge | `companies` | `hs_object_id`, `domain`, `name`, `sfdc_account_id` (custom prop convention) |
| Tag | **no first-class tag** — uses `hs_ticket_category` + custom multi-select props | — |
| SLA | per-pipeline-stage SLA config (Service Hub Pro+) | `hs_sla_*` properties on ticket |

**Default ticket properties confirmed:** `subject`, `hs_pipeline`, `hs_pipeline_stage`, `hs_ticket_priority`. To enumerate all properties for a tenant: `GET /crm/v3/properties/tickets`. `[verify-at-use — 2026-06-04]`

## Ticket-aging derivation

**HubSpot pre-computes** `time_to_first_agent_reply` and `time_to_close` as ticket properties on Service Hub — **read these directly rather than re-derive**. Service Hub does the business-hours math for you.

Status-bucket aging requires pulling `hs_pipeline_stage` history via:
- `GET /crm/v3/properties-history` (separate endpoint), OR
- `propertiesWithHistory=` parameter on the object call.

**Property-history is opt-in.** Without it, you'll miss status transitions.

## SLA-breach detection

Service Hub Pro+ surfaces SLA outcomes as ticket properties:

- `hs_sla_target` (deadline timestamp)
- `hs_sla_at_breach` (breach timestamp — non-null = breached)
- Per-pipeline-stage SLA flags

**Breach:** `hs_sla_at_breach IS NOT NULL`. `[verify-at-use — 2026-06-04]` — HubSpot property convention; verify on tenant before relying on names.

## Themes / tags & escalation

- **No tags.** Use `hs_ticket_category` + custom multi-select properties for theme assignment.
- **Escalation (derived):** priority bumped to `HIGH`, pipeline stage flipped to an "Escalated" stage, or owner reassigned to an escalation queue.

## Linking to SFDC Account / Planhat Company

**Bridge:** custom property on `companies` (typically `sfdc_account_id`) populated via the standard HubSpot↔Salesforce sync. Then Ticket→Company association → SFDC Account is a two-hop join.

Precedence:

1. `companies.sfdc_account_id` (custom prop) → `match_method='external_id'`, confidence 1.0
2. `companies.domain` ↔ SFDC `Account.Website` → `match_method='email_domain'`, confidence 0.8
3. Manual override.

## Common gotchas

1. **The Search API at 4 req/sec is the BINDING constraint.** The 190 req/10s headline doesn't apply to incremental — incremental lives on Search. Plan against 4/sec. `[verify-at-use — 2026-06-04]`
2. **Associations API has a separate burst limit** intentionally below 190/10s — verify per call shape. `[verify-at-use — 2026-06-04]`
3. **Property-history is opt-in** via `propertiesWithHistory=`. You'll miss status transitions without it.
4. **Date-based versioning rollover.** Pin to a known dated version and re-test on bumps. `[verify-at-use — 2026-06-04]`
5. **"Pipeline" + "Pipeline stage"** — a multi-pipeline tenant means `hs_pipeline_stage` strings are only unique **within** `hs_pipeline`. Key on the pair, never on stage alone.
6. **No first-class tags.** Build theme rollups off `hs_ticket_category` + custom multi-select props.
7. **`hs_ticket_priority` enum is LOW/MEDIUM/HIGH** — three levels, not four like Zendesk. Map carefully into `priority_conformed`.

## Recommended sync configuration

- **Cadence:** every 1–2 hours for tickets (constrained by 4 req/sec Search budget).
- **Backfill:** 12+ months for resolution-time distributions.
- **Incremental cursor:** `hs_lastmodifieddate` GTE filter via Search.
- **Associations:** pull on a slower cadence (daily) to respect the separate burst limit.
- **Property history:** enable `propertiesWithHistory=hs_pipeline_stage,hs_ticket_priority,hubspot_owner_id` for the aging analysis.

## Refresh triggers

- 4 req/sec Search API cap changes (any relaxation is meaningful).
- Date-based versioning rollover retires legacy paths.
- Pipeline-stage SLA property names shift.
- Associations API burst limit relaxes.
- Service Hub adds or removes pre-computed metrics (`time_to_first_agent_reply` etc.).

## References

All URLs accessed 2026-06-04.

- https://developers.hubspot.com/docs/developer-tooling/platform/usage-guidelines — API usage guidelines and limits
- https://developers.hubspot.com/changelog/increasing-our-api-limits — Rate-limit changelog (190/10s + 4/sec note)
- https://www.scopiousdigital.com/blog/hubspot-api-rate-limits-production — Production rate-limit guide
- https://developers.hubspot.com/docs/api-reference/legacy/crm/objects/tickets/guide — CRM Tickets API guide
- https://developers.hubspot.com/blog/a-developers-guide-to-hubspot-crm-objects-ticket-object — Ticket Object dev blog
- https://knowledge.hubspot.com/properties/hubspots-default-ticket-properties — Default ticket properties
- https://developers.hubspot.com/docs/guides/apps/api-usage/usage-details — Usage details
- https://fivetran.com/docs/connectors/applications/hubspot/setup-guide — Fivetran HubSpot setup
