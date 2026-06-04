# Connector + Warehouse + Rendering Research — PSM Command Center (2026-06-04)

Research substrate for a Partner Success / Customer Success operational dashboard built on Snowflake, fed by Salesforce + Planhat + support tools + calendar + contract systems, surfaced to a single PSM seat.

Sources are inline `[n]` and enumerated in Section 12. `[unverified — single source]` flags any claim backed by only one source.

---

## 1. Salesforce → Snowflake replication (Fivetran vs. Airbyte vs. native)

### 1.1 The four real options

| Path | Latency floor | Cost shape | Schema-drift handling | When to pick |
|---|---|---|---|---|
| **Fivetran managed connector** | 5-min sync schedule, ~6h recommended [1][2] | Per-connector MAR (changed March 2025; bills up ~50–60% for many orgs, 2–4× for some) [3] | Auto-promotion of new columns/tables; user opts per-column [4][30] | Default. Lowest engineering cost, broadest object coverage including Service Cloud Cases [4][30]. |
| **Airbyte (cloud or OSS)** | Configurable; per-stream cursor | $2.50/credit standard plan; APIs ~$15/M rows, DBs ~$10/GB [3] | Manual schema review; OSS allows code fork | Teams with engineers + objections to Fivetran MAR pricing, or needing OSS / custom destinations (Airbyte ships 30+ destinations vs. Fivetran 15+) [3]. |
| **Salesforce Pub/Sub API + Snowpipe Streaming** (CDC) | Sub-minute, 5–10s in practice [22][23] | Compute-heavy on Kafka/connector side; Snowpipe Streaming ~70% cheaper than batch micro-loads [21] | DIY — JSON schema-on-read into VARIANT, dbt downstream | Real-time PSM trigger use cases (e.g., "Closed-Won fires a play"). Adds operational complexity [22]. |
| **Salesforce Data Cloud zero-copy share to Snowflake** | Query-time federation, no replication | Data Cloud licensing; no Snowflake ingestion compute | No drift — pushdown queries hit live SF tables [5][6][7] | When the org already runs Data Cloud and wants no replication lag. **Confirmed GA 2024-08; Salesforce-IDP auth GA 2025-09** [5][7]. |

### 1.2 Bulk API 2.0 vs Streaming/Pub-Sub — decision rule [8][9]

- **Bulk API 2.0** — periodic loads ≥2,000 records; historical backfills; nightly warehouse syncs. Handles batching internally; CSV upload, Salesforce splits. Always use 2.0 unless legacy [8].
- **Pub/Sub API (Change Data Capture)** — event-driven, sub-minute, lean payloads. Replaces deprecated Streaming API as the modern entry point [22]. Use when 5-minute latency is unacceptable; otherwise scheduled Bulk wins for cost+simplicity [9].
- **Hybrid pattern (recommended)** — Bulk for initial backfill + nightly reconciliation; Pub/Sub for the 5–10 objects (Opportunity, Case, Task) that drive real-time plays [9][22].

### 1.3 Fivetran SFDC specifics worth wiring into a PSM dashboard

- **Incremental relies on `SystemModstamp` / `LastModifiedDate`**; tables without reliable timestamps re-import wholesale [1].
- **Formula fields excluded from incremental sync** — Fivetran detects and skips them; rederive downstream in dbt [1][4].
- **Soft deletes surface as `_fivetran_deleted = TRUE`** — every staging model needs `WHERE _fivetran_deleted = FALSE` to avoid ghost accounts in PSM views [1].
- **Fivetran auto-selects Bulk vs REST** by row volume [1].
- **6-hour sync = default best practice for cost**; an 8am PSM dashboard with last-night-fresh data is well within that envelope [1].

### 1.4 Pricing-shock alert

Fivetran's March 2025 shift from account-wide MAR aggregation to **per-connector MAR billing** removed bulk discounts. Teams with many small connectors (support tools + calendar + Planhat + SFDC + CPQ) felt 50–60% bill increases; some saw 2–4× [3]. This materially changes the build-vs-buy math for the *small* connectors (calendar, CPQ, Planhat) — a custom Python+Snowpipe pipeline may now beat Fivetran on TCO for any sub-100k-row/month source. Re-run the math on every connector individually, not in aggregate.

---

## 2. Planhat extraction — managed-vs-build verdict, externalId convention, rate limits

### 2.1 Managed-vs-build verdict — **2026 UPDATE: BUILD is no longer required**

The marketplace's existing `plugins/data-platform/knowledge/planhat-integration.md` says "BUILD." That guidance is now stale.

**Planhat ships a native bidirectional Snowflake integration** [10][11][12]:

- **Static CRM data** (Company, End User, License, etc.) — bidirectional, **continuous sync at least once per hour** [11][12].
- **Time-series Metrics data** — Snowflake → Planhat only, configurable cadence **5 minutes to 24 hours** [11][12].
- **Auth** — as of **July 2025, key-pair authentication via a "service"-type user** is the recommended path (replacing OAuth + password "person" user, which is impacted by Snowflake's MFA enforcement) [12][13].
- Sync direction is independently set per model/object — supports "Send to Provider," "Receive from Provider," "Both" [12].

**Therefore:** the right pattern is *not* "build a custom Planhat→Snowflake ingest." The right pattern is:
- Use Planhat's native Snowflake integration for the bidirectional CRM-data layer.
- For event/usage telemetry not already in Snowflake, push to Planhat via the **REST bulk-upsert API** (5,000 items/request) [14][15].
- For real-time "thing happened in Planhat → react" use cases, register **webhooks** [16].
- Fivetran/Airbyte managed Planhat connectors **still don't exist as of 2026-06**; Apideck / Portable / Estuary offer wrappers but none of them beat the native Snowflake integration for the CRM path [16][17].

### 2.2 externalId / sourceId / _id hierarchy [14][18][19]

Planhat's matching/keyable hierarchy on all bulk upserts:

```
_id  >  sourceId  >  externalId   (Enduser also accepts email below externalId)
```

- `_id` — Planhat-internal MongoDB-style ID.
- `sourceId` — the foreign CRM ID. **For a SFDC-anchored shop, `sourceId` = Salesforce Account 18-char ID.** [18]
- `externalId` — the customer's own internal ID (e.g., your `partner_key` or LEAID).

**Critical implication for cross-system joins:** `sourceId` already pins the SFDC bridge. Use `externalId` for the *district-level* identity (LEAID), and the bridge to a Snowflake `partner_key` follows naturally. **Do not invert these** — Planhat's docs explicitly say "if SourceId exists on a model, it must be used as the key; otherwise externalId is used" [18][14].

Properties that *are* the keyable cannot be updated via that key — to change a Planhat record's externalId you must address it by `_id` or `sourceId` [14]. Plan migration writes accordingly.

### 2.3 Rate limits [20]

- Main REST API: **soft limit 200 req/min**; **hard limit 150 req/sec** with **bursts up to 50 parallel** [20].
- Bulk upsert: **5,000 items per request**, all models [14][20].
- Webhooks: not rate-limited from Planhat's side; consumer must absorb spikes. Idempotency key is the model's `_id`.

### 2.4 Idempotent MERGE pattern into Snowflake

When pulling Planhat via REST (e.g., for history beyond the native integration's window) and landing in Snowflake:

```sql
MERGE INTO analytics.dim_partner AS tgt
USING staging.planhat_company AS src
   ON tgt.planhat_id = src._id        -- _id is the strongest key
WHEN MATCHED AND tgt.updated_at < src.updated_at THEN UPDATE SET …
WHEN NOT MATCHED THEN INSERT (…) VALUES (…);
```

Match on `_id` only — `sourceId` and `externalId` can change over a record's lifetime and will cause double-rows. [unverified — derived from Planhat's documented keyable hierarchy [14], not a Planhat-published MERGE template]

---

## 3. Snowflake operational-dashboard patterns

### 3.1 Layer pick — Dynamic Tables now dominate

Dynamic Tables replaced the manual Streams + Tasks pattern for declarative incremental pipelines in 2024–2025 and are now the default substrate for an operational dashboard layer [24][25][26][27].

| Layer | Refresh floor | Snowsight observability | Use for |
|---|---|---|---|
| **Dynamic Tables** | 1-minute (15s in preview) [24][25] | Lag, refresh history, dependency DAG built-in [25][26] | Continuous transforms (e.g., `tickets_aging`, `health_score_components`) feeding the dashboard. **Default choice.** |
| **Streams + Tasks** | Sub-minute possible | Manual instrumentation | Edge cases Dynamic Tables don't cover (complex stateful logic, MERGE-with-side-effects). Treat as the escape hatch. [25][27] |
| **Snowpipe Streaming** | ~5 seconds [21][23] | Snowpipe insights tables | Sub-minute ingest path (event-grade). Pair with Dynamic Tables downstream. |
| **Interactive Tables / Interactive Warehouses (GA Dec 2025)** [25][32] | Sub-second query latency | Dedicated for high-concurrency dashboards | Real-time dashboards and "data-powered APIs." Pay-per-query premium; use selectively for the hottest 5–10 panels [32]. |

### 3.2 Clustering keys — partner-keyed access pattern

For a PSM dashboard that filters by `partner_key` on every panel, the clustering key should be `(partner_key, event_date)` or similar [33][34][35]. Best-practice rules of thumb:

- **Cluster only the top 5% largest tables that drive ≥80% of scan cost** [34][37].
- Use `SYSTEM$ESTIMATE_AUTOMATIC_CLUSTERING_COSTS` before committing — actual costs can be ±50% from estimate, in rare cases multiple-X [35][39].
- Combine `DATE_TRUNC('day', …)` filters + entity_id filters in the cluster key; this is the most common dashboard query shape [37].
- **Most teams waste 30–50% on Snowflake compute due to poor clustering** [33] — this is the #1 cost lever on a dashboard that hits the warehouse every page load.

### 3.3 Cost control on a "PSM opens the dashboard every morning" pattern

- **Result caching covers identical queries for 24h** — design the dashboard's morning view so all PSMs hit the cache (parameterize on user only for personalization, not on time-bucket). [38]
- **Use `INFORMATION_SCHEMA` not `ACCOUNT_USAGE`** for any live telemetry panels — latency ~minutes vs ~90 minutes for `ACCOUNT_USAGE` [49].
- **Search Optimization Service** — for high-cardinality point lookups (e.g., "search for partner by district name"). Estimates via `SYSTEM$ESTIMATE_SEARCH_OPTIMIZATION_COSTS`; actuals can drift ±50% [54]. Start with one column on one table and monitor before broadening [54].

---

## 4. Support-tool ingestion — per-vendor connector + schema shape

### 4.1 Zendesk [40][41][42][43]

- **Fivetran connector** — first-class. Syncs `TICKET`, `TICKET_METRIC_EVENTS`, `TICKET_FIELD_HISTORY`, `SLA_POLICY`, `DAYLIGHT_TIME`, `TIME_ZONE` [40][41]. The `TIME_ZONE`/`DAYLIGHT_TIME` tables are essential for accurate SLA-breach calculation across DST [40][41].
- **`fivetran/zendesk` dbt package** — ships ticket-aging + calendar-hour and business-hour SLA breach derivations out-of-the-box [40][43].
- **`ORGANIZATION_MEMBERSHIP` and `AUDIT_LOG` are deselected by default** — large, perf-sensitive [40].
- **Airbyte alternative** — 99% SLA on GA connectors; supports same source [42].

### 4.2 Freshdesk [44]

- **Fivetran connector** — schema applies to all connections after 2023-01-10 [44].
- **`TICKET` table is deselected by default**; if you opt in after initial sync, history reimports from epoch [44].
- **`TIME_ENTRIES` + `TICKET_HISTORY` sync incrementally via webhooks**; deletes captured by full reimport once weekly [44].

### 4.3 Intercom [44]

- **Fivetran connector** — first-class.
- **`COMPANY_HISTORY`, `COMPANY_TAG_HISTORY` not incremental** at the Intercom API level — reimported weekly [44].
- Cross-reference the existing `plugins/data-platform/knowledge/intercom-integration.md`.

### 4.4 Salesforce Service Cloud [4][30]

- **Already covered by the SFDC Fivetran connector** — `CASE`, `CASE_HISTORY`, `CASE_COMMENT` come for free [30][4]. The `Case` object is in the same MAR pool as the rest of SFDC, so no incremental connector cost — a meaningful Fivetran-pricing-era advantage.
- **`Case.ClosedDate - Case.CreatedDate` for ticket aging**; `Case.SlaStartDate` / `Case.SlaExitDate` for breach detection where Entitlements/Milestones are configured.

### 4.5 Jira Service Management [45]

- **Fivetran Jira connector covers JSM** — issues, sprints, users [45].
- **`fivetran/jira` dbt package** ships transforms for BigQuery / Snowflake / Redshift / Databricks / Postgres [45].
- For native JSM-specific objects (request types, queues, SLAs), Airbyte's Jira connector has parity but requires manual modeling [45].

### 4.6 HubSpot Service Hub [46]

- **HubSpot ships a native Snowflake Data Share** — `V2_LIVE` schema refreshed every 15 minutes; `V2_DAILY` daily; subset of `V2_LIVE` views (`association_definitions`, `owners`, `pipelines`, `pipeline_stages`) are daily-only [46].
- **No connector compute cost** — it's a Snowflake share, billed by HubSpot tier, not by row volume [46]. Strongly prefer over Fivetran HubSpot when the org is on Service Hub.

### 4.7 Ticket-aging + SLA-breach derivation (cross-vendor pattern)

| Metric | Derivation rule (warehouse-side) |
|---|---|
| `ticket_age_hours` | `DATEDIFF('hour', created_at, COALESCE(closed_at, CURRENT_TIMESTAMP()))` filtered to business hours via vendor `BUSINESS_HOURS` calendar [40][41] |
| `sla_breached` | `sla_policy.target_minutes < ticket_age_business_minutes AND status != 'closed'` |
| `time_to_first_response` | `MIN(public_comment.created_at) - ticket.created_at` |
| `reopen_count` | `COUNT(status_change WHERE prev_status='solved' AND new_status='open')` |

Per-vendor SLA semantics differ (Zendesk SLA policies vs. SFDC Entitlements vs. HubSpot pipelines) — normalize into a `fact_support_ticket` dim at the dbt layer, do not push the difference up to the dashboard.

---

## 5. Contract-system ingestion — per-vendor

### 5.1 Salesforce CPQ (default if the org runs SFDC) [47][48]

- **Already in the SFDC Fivetran feed** — `Quote`, `QuoteLineItem`, `Contract`, `ContractLineItem`, `Order`, `OrderProduct`, and CPQ-managed objects (`SBQQ__*` namespace) flow with the standard SFDC connector [47][30].
- **Field mapping for partner-success metrics:**

| Metric | Field source (CPQ → Contract → Account roll-up) |
|---|---|
| ARR | Sum of `OpportunityLineItem.SBQQ__AnnualAmount__c` or `Contract.SBQQ__AmountRolledUp__c` (annualized MRR × 12) [47][48] |
| TCV | `Contract.ContractTermLength` × ARR + one-time line items; CPQ field `SBQQ__SubscriptionTerm__c` [48] |
| Renewal date | `Contract.EndDate` — NOT `Contract.RenewalDate` (which is auto-renewal target, often null) [48] |
| Termination-notice date | `Contract.EndDate - Contract.TerminationNoticeDays` — a derived field; warehouse-side compute [48] |
| PD purchased/used/remaining | Almost always custom fields (`Account.PD_Hours_Purchased__c` etc.) — confirm in each org |
| Multi-year clause | `Contract.SBQQ__SubscriptionTerm__c > 12` OR presence of `SBQQ__AmendmentStartDate__c` |

### 5.2 Ironclad CLM [50]

- **API-first** — `developer.ironcladapp.com`. Bulk-export endpoints; AI-extraction of clauses on ingest [50].
- **No managed Fivetran/Airbyte connector as of 2026-06** — BUILD via REST + Snowpipe.
- **Renewal-date extraction** is Ironclad's strength — Ironclad AI returns structured clauses (renewal_date, notice_period, auto_renewal_flag) from PDFs [50]. Land these into a `dim_contract_clauses` table.

### 5.3 DocuSign CLM (Insight) [50]

- **Insight is the post-signature intelligence layer** — term extraction, obligation tracking, renewal alerts [50].
- **REST API + Webhook (DocuSign Connect)** — webhooks for envelope status changes; REST for envelope/clause pulls.
- **No managed connector** — BUILD via REST + webhook → S3 → Snowpipe → Snowflake. Same pattern as Ironclad.

### 5.4 Conga CLM (and Conga Contracts) [55]

- REST API documented at `documentation.conga.com` [55].
- No managed Fivetran/Airbyte. BUILD path.
- For SFDC-anchored Conga deployments, `Contract` and Conga's custom objects flow through the SFDC connector — verify the namespace before assuming BUILD is required.

### 5.5 ContractWorks / vaquill / smaller CLMs [50]

- Generally REST-API + webhook. BUILD pattern. Single-source viability since they typically don't appear in connector catalogs [50].

### 5.6 Cross-vendor normalization

Define `dim_contract` at the dbt layer with vendor-agnostic columns: `partner_key`, `contract_start_date`, `contract_end_date`, `arr_usd`, `tcv_usd`, `auto_renew_flag`, `notice_period_days`, `clm_source`, `clm_source_id`. This is where SCD Type 2 (see §8.2) lives — contract amendments are exactly the workload SCD2 was designed for [60].

---

## 6. Calendar ingestion — Google / Outlook / Calendly / Chili Piper

### 6.1 Google Calendar API [51][52]

- `events.list` is the workhorse — supports `updatedMin` for incremental pulls.
- **RFC 3339 string timestamps** with offset; trivially Snowflake-castable.
- OAuth 2.0 with domain-wide delegation for org-wide ingest [51].
- No managed Fivetran connector for raw calendar events; Airbyte has one (community-supported). BUILD path is typical [51].

### 6.2 Microsoft Graph (Outlook) [51][52]

- `/me/calendarView` for time-bounded reads with auto-expansion of recurring events [52].
- **`dateTime + timeZone` object** (NOT RFC 3339 with offset) — must reassemble in your ingest [51][52].
- Use `Prefer: outlook.timezone="UTC"` header to force UTC-returned events; eliminates DST math at ingest time [51][52].
- Bugs to watch: DST-boundary event creation, Graph returning local-time stamps without offset on some endpoints [52]. Use **IANA timezone names** end-to-end [52].
- **Google ↔ Outlook calendar interoperability via Graph API GA May 2025** — relevant if your PSMs have mixed Gmail/Outlook accounts [51].

### 6.3 Calendly / Chili Piper / Reclaim.ai [53]

- **Calendly** — REST API with full webhook coverage; documented event-types `invitee.created`, `invitee.canceled`. Strong for inbound prospect/partner scheduling [53].
- **Chili Piper** — REST API; strength is real-time lead routing/qualification. CSV export of meetings activity is the documented data-pull path [53].
- **Reclaim.ai** — practitioner-facing layer; doesn't add new data — surfaces existing Google Calendar via its own UI. Skip from ingest perspective.

### 6.4 Timezone normalization — the cross-state K-12 gotcha

K-12 partners span all US timezones plus DST/non-DST regions (Arizona, Hawaii). Pattern:

1. Store all calendar events in **UTC** in Snowflake (`event_start_utc TIMESTAMP_TZ`).
2. Store the partner's `timezone_iana` (e.g., `America/Chicago`) on `dim_partner`.
3. Compute `event_start_local = CONVERT_TIMEZONE('UTC', dim_partner.timezone_iana, event_start_utc)` at query time.
4. Never store local time without timezone — it loses DST context [51][52].

Microsoft Graph DST bugs are documented and persistent — defend against them with assertion tests in dbt (e.g., "no event_start_utc < event_end_utc" or "no events whose duration changed by exactly 1h around DST transition without a corresponding update_time") [52].

---

## 7. Cross-system identity resolution — district matching, LEAID, confidence tiers

### 7.1 The four identity domains to reconcile

| Domain | Identifier | Stability |
|---|---|---|
| Salesforce | `Account.Id` (18-char) | Stable forever |
| Planhat | `Company._id` (MongoDB ObjectId), `Company.sourceId` (= SFDC ID) | Stable; `sourceId` is the SFDC bridge [18] |
| Snowflake | `partner_key` (synthetic surrogate) | Yours to assign |
| State DOE | **LEAID** (7-digit NCES Local Education Agency ID) | Stable per NCES; changes on district consolidation [56][57] |
| School-level | NCES School ID (12 digits = LEAID + SCHNO) | Stable per NCES [56][57] |

### 7.2 LEAID structure [56][57]

- **7 digits, first 2 = State FIPS code.** A Texas district always starts with `48`, Wisconsin with `55`, etc.
- Updated annually via NCES Common Core of Data (CCD).
- **Public lookup tool** — `nces.ed.gov/ccd/districtsearch/` — programmatic flat-file at `nces.ed.gov/ccd/ccddata.asp` [56].

### 7.3 Confidence-tier pattern (deterministic → probabilistic) [58][59]

| Tier | Match logic | Confidence | Action |
|---|---|---|---|
| **T0 — Exact ID** | SFDC `Account.NCES_LEAID__c` populated AND matches `dim_lea.leaid` | 100% | Auto-link. |
| **T1 — Deterministic compound** | `(state_fips, normalized_district_name, city)` exact match | ~95% | Auto-link with audit log [58]. |
| **T2 — Fuzzy district name** | Levenshtein/Jaro on normalized name within state; threshold ≥0.92 [59][61] | 85–95% [58] | Auto-link, flag for review at first sync. |
| **T3 — Probabilistic** | Multi-signal: name + city + zip + enrollment-band agreement | 70–85% | Queue for human review; do not auto-link. |
| **T4 — Below threshold** | <70% | — | Reject; surface as unmatched. |

**Industry-standard threshold for deterministic-vs-probabilistic boundary is 85–95%** [58]. Devicre/IP probabilistic peaks at 75–85% for cross-session same-device; cross-device 60–70% [58]. Apply tighter thresholds for B2B district matching because the entity universe is smaller and the cost of a wrong match is higher.

### 7.4 Implementation pattern (dbt + Snowflake)

- `seed_nces_districts.csv` (or Snowflake share / S3 pull) → `dim_lea` materialized monthly.
- `int_district_match__sfdc_to_lea.sql` — stage of stages, one CTE per tier. Surface `match_tier` + `match_confidence` on the final mart row.
- Reuse the existing `plugins/data-platform/skills/cross-system-identity-resolution/` skill — **enhance** with this confidence-tier scaffold and the LEAID-specific normalization rules (strip "Public Schools," "School District," "ISD" suffixes; normalize "Saint" / "St." / "St"; uppercase + collapse whitespace before fuzzy compare).

### 7.5 Gotcha — district consolidation/split

LEAIDs change on consolidation. Keep `dim_lea` SCD2 (effective_from / effective_to) and join through `dim_lea` rather than embedding LEAID directly in fact tables. The fact table holds `partner_key`; the join chain `fact → dim_partner → dim_partner_lea_link → dim_lea` survives consolidation [56].

---

## 8. dbt + semantic layer for CS metrics — where formulas live

### 8.1 The three semantic-layer contenders [62][63][64]

| Tool | Where metrics live | Strongest with | Weakness |
|---|---|---|---|
| **dbt Semantic Layer / MetricFlow** | YAML in dbt project, version-controlled, PR-reviewed [62][63] | Any tool via the dbt Cloud API (Mode, Hex, Tableau via partner connections) | Locked to dbt Cloud for live consumption; OSS query path is more limited |
| **Cube (Cube Core)** | YAML or JS schema in your repo; exposed via SQL/REST/GraphQL APIs [64] | Embedded analytics, React/Next.js apps, custom dashboards, multi-tenant SaaS [64] | Another service to operate; smaller surface than dbt for warehouse-side modeling |
| **LookML (Looker)** | LookML files | Looker dashboards | Locked inside Looker — "leave Looker, leave your metric layer" [63] |

**Both dbt and Cube joined the OSI (Open Semantic Interchange) initiative in 2025** — metric definitions are becoming portable [64].

### 8.2 Where the priority-score / health-score formula should live

For RavenClaude's PSM use case (Snowflake warehouse, eventual React-or-Hex dashboard, dbt already in the stack):

- **Single source of truth at the dbt model layer** (`fct_partner_health.sql`) — produces a materialized score column per partner per snapshot date.
- **Semantic layer (MetricFlow OR Cube) on top** — exposes derived metrics like `avg_health_30d`, `pct_partners_at_risk` to the dashboard.
- **Do NOT define the score arithmetic in two places.** The most common drift pattern is "the dashboard says 7.2, the dbt model says 7.4." Source: every dbt-Labs case study on metric ownership [62][63].

**SCD Type 2 for contract-state history** — `dim_contract` snapshot via dbt's built-in `snapshots` directive [60]. Strategy: `timestamp` on `LastModifiedDate` (cheap, requires reliable timestamp) preferred over `check_cols` (expensive row-by-row compare) [60].

### 8.3 Health-score factor sources (mapped to Section 11 deliverables)

Planhat documents the standard Health Profile factor set [29]:

- System & custom CRM fields (from SFDC + Planhat sync).
- Metrics (time-series — usage, MAU, license utilization).
- End-User Global Filters (engagement, login frequency).
- Comparison operators: lt, gt, eq, ne, linear, linear-bounded [29].

Mirror this factor model in the warehouse so the dashboard can show "why did the score change" without round-tripping to Planhat [29].

---

## 9. Rendering layer comparison

### 9.1 The five practical paths [65][66][67][68][69]

| Tool | Auth story | Shipped-against-Snowflake speed | Cost | When to pick |
|---|---|---|---|---|
| **Evidence.dev** | Code-first; SQL + Markdown; static site or cloud deploy [65] | Hours-to-days for a v1 [65] | OSS free; cloud paid | Markdown-and-SQL natives; static-site deployment; minimal infra |
| **Apache Superset** | Self-hosted; row-level security; 70k+ GitHub stars [65][66] | Days-to-weeks (more setup) | OSS; infra cost | Heavy-duty BI, large user base, need SQL Lab + role-based dashboards |
| **Metabase** | Self-hosted or cloud; non-SQL users can build dashboards [65][66] | Hours-to-days | OSS or hosted | Mixed-skill audience; non-SQL business users self-serving |
| **Hex** | SaaS; SSO; Snowflake-native (Elite Partnership) [67] | Hours [67] | Per-seat | Operational dashboards with notebook-grade flexibility; uses Snowpark; Mercor case study tracks 60+ metrics across hundreds of projects [67] |
| **Streamlit in Snowflake (SiS)** | Lives in Snowflake; uses Snowflake auth [49] | Hours | Snowflake compute only | Internal tool, zero infra, single-vendor lock-in OK |
| **React + Tremor + Recharts** | DIY (Auth0, Clerk, NextAuth, custom JWT) [68] | Days-to-weeks for v1 | Engineering time | Pixel-perfect operational console, embedded multi-tenant, full control of UX. Tremor acquired by Vercel; "Tremor Raw" actively developed as of Jan 2025 [68] |
| **Cube + React** | Cube handles auth/RLS; React renders [64] | Days for v1 [64] | Cube licensing + engineering | Embedded analytics; multi-tenant SaaS; sub-second P95 at 1s on Snowflake claim [64] |

### 9.2 Recommendation for the PSM-command-center pattern

Two viable paths:

**Path A — Hex (fastest)**
- v1 in a week.
- Pre-built notebook → dashboard transition.
- Cost per PSM seat, scales linearly.
- Trade-off: vendor lock; notebook idioms not always operational-console idioms.

**Path B — Streamlit in Snowflake or React+Tremor (most controllable)**
- v1 in 2–4 weeks.
- SiS: no infra, single-vendor. React: maximum UX control, multi-tenant out-of-the-box [68].
- Trade-off: more engineering up front; the design pays back when PSM-specific affordances (snooze, escalate, assign, snooze-until) need to ship.

**Avoid Path C (Superset)** for a single-PSM operational console — it's optimized for a large analyst population, not a five-PSM team [65][66].

---

## 10. ELT freshness SLA patterns for operational dashboards

### 10.1 Design the SLA before designing the pipeline [70][71]

A real-time-dashboard SLA specifies [70][72]:

- **Freshness target** — "data must be ≤N minutes old."
- **Availability** — typically 99.9% [70].
- **Monitoring mechanism** — how breach is detected.
- **Escalation procedure** — who gets paged.
- **Consequences** — what the SLA buys; what its breach costs.

For "PSM opens dashboard at 8am, needs last-night-fresh," realistic SLA:

- Freshness ≤ 2 hours during business hours [unverified — practitioner heuristic]
- Availability 99.5% [unverified — common SaaS baseline]
- Stale-data warning visible if freshness > 4 hours.

### 10.2 Freshness telemetry — what to instrument [70][71][73][74]

1. **`max(source_event_time)` per fact table** — pipeline success ≠ fresh data; a pipeline can succeed against a stalled source and load nothing new [71].
2. **dbt source freshness checks** (built-in) — declare expected `loaded_at_field` and `warn_after`/`error_after` thresholds [73][74].
3. **Elementary OSS** layered on dbt — `freshness_anomalies` test detects drift vs historical baseline; sends Slack/Teams alerts [73][74].
4. **Snowflake `FRESHNESS()` system data metric function** — table-level freshness as a SQL primitive [70].

### 10.3 Stale-data warning UX patterns [70][72]

Smashing Magazine's 2025 "UX strategies for real-time dashboards" piece [72] codifies:

- **Three-state badge** — "Live / Stale / Paused" — analysts get detailed update logs; business users get the simple state [72].
- **Manual refresh button + freshness timestamp** ("data as of 03:12 EST") visible per panel — improves transparency, reinforces user control [72].
- **Freshness independent of latency** — fast query against stale data is the silent killer; surface staleness explicitly [71].

### 10.4 The composite pattern for a PSM dashboard

```
Salesforce/Planhat/Zendesk → Fivetran (or Planhat-native share)
   → Snowflake raw layer
   → dbt staging + facts (with source freshness checks declared)
   → Dynamic Tables for hot rollups
   → Elementary observability → Slack alerts
   → Hex / Streamlit / React renders with three-state freshness badge
```

Every panel renders its own "data as of <timestamp>" using `MAX(loaded_at)` from the underlying fact table; the badge color is computed from that vs SLA threshold [70][72].

---

## 11. Recommended RavenClaude enhancements

The marketplace already has substantial coverage. Section 11 is **surgical augmentation**, not duplication.

### 11.1 `plugins/data-platform/knowledge/planhat-integration.md` — UPDATE (do not duplicate)

Current file says "BUILD." This is stale.

**Replace the "Connector availability" section with:**

```markdown
## Connector availability (verified 2026-06-04)

**Native Snowflake integration: YES** — bidirectional for CRM data (continuous, ≥hourly),
Snowflake→Planhat for time-series Metrics (5min–24h). Auth: key-pair via service-type
user (recommended since 2025-07; OAuth+password "person" user being deprecated due to
Snowflake MFA enforcement). See https://help.planhat.com/en/articles/9586985.

**Fivetran/Airbyte managed connector: NO** (as of 2026-06).

**REST API: YES** — for time-series/event push and out-of-band history pulls.
- Soft limit 200 req/min, hard 150 req/sec, bursts ≤50 parallel.
- Bulk upsert: 5,000 items/request, all models.

**Webhooks: YES** — for real-time event-driven reactions.

**Keyable hierarchy (used for all bulk-upsert matching):**
   _id  >  sourceId  >  externalId   (Enduser also accepts email below externalId)
- _id     — Planhat MongoDB-style internal ID
- sourceId — the foreign CRM record ID (= SFDC Account 18-char ID in SFDC-anchored shops)
- externalId — your own internal ID (e.g., partner_key or LEAID)

A property that IS the keyable cannot be updated via that key — you must address the
record by a higher-priority key to mutate it.
```

### 11.2 `plugins/data-platform/knowledge/salesforce-cpq-integration.md` — NEW

Gap: existing `salesforce-integration.md` covers core SFDC. CPQ field mapping for ARR/TCV/renewal is not documented.

Content sketch:

- CPQ object hierarchy (Quote → QuoteLineItem → Contract → ContractLineItem → Order → OrderProduct).
- `SBQQ__*` namespace overview.
- ARR / TCV / renewal-date / termination-notice-date field-mapping table (from §5.1 above).
- SCD Type 2 modeling for contract amendments (dbt snapshot recipe).
- Common gotcha: `Contract.RenewalDate` is the auto-renewal target (often null), not the renewal date.

### 11.3 `plugins/data-platform/knowledge/clm-integration-ironclad-docusign.md` — NEW

Gap: contract systems beyond SFDC CPQ have no coverage.

Content sketch:

- Ironclad API + AI-clause extraction; webhook-driven ingest pattern.
- DocuSign CLM Insight; REST + Connect webhook pattern.
- Conga CLM (SFDC-anchored vs. standalone).
- ContractWorks / smaller CLMs — generic REST+webhook → S3 → Snowpipe pattern.
- Cross-vendor `dim_contract` normalization schema (vendor-agnostic columns).

### 11.4 `plugins/data-platform/knowledge/calendar-integration-google-outlook.md` — NEW

Gap: no calendar coverage in the current knowledge base.

Content sketch:

- Google Calendar API (`events.list` + `updatedMin`, RFC 3339, OAuth DwD).
- Microsoft Graph (`/me/calendarView`, `dateTime+timeZone` object, `Prefer: outlook.timezone` header, DST bugs).
- Calendly + Chili Piper REST + webhooks.
- Timezone normalization pattern (UTC storage + `CONVERT_TIMEZONE` at query time + dim_partner.timezone_iana).
- The K-12 cross-state DST gotcha (Arizona, Hawaii).
- dbt assertion tests for DST-boundary integrity.

### 11.5 `plugins/data-platform/knowledge/snowflake-operational-dashboard-patterns.md` — NEW

Gap: `cloud-database-landscape-2026.md` is general; nothing covers the Dynamic Tables / Streams+Tasks / Snowpipe Streaming / Interactive Tables decision specifically for operational dashboards.

Content sketch:

- Layer decision table (§3.1 above).
- Clustering key strategy for partner-keyed access patterns (§3.2).
- Dashboard-cost-control playbook (§3.3).
- Search Optimization Service when to enable.
- Row Access Policy + entitlements-table pattern for multi-PSM scoping (cross-reference `multi-tenant-rls-patterns.md`).

### 11.6 `plugins/data-platform/knowledge/elt-freshness-sla-patterns.md` — NEW

Gap: data-quality skill exists but freshness-SLA-for-operational-dashboards is not directly addressed.

Content sketch:

- Freshness vs. latency distinction.
- The 5-element SLA template (§10.1).
- dbt source freshness + Elementary freshness_anomalies recipe.
- Snowflake `FRESHNESS()` SDMF.
- Three-state stale-data UX pattern.
- Composite pipeline diagram (§10.4).

### 11.7 `plugins/data-platform/skills/cross-system-identity-resolution/SKILL.md` — UPDATE

Skill exists; extend with the LEAID-specific confidence-tier scaffold (§7.3, 7.4 above):

- Add a "K-12 LEAID matching" section.
- Drop in the four-tier (T0/T1/T2/T3) ladder with the 92% Levenshtein threshold and the district-name normalization rules.
- Reference `seed_nces_districts.csv` source (NCES CCD flat file).
- Document the SCD2 `dim_lea` pattern for consolidation/split survivability.

### 11.8 `plugins/data-platform/skills/support-ticket-normalization/SKILL.md` — NEW

Gap: no skill walks an agent through normalizing Zendesk + Freshdesk + SFDC Service Cloud + Jira SM + HubSpot Service into a single `fact_support_ticket`.

Content sketch (skill workflow):

1. Identify which support vendors are in the org.
2. Per vendor, declare canonical fields: `ticket_id`, `partner_key`, `created_at`, `closed_at`, `status`, `priority`, `sla_breached`, `time_to_first_response_min`, `reopen_count`.
3. Generate the per-vendor `stg_<vendor>__tickets.sql`.
4. Union into `int_support_tickets__unioned.sql`.
5. Materialize as `fact_support_ticket` with vendor-agnostic semantics.
6. Add dbt tests: `not_null(partner_key, created_at)`, `accepted_values(status, [...])`, source freshness ≤24h.

### 11.9 `plugins/data-platform/skills/contract-renewal-rollup/SKILL.md` — NEW

Gap: ARR/TCV/renewal-date rollups across CPQ + CLM systems have no skill.

Content sketch (skill workflow):

1. Identify the contract systems in scope (SFDC CPQ, Ironclad, DocuSign CLM, etc.).
2. Map to canonical `dim_contract` schema (per §5.6).
3. Build SCD2 snapshot on `LastModifiedDate` timestamp strategy.
4. Derive `arr_usd`, `tcv_usd`, `days_to_renewal`, `auto_renew_flag`, `notice_window_open` at the fact layer.
5. Add tests: ARR ≥ 0; renewal_date > start_date; sum(arr_per_account) reconciles to SFDC roll-up within ±1%.

### 11.10 `plugins/edtech-partner-success/` — CALL-OUT (data dependencies)

The edtech-partner-success plugin should explicitly document **which Section-11 data-platform knowledge files are prerequisites** for any agent recommending a PSM dashboard architecture. Add a `data-dependencies.md` (or extend the plugin's CLAUDE.md):

- LEAID identity resolution → §11.7
- CPQ field mapping for ARR/TCV → §11.2
- Calendar ingestion for partner-touch metrics → §11.4
- Support-ticket normalization → §11.8
- Contract renewal rollup → §11.9

This prevents the edtech plugin from re-deriving the same patterns and keeps the boundary clean (edtech = domain semantics; data-platform = warehouse mechanics).

### 11.11 `plugins/data-platform/skills/rendering-layer-selection/SKILL.md` — NEW (or extend `stack-selection`)

Gap: `stack-selection` is general; this captures the §9 decision specifically for "PSM operational console against Snowflake."

Content sketch:

- Decision tree: notebook-friendly team → Hex; single-vendor OK → Streamlit in Snowflake; multi-tenant embedded → Cube + React; pixel-perfect UX → React + Tremor; mixed-skill BI users → Metabase; heavy analyst pop → Superset; markdown-first → Evidence.
- Time-to-v1 estimate per path.
- Cost-shape table.

---

## 12. Source ledger

All URLs accessed **2026-06-04**.

1. https://fivetran.com/docs/connectors/applications/salesforce — Fivetran Salesforce schema docs.
2. https://www.fivetran.com/learn/salesforce-to-snowflake — Fivetran SFDC→Snowflake guide.
3. https://portable.io/learn/fivetran-vs-airbyte-comparison — Fivetran vs Airbyte 2025 head-to-head incl. March 2025 MAR pricing change.
4. https://www.phdata.io/blog/how-to-use-fivetran-to-ingest-salesforce-data-into-snowflake/ — phData Fivetran SFDC patterns.
5. https://developer.salesforce.com/blogs/2024/08/zero-copy-data-federation-with-snowflake-and-salesforce-data-cloud — Salesforce Data Cloud zero-copy GA blog.
6. https://www.salesforce.com/data/connectivity/zero-copy/ — Salesforce Data Cloud zero-copy product page.
7. https://www.salesforceblogger.com/2025/09/08/connect-data-cloud-to-snowflake-using-salesforce-idp/ — Sept 2025 IDP auth for Data Cloud↔Snowflake.
8. https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/bulk_api_2_0.htm — Salesforce Bulk API 2.0 docs.
9. https://sfdcdevelopers.com/2025/10/29/salesforce-integration-patterns-types-use-cases-and-best-practices/ — Salesforce integration patterns 2025.
10. https://www.planhat.com/integrations/snowflake — Planhat Snowflake integration product page.
11. https://help.planhat.com/en/articles/9587348-preparing-snowflake-and-connecting-the-integration — Planhat Snowflake prep guide.
12. https://help.planhat.com/en/articles/9586985-setting-up-the-snowflake-integration — Planhat Snowflake setup guide.
13. https://www.planhat.com/developers/api/authentication-limits — Planhat API auth + limits.
14. https://www.planhat.com/developers/api/bulk-upsert — Planhat bulk-upsert API + keyable hierarchy.
15. https://github.com/robocorp/robocorp-planhat/blob/main/docs/api/planhat.md — Robocorp Planhat client (third-party reference for API shape).
16. https://www.apideck.com/integrations/planhat — Apideck Planhat integration wrapper.
17. https://portable.io/connectors/planhat/snowflake — Portable.io Planhat→Snowflake connector listing.
18. https://help.planhat.com/en/articles/9587186-external-ids-source-ids-related-domains — Planhat external ID/source ID docs.
19. https://help.planhat.com/en/articles/9587130-setting-up-the-salesforce-integration — Planhat ↔ Salesforce integration setup.
20. https://www.planhat.com/developers/api/authentication-limits — Planhat rate limits (200 req/min soft, 150 req/sec hard, 50 parallel burst, 5000 items/bulk).
21. https://estuary.dev/blog/reduce-snowflake-ingestion-costs/ — Snowpipe Streaming up to 70% cost cut vs batch.
22. https://www.striim.com/blog/change-data-capture-salesforce-real-time-integration-guide/ — Salesforce CDC + Pub/Sub overview.
23. https://streamkap.com/blog/snowflake-snowpipe-streaming-with-change-data-capture-cdc — Snowpipe Streaming + CDC ~5s latency.
24. https://www.snowflake.com/en/blog/dynamic-tables-delivering-declarative-streaming-data-pipelines/ — Snowflake Dynamic Tables blog (1-min latency, 15s preview).
25. https://docs.snowflake.com/en/release-notes/2025/other/2025-12-11-interactive-tables-ga — Snowflake Interactive Tables/Warehouses GA Dec 2025.
26. https://www.snowflake.com/en/developers/guides/cdc-snowpipestreaming-dynamictables/ — Snowpipe Streaming + Dynamic Tables CDC quickstart.
27. https://www.tothenew.com/blog/from-tasks-and-streams-to-tranquility-my-first-real-project-with-snowflake-dynamic-tables/ — Streams+Tasks→Dynamic Tables migration retrospective.
28. https://www.tredence.com/blog/unleash-the-power-of-dynamic-tables-in-snowflake — Dynamic Tables guide 2025.
29. https://help.planhat.com/en/articles/9587310-set-up-your-health-score-profiles — Planhat Health Score Profile factors and operators.
30. https://fivetran.com/docs/connectors/applications/salesforce — Fivetran SFDC schema incl. Service Cloud Case.
31. https://www.fivetran.com/blog/fivetran-vs-airbyte-features-pricing-services-and-more — Fivetran's published comparison.
32. https://www.snowflake.com/en/engineering-blog/snowflake-interactive-analytics-spring-2026-updates/ — Snowflake Interactive Analytics Spring 2026 features (sub-second latency).
33. https://keebo.ai/2025/11/03/snowflake-clustering-keys-optimization — "30–50% wasted on poor clustering."
34. https://seemoredata.io/blog/implementing-cluster-keys-for-snowflake-optimization/ — Cluster key implementation guidance.
35. https://docs.snowflake.com/en/sql-reference/functions/system_estimate_automatic_clustering_costs — `SYSTEM$ESTIMATE_AUTOMATIC_CLUSTERING_COSTS` reference.
36. https://docs.snowflake.com/en/user-guide/tables-clustering-keys — Snowflake clustering keys docs.
37. https://www.e6data.com/query-and-cost-optimization-hub/snowflake-query-optimization — Snowflake query optimization 2025.
38. https://seemoredata.io/blog/snowflake-cost-optimization-top-17-techniques-in-2025/ — Snowflake cost optimization techniques.
39. https://docs.snowflake.com/en/user-guide/search-optimization/cost-estimation — Search Optimization cost estimation (±50% drift).
40. https://fivetran.com/docs/connectors/applications/zendesk — Fivetran Zendesk schema docs.
41. https://fivetran.com/docs/transformations/data-models/zendesk-support-data-model — Fivetran Zendesk dbt data model.
42. https://airbyte.com/connections/zendesk-support-to-snowflake — Airbyte Zendesk→Snowflake (99% GA SLA).
43. https://www.fivetran.com/blog/fivetran-dbt-zendesk — Fivetran's dbt-Zendesk package blog (SLA breach + ticket history).
44. https://fivetran.com/docs/connectors/applications/freshdesk — Fivetran Freshdesk schema.
45. https://fivetran.com/docs/transformations/data-models/jira-data-model/jira-source-model — Fivetran Jira data model.
46. https://knowledge.hubspot.com/integrations/connect-hubspot-and-snowflake-data-sync — HubSpot↔Snowflake native data share (V2_LIVE 15min, V2_DAILY daily).
47. https://atrium.ai/resources/a-complete-guide-to-salesforce-cpq-objects/ — Salesforce CPQ objects guide.
48. https://revsolutions.co/blog/salesforce-revenue-cloud-data-model/ — Salesforce Revenue Cloud data model.
49. https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit — Streamlit in Snowflake docs (INFORMATION_SCHEMA latency note).
50. https://developer.ironcladapp.com/ — Ironclad CLM developer hub.
51. https://workspaceupdates.googleblog.com/2025/05/calendar-interoperability-microsoft-office-365-with-microsoft-graph-api.html — Google↔Microsoft calendar interop GA May 2025.
52. https://learn.microsoft.com/en-us/graph/api/resources/datetimetimezone?view=graph-rest-1.0 — Microsoft Graph dateTimeTimeZone resource.
53. https://help.chilipiper.com/hc/en-us/articles/31428605286931-Meetings-Activity-and-Events-History — Chili Piper meetings activity export.
54. https://docs.snowflake.com/en/sql-reference/functions/system_estimate_search_optimization_costs — Search Optimization cost estimation function.
55. https://documentation.conga.com/clm/latest/api-reference-150503950.html — Conga CLM API reference.
56. https://nces.ed.gov/ccd/aadd.asp — NCES Common Core of Data district address file.
57. https://nces.ed.gov/programs/edge/docs/EDGE_GEOCODE_PUBLIC_FILEDOC.pdf — NCES EDGE geocode file doc (LEAID + SCHNO structure).
58. https://www.cometly.com/post/identity-resolution-marketing — Identity resolution 2026 (85–95% threshold guidance).
59. https://www.customerlabs.com/blog/deterministic-vs-probabilistic-identity-resolution-guide/ — Deterministic vs probabilistic match guide.
60. https://xebia.com/blog/a-practical-guide-to-creating-slowly-changing-dimensions-type-2-in-dbt-part-1/ — SCD2 in dbt practical guide.
61. https://towardsdatascience.com/fuzzywuzzy-basica-and-merging-datasets-on-names-with-different-transcriptions-e2bb6e179fbf/ — FuzzyWuzzy / Levenshtein for name matching.
62. https://docs.getdbt.com/docs/build/about-metricflow — dbt MetricFlow docs.
63. https://www.devoteam.com/expert-view/lookml-vs-dbt-semantic-layer-which-one-is-better/ — LookML vs dbt Semantic Layer.
64. https://cube.dev/ — Cube headless semantic layer (Snowflake 1s P95 claim, OSI 2025).
65. https://trybuildpilot.com/677-evidence-vs-metabase-vs-apache-superset-2026 — Evidence vs Metabase vs Superset 2026.
66. https://flowmetrics.space/2025/08/10/superset-vs-metabase-2025-comparison/ — Superset vs Metabase 2025.
67. https://hex.tech/customers/mercor/ — Hex Mercor customer case study (60+ metrics, hundreds of projects).
68. https://www.tremor.so/ — Tremor (acquired by Vercel; "Tremor Raw" actively developed).
69. https://blog.logrocket.com/build-react-dashboard-tremor/ — Building React dashboards with Tremor.
70. https://www.integrate.io/blog/build-slas-for-real-time-dashboards-with-ai-etl/ — Building SLAs for real-time dashboards.
71. https://tacnode.io/post/data-freshness-vs-latency — Data freshness vs latency distinction.
72. https://www.smashingmagazine.com/2025/09/ux-strategies-real-time-dashboards/ — Smashing Mag UX for real-time dashboards (Live/Stale/Paused pattern).
73. https://docs.elementary-data.com/oss/guides/collect-dbt-source-freshness — Elementary dbt source freshness guide.
74. https://www.elementary-data.com/dbt-tests/freshness-anomalies — Elementary `freshness_anomalies` test.
75. https://docs.getdbt.com/reference/resource-properties/freshness — dbt source `freshness` property.
76. https://www.getdbt.com/blog/data-slas-best-practices — dbt Labs on data SLAs best practices.
77. https://medium.com/snowflake/hightouch-the-reverse-etl-and-data-activation-solution-powered-by-snowflake-71309d65114c — Hightouch reverse-ETL on Snowflake (CircleCI case).
78. https://hightouch.com/solutions/snowflake-cdp — Hightouch as Snowflake CDP (Gartner Leader 2026).
79. https://docs.snowflake.com/en/user-guide/snowpipe-streaming/data-load-snowpipe-streaming-overview — Snowpipe Streaming overview.
80. https://docs.snowflake.com/en/release-notes/2025/other/2025-12-08-snowpipe-simplified-pricing — Snowpipe simplified pricing Dec 2025 (0.0037 credits/GB).
81. https://www.snowflake.com/en/blog/data-vault-row-access-policies-multi-tenancy/ — Snowflake row access policies + multi-tenancy.
82. https://docs.snowflake.com/en/user-guide/security-row-intro — Snowflake row access policy intro.
