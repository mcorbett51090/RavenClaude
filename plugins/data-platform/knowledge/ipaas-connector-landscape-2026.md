# iPaaS connector landscape 2026

> **Last reviewed:** 2026-05-21. Sources: Fivetran docs (primary), Airbyte docs (primary), TechCrunch on M&A, secondary aggregators (Integrate.io, Costbench, Vendr). Refresh when: (a) Fivetran or Airbyte materially restructure pricing, (b) a new entrant gains meaningful market share, (c) a major M&A event (Stitch under Qlik, Catalyst under Totango precedents), or (d) a flagship source (QBO / Stripe / Salesforce / HubSpot / GA4 / Shopify) makes an API-version change that breaks existing connectors.

## Default recommendation

For a 4-6 engagement/year solo consulting practice:

- **Default ELT:** **Airbyte** (Cloud Standard $10/mo or self-hosted OSS)
- **Modeling layer:** dbt Core (free, OSS) — ships with every engagement
- **Reverse ETL (only if activation is part of the deliverable):** Hightouch free tier
- **SaaS-to-SaaS / lightweight automation:** n8n self-hosted ($3-20/mo VPS)
- **Fivetran free tier** when client takes over post-engagement AND MAR < 500k
- **Embedded iPaaS for future productized offerings:** Merge.dev (HRIS/CRM/accounting) or Apideck

**Avoid above 500k MAR on Fivetran** — the 2026 deletes-count change makes it cost-unpredictable on change-heavy sources.

## Managed ELT pricing

### Fivetran
- **MAR tiers (2026):** $2.50/M rows (0-5M), $2.00/M (5-20M), $1.50/M (20-100M), $1.00/M (100M+) [per fivetran.com/docs/usage-based-pricing](https://fivetran.com/docs/usage-based-pricing)
- **$5 base charge per connection between 1-1M MAR**
- **As of Jan 1, 2026: inserts, updates AND deletes all count toward paid MAR** (previously deletes didn't). [Per fivetran.com/docs/usage-based-pricing/pricing-updates/2026-pricing-updates](https://fivetran.com/docs/usage-based-pricing/pricing-updates/2026-pricing-updates). **This is a material cost increase for change-heavy systems (Salesforce, HubSpot deal updates).**
- **500+ pre-built connectors** including Stripe, Salesforce, HubSpot, Shopify, QuickBooks, GA4, Workday HCM/Adaptive/Financial
- **Free tier:** accounts under 500k MAR
- **HVR acquisition:** $700M, completed shortly after Sept 2021 announcement [per Fivetran press release](https://www.fivetran.com/press/fivetran-completes-acquisition-of-hvr) — brought log-based CDC into the platform

### Airbyte
- **Cloud Standard:** $10/mo with 4 credits included; additional credits $2.50 each. One credit ≈ 1/6M API rows OR 250 MB DB/files [per docs.airbyte.com](https://docs.airbyte.com/platform/cloud/managing-airbyte-cloud/manage-credits)
- **Plus tier (reported):** $25k/year via sales — Plus is capacity-based with "Data Workers" (secondary source via Integrate.io; not on Airbyte's public site)
- **600+ replication connectors + 50+ AI-workload "agent connectors"**
- **OSS (Apache + Elastic License v2):** free for self-host
- **Series B:** $150M Dec 2021. **No Series C/D found** as of mid-2026. Managed shift is real but funded out of Series B + revenue (Sacra company profile).

### Stitch (under Qlik/Talend)
- **Pricing:** Standard $100/mo (5M MAR, 1 destination, 10 sources), Advanced $1,250/mo (100M rows), Premium $2,500/mo (1B rows)
- **Status:** **Maintenance mode** under Qlik/Talend. Existing customers continue; new buyers funneled to Qlik Talend Cloud. Talend Open Studio (free) was discontinued Jan 31, 2024. (Secondary; not confirmed via primary Qlik announcement.)
- **Don't recommend for new engagements** unless client specifically wants Stitch continuity.

### Estuary Flow
- **Pricing:** $0.50/GB change data moved + $0.14/hour per active connector instance [per estuary.dev/pricing](https://estuary.dev/pricing/)
- **Positioning:** real-time CDC with sub-100ms latency and exactly-once semantics — narrower scope than Fivetran/Airbyte but cheaper for streaming workloads

### Hevo Data
- **Pricing:** Free (1M events), Starter $239/mo (5M events), Professional $679/mo (20M events) [per docs.hevodata.com](https://docs.hevodata.com/account-management/billing/pricing-plans/)
- **Event-based** — every insert/update/delete = 1 event

## Workflow / lightweight (not ELT)

### n8n
- **Self-hosted Community Edition:** free; only cost is the server ($3-20/mo VPS)
- **Cloud:** Starter $24/mo (2,500 executions), Pro $60/mo (10,000), Business reported €800/mo
- **Old free Cloud tier was removed**

### Zapier
- **Free (100 tasks/mo); Professional $19.99/mo (750 tasks, annual); Team $69/mo (2,000 tasks)** [per zapier.com/pricing](https://zapier.com/pricing)

### Make.com
- **Free (1,000 ops); Core ~$9-10.59/mo for 10k ops; Pro ~$19/mo; Teams ~$34/mo**

### Activepieces
- **Open-source Zapier alternative.** Free (1k tasks, 2 flows); Plus $25/mo (unlimited, AI agents); Business $150/mo. Apache 2.0 self-hosted.

## Reverse ETL

### Hightouch
- **Free plan; Growth ~$1,000/mo for production; median Vendr contract ~$15k/year** (Costbench, Vendr)

### Census
- **Free; Professional from ~$350/mo** (Vendr — number variance across sources)

### Polytomic
- ELT + reverse ETL + bi-directional. **From ~$500/mo published; Standard tier reported $1,500-$2,500/mo** (secondary)

## Embedded iPaaS (only relevant if Matt builds a productized offering)

### Merge.dev
- **Launch tier free for first 3 production linked accounts; $650/mo for up to 10, then $65 per additional** [per merge.dev/pricing](https://www.merge.dev/pricing)
- **220+ integrations across HRIS, ATS, CRM, accounting, ticketing, file storage**
- **SOC 2 / HIPAA / GDPR compliant**

### Apideck
- **Moved from API-call-based to consumer-based pricing in January 2026.** Unlimited API calls within tier; one customer = one consumer regardless of how many integrations.
- **Three plans (Launch, Growth, Enterprise); 30-day free trial**
- Considered the cheapest unified-API vendor

### Paragon
- **Sales-quoted; reportedly $500-$3,000+/month with annual plans starting in five figures**

### Prismatic
- **Sales-quoted; per-integration-instance pricing**

## Source-system deep dives

### QuickBooks Online
- **OAuth 2.0 Authorization Code; 1-hour access tokens; 100-day rolling refresh expiry** (notifications at 30, 7 days)
- **Rate limits:** 10 req/s per realm-ID & app; batch 120/min; concurrent ~10
- **Connectors:** Fivetran ✅, Airbyte ✅, Hevo ✅, Stitch ✅, all major workflow tools
- **QB Desktop ≠ QBO** — Desktop usually needs QB Web Connector + CData / Transaction Pro (deferred to v0.2.0 in this plugin)

### Stripe
- **All major ELT vendors ship a Stripe connector** (Fivetran, Airbyte, Hevo, Stitch, Estuary)
- **Pattern:** batch ELT for history + webhooks for real-time

### Salesforce
- **Bulk API 2.0:** 150M records/day; 15k batches/24hr; 10k records/batch; 10MB payload (Salesforce developer docs)
- All major ELT vendors support Salesforce

### HubSpot
- **Rate limits:** 110 req/10s OAuth marketplace apps; private apps 100/10s (Free/Starter) → 190/10s (Pro/Enterprise); CRM Search API capped at 4/sec; OAuth dev accounts up to 1M/day

### Google Analytics 4
- **Native BigQuery export — free, daily + streaming/intraday — the recommended path when destination is BigQuery**
- **UA is gone**; GA4 only

### Shopify
- **REST Admin API is legacy as of Oct 1, 2024**; **GraphQL Admin API required for new public apps since April 1, 2025**
- Webhooks via GraphQL `webhookSubscriptionCreate`; HTTPS / Pub/Sub / EventBridge destinations

### HRIS — Workday, BambooHR, ADP
- **Workday:** Fivetran ships HCM, Adaptive, Financial, Strategic Sourcing, RaaS connectors
- **BambooHR:** Airbyte ✅ (source + destination)
- **ADP:** thinner native ELT coverage; usually via Flexspring or Merge.dev unified API

## Direct warehouse-to-warehouse sharing (skip the iPaaS)

- **Snowflake Data Sharing:** native, zero-ETL across regions/clouds. Iceberg and Delta tables share announced 2025/2026.
- **Databricks Delta Sharing:** open protocol; first-class Iceberg support announced. 300%+ YoY usage growth (per Databricks).

**When the client says "our data is already in Snowflake" or "our data is in Databricks," the right answer is often "we'll use a data share, not build a pipeline."** Avoids the entire ELT cost line.

## Decision criteria

| Criterion | When matters |
|---|---|
| Sync frequency | Real-time → Estuary or webhooks; daily → batch ELT fine |
| Volume | Millions → ELT; thousands → workflow tool may suffice |
| Schema management | Fivetran/Airbyte ship schemas; custom = consultant models |
| PII/PHI | Merge.dev, Fivetran HIPAA BAA available; n8n self-hosted = most control |
| Cost predictability | Flat/seat = friendlier to fixed-fee consulting; per-row = invoice surprises |
| Direction | Bidirectional → Polytomic or workflow; one-way → ELT |
| Termination | Hosted → self-host risky; managed (Fivetran/Airbyte Cloud) = easier handoff |

## Recommended stack for SMB consulting

1. **Source-to-warehouse ELT:** Airbyte (Cloud Standard for short engagements; self-host for sticky deployments with engineering capacity)
2. **Warehouse:** client-dependent — BigQuery if GA4-heavy; Snowflake if enterprise SaaS; Postgres for small projects
3. **Modeling:** dbt Core — ships with every engagement
4. **Reverse ETL** (optional): Hightouch free, upgrade only if MTR volume requires
5. **Workflow / lightweight automation:** n8n self-hosted
6. **Fallback handoff-friendly:** Fivetran free tier when client has <500k MAR and wants fully managed
7. **Embedded iPaaS for productized offering:** Merge.dev (HRIS/CRM/accounting), Apideck (cost-sensitive)

## Decision tree the plugin uses

1. Source already in Snowflake / Databricks? → **Recommend data sharing, skip iPaaS**
2. Destination is another SaaS, not a warehouse? → **Workflow tool (n8n / Make / Zapier / Activepieces)**
3. Destination is warehouse, volume < 500k MAR/month? → **Fivetran free OR Airbyte Cloud Standard**
4. Destination is warehouse, volume high or sticky? → **Airbyte (self-host if firm hosts; Cloud if client takes over)**
5. Deliverable is software product ingesting other customers' data? → **Embedded iPaaS (Merge / Apideck)**
6. Bidirectional sync or warehouse-to-CRM activation? → **Add Hightouch or Census**

## Refresh triggers

- Fivetran or Airbyte material pricing restructure
- New entrant gaining >5% mid-market share
- Major M&A event (Stitch under Qlik, Catalyst under Totango precedents)
- Flagship source makes API-version change (Shopify GraphQL transition was 2024-2025)
- Open-source iPaaS (n8n, Activepieces) reaches new feature-parity milestone with Zapier/Make
