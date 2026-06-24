# HubSpot integration

> **Last reviewed:** 2026-05-21. Sources: HubSpot developer docs ([developers.hubspot.com/docs/developer-tooling/platform/usage-guidelines](https://developers.hubspot.com/docs/developer-tooling/platform/usage-guidelines)), Fivetran/Airbyte connector docs. Refresh when: (a) HubSpot raises or restructures API rate limits, (b) v4 API release changes the entity model, or (c) HubSpot deprecates v3 endpoints.

## Auth

- **OAuth 2.0 (marketplace apps)** — for distributed integrations; rate limits are per-installed-account
- **Private apps (workspace-scoped)** — for single-org integrations; rate limits are per-app
- **API keys** — deprecated; do not use for new builds

## Registering the app (developer portal)

Two registration paths depending on whether the integration is single-org or distributed. Treat each step as `[verify-at-build]` — HubSpot's settings + developer UIs move.

> **Single-org ELT (the common case) — Private App.**
> **Portal:** the HubSpot portal → **Settings (gear) → Integrations → Private Apps → Create a private app**.
> **Who can do it:** a HubSpot **super admin** on that portal.
>
> **Distributed / marketplace — OAuth App.**
> **Portal:** [developers.hubspot.com](https://developers.hubspot.com) → create a developer account → **Apps → Create app**.
> **Who can do it:** anyone with a HubSpot developer account to *build* it; installing it into a customer portal still needs that portal's **super admin** to grant consent.

1. **Private app:** create it, select **CRM read scopes** (`crm.objects.contacts.read`, `…companies.read`, `…deals.read`, `tickets`, etc.), then copy the **access token** (a bearer token — store as a secret reference).
2. **OAuth app:** set scopes + the **redirect URL** (your ELT vendor's callback), copy the **Client ID/Secret**, and run the install/consent flow per installed account.
3. Use the **least scopes** the marts actually need — over-broad scopes widen the blast radius and can trip the install review.

## Rate limits (CRITICAL — easy to hit)

### OAuth marketplace apps
- **110 req/10 sec** per installed account

### Private apps
| Tier | Limit |
|---|---|
| Free / Starter | 100 req/10s |
| Professional / Enterprise | 190 req/10s |

### Search API (separate, lower)
- **CRM Search API: 4 req/sec** — separate from other API limits
- The Search API is what large filtered queries use; easy to throttle when paginating

### Daily limits
- **Developer accounts via OAuth: up to 1,000,000 calls/day**
- Higher limits available through HubSpot Support for enterprise integrations

> Source: [HubSpot Platform Usage Guidelines](https://developers.hubspot.com/docs/developer-tooling/platform/usage-guidelines) — verify before quoting in client engagements

## Connector availability

| Vendor | HubSpot connector |
|---|---|
| Fivetran | ✅ |
| Airbyte | ✅ |
| Hevo | ✅ |
| Stitch | ✅ (maintenance mode) |

## Common entities (CRM API v3)

| Object | Use case | Notes |
|---|---|---|
| `companies` | Account dimension | Standard CRM object |
| `contacts` | Contact dimension | Standard CRM object |
| `deals` | Opportunity/pipeline fact | Equivalent to Salesforce Opportunity |
| `tickets` | Service/support fact | Equivalent to Salesforce Case |
| `engagements` | Activity fact (calls, emails, meetings, notes, tasks) | Multiple subtypes |
| `line_items` | Deal-line-item fact | Quote and revenue analytics |
| `products` | Product dimension | |
| `quotes` | Quote dimension | |
| `properties` | Schema metadata | Useful for understanding custom-field shapes |
| `owners` | Internal user dimension | For deal/ticket owner attribution |
| `marketing_emails` | Marketing campaign fact | If marketing hub is in use |
| `forms` | Form-submission dimension | Marketing analytics |
| `workflows` | Workflow metadata | For automation tracking |

## Custom properties / objects

HubSpot has custom properties on every standard object + supports custom objects (Enterprise tier). The pattern:

1. List custom properties via `/crm/v3/properties/{objectType}`
2. Include the ones with analytics value in the ELT configuration
3. Custom objects (Enterprise) — list via `/crm/v3/schemas`, include needed ones

## Incremental sync

- **`lastmodifieddate`** is the canonical cursor for most objects
- **HubSpot exposes `hs_lastmodifieddate`** on custom objects
- Some Lifecycle / Engagement objects have separate timestamps — verify per object

## Recommended pattern: separate the CRM API from the Search API

The Search API's 4 req/sec ceiling means batch-heavy operations *must* avoid it where possible:

- **Use the read-all endpoint** (`/crm/v3/objects/{objectType}`) for initial backfill — uses CRM API rate limits, not Search
- **Use Search only for filtered queries** — and only when truly necessary
- **Pagination via `after` cursor** — preferred over offset

## Fivetran MAR cost-predictability warning

HubSpot deals are change-heavy — stage transitions, owner changes, amount updates fire frequent updates. **As of Jan 1 2026, Fivetran counts deletes (and the underlying updates) toward MAR**. For high-velocity sales orgs (>100k contacts, >10k deals/month with frequent stage changes), Fivetran MAR cost can scale unexpectedly. Flag this when quoting fixed-fee engagements.

## dbt modeling — common marts

| Mart | Purpose |
|---|---|
| `dim_company` | Company dimension |
| `dim_contact` | Contact dimension |
| `dim_owner` | Internal owner dimension |
| `fact_deal` | Pipeline + closed-won/lost facts |
| `fact_deal_stage_history` | Deal stage transitions |
| `fact_ticket` | Service/support volume + resolution times |
| `fact_activity` | Engagements unified (calls, emails, meetings, notes, tasks) |
| `fact_form_submission` | Form-submission analytics (marketing-attribution) |
| `mart_pipeline_velocity` | Deal stage velocity, win rate, average time-in-stage |
| `mart_lead_attribution` | First-touch / last-touch / multi-touch attribution |
| `mart_email_engagement` | Marketing email open/click rates by campaign |

## Common gotchas

1. **CRM-Sales-Hub vs CRM-Marketing-Hub** — separate APIs and feature gates. Deal pipeline data is in Sales Hub; marketing email data is in Marketing Hub. Check what tier the client has.
2. **Lifecycle stage** — HubSpot's "Lifecycle Stage" property tracks contacts through marketing → sales funnel. Historical changes require `hs_lifecyclestage_<stage>_date` properties.
3. **Deal stage `dealstage` is an ID, not a label** — needs `deal_pipelines` schema lookup to get human-readable stage name
4. **Engagement subtypes** — calls, emails, meetings, notes, tasks all live in `engagements` but have different child schemas (`call`, `email`, `meeting`, etc.)
5. **Properties API rate limits** — listing all properties for an object is one call, but reading values per record can blow up
6. **Marketing emails are large** — every send/open/click is a separate event; high-volume marketing orgs can have millions per month
7. **Soft-deletes** — `archived` records are recoverable; some connectors handle this, others don't
8. **Account hierarchies** — HubSpot has parent/child company relationships (Enterprise tier); custom objects support hierarchies. Plan dim_company accordingly.

## PII / PHI considerations

- **Contacts contain PII** — name, email, phone, IP address, browsing history
- **Marketing email tracking pixels** track behavior — GDPR cookie-consent considerations
- **HubSpot has SOC 2 + GDPR compliance** — vendor-side is fine; engagement-side processing needs the standard treatments
- **CCPA right-to-erasure** — HubSpot's contact-delete API removes data; the warehouse needs parallel delete

## Recommended sync configuration

- **Cadence:** daily for analytics; hourly only if intraday-pipeline-movement dashboards required
- **Backfill:** 12-24 months for sales analytics; 36+ months for cohort/retention analysis
- **Incremental cursor:** `lastmodifieddate` for most objects; `hs_lastmodifieddate` for custom objects
- **Avoid Search API for bulk** — use object-read endpoints

## Refresh triggers

- HubSpot raises or restructures API rate limits
- HubSpot v4 API release (anticipated but not announced as of 2026-05)
- Engagement uses a HubSpot Hub the connector doesn't fully cover (CMS Hub, Operations Hub)
- New custom objects added that need ELT inclusion
- ELT vendor changes pricing model
