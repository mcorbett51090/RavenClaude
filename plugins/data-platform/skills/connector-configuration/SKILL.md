---
name: connector-configuration
description: Connector-specific configuration patterns for ELT pipelines — QuickBooks OAuth + rate-limit handling, Stripe webhook + batch hybrid, Salesforce Bulk API 2.0, HubSpot API v3, GA4 BigQuery export, Shopify GraphQL Admin API. Used by `etl-pipeline-engineer` when configuring an Airbyte / Fivetran / n8n connector against a real source.
---

# Skill: connector-configuration

> **Invoked by:** `etl-pipeline-engineer` (primary), `connector-developer` (custom-connector path).
>
> **When to invoke:** configuring any pre-built ELT connector (QBO, Stripe, Salesforce, HubSpot, GA4, Shopify, HRIS); diagnosing a rate-limit-related failure; deciding on sync frequency / state-management posture.
>
> **Output:** a working connector config + rate-limit-aware retry plan + state-management strategy + handoff documentation for engagement end.

## The 6-source toolkit (per the consulting practice's most common ingestion targets)

### QuickBooks Online
- **Auth:** OAuth 2.0 Authorization Code; 1-hour access tokens; refresh tokens 100-day rolling with notifications at 30 and 7 days
- **Rate limits:** 10 req/s per realm-ID + app; batch endpoint 120/min; concurrent ~10. HTTP 429 / 403 → honor `Retry-After`
- **Connector availability:** Fivetran ✅, Airbyte ✅, Hevo ✅, Stitch ✅ (in maintenance)
- **QBO vs QB Desktop:** Desktop is materially different — usually requires QB Web Connector + CData / Transaction Pro. **QB Desktop is v0.2.0+ scope for this plugin.**
- **2026 watch:** "Reconnect URL" mandatory field in Intuit developer portal (single-source claim; verify before implementing)

### Stripe
- **Auth:** API key (restricted keys for production)
- **Connector availability:** Fivetran ✅, Airbyte ✅, Hevo ✅, Estuary ✅
- **Pattern:** **batch for history + webhooks for real-time** — don't try to ELT a webhook-driven event source as if it's a CRUD database
- **Common error:** ELT vendors are batch-only; client expects real-time fraud signals — webhook handlers run separately

### Salesforce
- **Auth:** Connected App + OAuth 2.0 JWT-bearer flow (server-side) or Web Server flow (interactive)
- **Bulk API 2.0 ceilings:** 150M records/day; 15k batch submissions/24hr; 10k records/batch; 10MB payload (per [developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/bulk_common_limits.htm](https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/bulk_common_limits.htm))
- **Connector availability:** Universal — all major ELT vendors. Bulk API 2.0 is the standard backbone.
- **Common error:** custom SObject field selection — limit query result columns to avoid 10MB payload pings

### HubSpot
- **Rate limits:** OAuth marketplace apps 110/10s per installed account; private apps 100/10s (Free/Starter) → 190/10s (Pro/Enterprise); **CRM Search API capped at 4/sec**; OAuth via developer accounts up to 1M/day (per [developers.hubspot.com/docs/developer-tooling/platform/usage-guidelines](https://developers.hubspot.com/docs/developer-tooling/platform/usage-guidelines))
- **Connector availability:** Fivetran ✅, Airbyte ✅, Hevo ✅
- **Common error:** sync designed against private-app rate limits then deployed via OAuth marketplace (or vice versa) — different ceilings

### Google Analytics 4
- **Native BigQuery export:** FREE, daily + streaming/intraday — **this is the recommended path** when destination is BigQuery
- **UA is gone.** GA4 only. Historical UA windows have closed for most properties.
- **ELT vendor connectors:** useful when destination is *not* BigQuery, or when blending with other sources

### Shopify
- **Auth:** OAuth 2.0
- **API contract:** REST Admin API is legacy as of Oct 1, 2024. **GraphQL Admin API required for new apps since April 1, 2025.** All new connector work uses GraphQL.
- **Webhooks:** via GraphQL `webhookSubscriptionCreate`; HTTPS / Google Pub/Sub / AWS EventBridge destinations
- **Pattern:** ELT for orders / customers / products (historical) + webhooks for inventory + order events (real-time)

### HRIS (Workday, BambooHR, ADP)
- **Workday HCM / Adaptive / Financial / Strategic Sourcing / RaaS:** Fivetran ✅; setup requires Workday Integration System User with appropriate domain permissions
- **BambooHR:** Airbyte ✅ (both source and destination)
- **ADP:** thinner native ELT coverage; usually via **Flexspring** (API-to-API connector) or **Merge.dev** unified HRIS API

## Sync-frequency decision

| Frequency | When to pick | Cost implication |
|---|---|---|
| Real-time (webhooks) | Operational dashboards, fraud, inventory | Webhook handler runs separately from ELT |
| Hourly | Recent-activity reporting | Mid-tier per-MAR; high credit usage |
| Daily | Most analytics dashboards | Industry-standard; cheapest defensible cadence |
| Weekly | Trend / retention / cohort | Cheapest; rare for SMB dashboards |

**Heuristic:** the dashboard's refresh expectation is the cadence ceiling. Daily ELT for a quarterly QBR is wasted MAR.

## The Fivetran 2026 cost-predictability warning

**As of Jan 1, 2026, Fivetran counts deletes toward paid MAR** (previously only inserts/updates). For change-heavy sources (Salesforce, HubSpot deal updates, ticketing systems), this is a material cost increase per [fivetran.com/docs/usage-based-pricing/pricing-updates/2026-pricing-updates](https://fivetran.com/docs/usage-based-pricing/pricing-updates/2026-pricing-updates). **Flag this when proposing Fivetran for fixed-fee consulting engagements** — invoice surprises break the fixed-fee model.

## Workflow vs ELT decision (when n8n / Zapier vs Airbyte)

- **Workflow (n8n / Zapier / Make / Activepieces):** SaaS-to-SaaS, event-driven, low-volume (thousands of events/day), destination is another SaaS app
- **ELT (Fivetran / Airbyte):** destination is a warehouse, schema-managed, hundreds-of-thousands to millions of rows

## Anti-patterns this skill flags

- Rate-limit-naive code that doesn't honor `Retry-After`
- ELT pipeline scheduled more frequently than the dashboard needs
- Salesforce / HubSpot pipeline without naming the daily-API-cap math
- Fivetran proposed for change-heavy source without flagging the 2026 deletes-count change
- Stripe batch-only when client expects real-time signals (need webhooks)
- GA4 connector spend when native BigQuery export is free
- Workflow tool (n8n / Zapier) proposed for warehouse-bound ELT at million-row volume
- Custom integration when Airbyte ships a connector (re-inventing maintenance burden)
- ELT pipeline with no documented data-handoff plan
- Storing OAuth refresh tokens in plain text in a config repo (use a secret store)

## References

- Knowledge: [`../../knowledge/ipaas-connector-landscape-2026.md`](../../knowledge/ipaas-connector-landscape-2026.md)
- Knowledge: [`../../knowledge/quickbooks-online-integration.md`](../../knowledge/quickbooks-online-integration.md)
- Template: [`../../templates/airbyte-source-config.yaml`](../../templates/airbyte-source-config.yaml)
- LMS-specific: [`../../knowledge/edtech-lms-connector-gap.md`](../../knowledge/edtech-lms-connector-gap.md)
