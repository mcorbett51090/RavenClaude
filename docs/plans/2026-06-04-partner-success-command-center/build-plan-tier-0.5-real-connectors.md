# Build plan for Codex — Partner Success Command Center, Tier 0.5 (real connectors)

**Audience:** a fresh **Codex (GPT-5.5) session running in GitHub Copilot CLI**, in a Codespace with RavenClaude installed. Codex is the engineer; this file is the engineer's brief. **Self-contained — do not ask Matt to clarify what's already in here.**

**Scope:** Tier 0.5 of [`plan.md`](./plan.md) — stand up the **real Snowflake-backed data layer** that swaps for the synthetic fixture Tier 0 shipped. Snowflake raw + conformed databases; Fivetran-fed Salesforce + Service Cloud + CPQ; Planhat-native Snowflake bidirectional integration; dbt project (sources → staging → intermediate → marts) with MetricFlow semantic layer; `bridge_account_xref` loader with Splink + 7-tier confidence ladder; `export-psm-dashboard.py` that drops a `data.json` in the same shape as Tier 0's fixture. **No rendering changes. No `priority_score` math at the warehouse. No multi-tenant.** Tiers 1–4 ship the rendering; Tier 5 ships multi-tenant.

**Foundation:** [`build-plan-for-codex.md`](./build-plan-for-codex.md) (Tier 0 v3 brief) is your contract. Every artifact this tier produces must validate against the schemas Tier 0 froze (`data.schema.json`, `data.export.schema.json`, `field-classifications.json`). When this brief and Tier 0 disagree — **Tier 0 wins**.

**Settling-step Q1/Q2/Q3 — PRE-ANSWERED (so this brief is fully self-contained):**

| # | Open question (from `plan.md` §Settling steps) | Pre-stocked answer | Rationale |
|---|---|---|---|
| **Q1** | Which support tool does she use? | **Salesforce Service Cloud (`Case` object)** | Smallest blast — rides the existing SFDC Fivetran connector; no new connector contract; in the same MAR pool. |
| **Q2** | Contract system-of-record? | **Salesforce CPQ (`SBQQ__*` namespace)** | Same connector as Q1; `salesforce-cpq-integration.md` covers field mapping. |
| **Q3** | Calendar tool? | **Google Calendar (primary)** | Build against `events.list` + `syncToken` per `calendar-integration-google-outlook.md`. Outlook fallback documented in §3.6 but not implemented in Tier 0.5. |

Codex MUST NOT re-ask Matt about Q1/Q2/Q3 — they are settled. If the wife later contradicts (e.g., she uses Zendesk, not Service Cloud), Tier 0.5 is re-done; that is a Tier 0.5 v2 problem, not a Tier 0.5 v1 problem.

---

## 0. What Tier 0.5 does (and what it does NOT do)

**Tier 0.5 produces:**

1. A Snowflake account with `psm_raw` (per-source landing) + `psm_conformed` (dbt marts) databases.
2. A `WH_PSM_DASHBOARD` XS Standard warehouse (auto-suspend 60s) and three sibling warehouses (`WH_DBT_TRANSFORM`, `WH_INGEST`, `WH_PLANHAT_SYNC`) sized per `snowflake-operational-dashboard-patterns.md`.
3. Fivetran connections for Salesforce (Account/Contact/Opportunity/Contract/Quote/QuoteLineItem + SBQQ__* + Case).
4. Planhat ↔ Snowflake **native bidirectional integration** (BUY — per refreshed `planhat-integration.md`) for Company/EndUser/License + warehouse → Planhat metrics.
5. A Google Calendar BUILD ingest landing raw events to `psm_raw.google_calendar_*`.
6. A dbt project under `plugins/data-platform/dbt/psm_dashboard/` with the three-layer staging/intermediate/marts shape, source freshness declarations, generic + custom tests, and a MetricFlow semantic layer.
7. Dynamic Tables (`TARGET_LAG='15 min'`) on the hot marts that feed every dashboard panel.
8. `bridge_account_xref` populated via a Splink-driven loader implementing the 7-tier confidence ladder (T0 Exact LEAID → T6 Reject) per the SKILL.
9. `export-psm-dashboard.py` — a Python stdlib + `snowflake-connector-python` only script that runs the conformed mart queries, writes a `data.json` that validates against `data.export.schema.json`, and drops in as the synthetic fixture's replacement.
10. Gate 53 wired into `scripts/audit-gates.sh` validating the exported data.json.

**Tier 0.5 does NOT:**

- Render anything. No HTML, no `report.html` edit, no `generate-bi-report.py` extension.
- Compute `priority_score` or `priority_breakdown` in the warehouse. Per Tier 0 `field-classifications.json`, these are `derived_at_render`. The Tier 0.5 export emits `null` for these fields and the renderer fills them.
- Define MetricFlow metrics for `priority_score`. MetricFlow ships measures (raw signals) only.
- Multi-tenant anything. `org_uid` is a constant inside this single-tenant build, populated from `.env`.
- Add a new agent, bump a plugin version, or touch `marketplace.json`.
- Reach beyond the Q1/Q2/Q3 pre-stocked choices.

---

## 1. Pre-flight

| # | Action | Command | Confirm |
|---|---|---|---|
| 1 | Sync main | `git fetch origin main && git checkout origin/main` | tip is latest main |
| 2 | New branch | `git checkout -b feat/psm-dashboard-tier-0.5-real-connectors` | switched |
| 3 | Read this brief end-to-end | (open the file) | every section |
| 4 | Read Tier 0 brief | `cat docs/plans/2026-06-04-partner-success-command-center/build-plan-for-codex.md` | full file |
| 5 | Read the strategic plan | `cat docs/plans/2026-06-04-partner-success-command-center/plan.md` | full file |
| 6 | Read Tier 0's frozen schemas | `cat plugins/edtech-partner-success/bi-report/data.schema.json` then `data.export.schema.json` then `field-classifications.json` | confirm field names + classifications |
| 7 | Read the existing synthetic fixture | `cat plugins/edtech-partner-success/bi-report/data.json \| head -200` | confirm top-level keys + 25 partners + band enum is `"green"/"yellow"/"red"` |

**Read also (priors that constrain design; do NOT re-author):**

- `plugins/data-platform/CLAUDE.md` — house rules 1, 3, 5, 7, 8, 10.
- `plugins/data-platform/knowledge/planhat-integration.md` — Snowflake native BUY verdict (the prior BUILD verdict was reversed 2026-06-04).
- `plugins/data-platform/knowledge/salesforce-cpq-integration.md` — `SBQQ__*` field mapping; `Contract.EndDate` is the renewal anchor.
- `plugins/data-platform/knowledge/clm-integration-ironclad-docusign.md` — read for the cross-vendor `dim_contract` shape (Q2 = CPQ means we don't ship CLM in v1, but the conformed `dim_contract` shape stays vendor-agnostic for forward-compatibility).
- `plugins/data-platform/knowledge/calendar-integration-google-outlook.md` — Google Calendar `events.list` + `syncToken`; Outlook fallback notes.
- `plugins/data-platform/knowledge/snowflake-operational-dashboard-patterns.md` — Dynamic Tables substrate; XS Standard warehouse; clustering keys; result-cache discipline.
- `plugins/data-platform/knowledge/elt-freshness-sla-patterns.md` — three-state Live/Stale/Paused badge; tier-1 SLAs; `mart_connector_health`.
- `plugins/data-platform/knowledge/zendesk-integration.md` — NOT used (Q1 = Service Cloud), but read the SLA-derivation patterns for the parallel `fivetran/dbt_salesforce` Case-handling.
- `plugins/data-platform/skills/cross-system-identity-resolution/SKILL.md` — the 7-tier LEAID ladder; `bridge_account_xref` shape; SCD2 `dim_lea` discipline.

**Verify environment availability (loud-skip if absent, NEVER silent-skip):**

```sh
# Snowflake CLI / SnowSQL: required for Snowflake DDL apply. If absent → loud-skip §3 Snowflake DDL "REQUIRES SNOWSQL".
command -v snowsql || echo "SNOWSQL ABSENT — Snowflake DDL must be applied manually via Snowsight UI; mark §3 step as MANUAL"
# dbt-snowflake adapter: required for dbt parse/build. Install if absent.
python3 -c "import dbt.adapters.snowflake" 2>/dev/null || pip install dbt-snowflake
# Splink: required for the bridge_account_xref loader.
python3 -c "import splink" 2>/dev/null || pip install splink
# snowflake-connector-python: required for export-psm-dashboard.py.
python3 -c "import snowflake.connector" 2>/dev/null || pip install snowflake-connector-python
# jsonschema: required for export schema validation.
python3 -c "import jsonschema" 2>/dev/null || pip install jsonschema
```

These tools are runtime dependencies, NOT new third-party deps in any committed Python script. The committed scripts use **Python stdlib + snowflake-connector-python + jsonschema only** for the export, and **stdlib + splink + snowflake-connector-python** for the bridge loader.

---

## 2. The settling-step answers — encoded

The plan's open questions Q1/Q2/Q3 are answered in §0. They show up as concrete design choices everywhere downstream. The two enduring lessons (per CLAUDE.md):

1. **Q1 = SFDC Service Cloud, NOT a separate support tool.** The dbt sources for support tickets read from the SFDC `case` table — same Fivetran connector. No new vendor contract.
2. **Q2 = SFDC CPQ, NOT Ironclad / DocuSign CLM.** The dbt sources for contracts read from the SFDC `contract` + `SBQQ__*` tables — same Fivetran connector. No CLM BUILD path in v1.
3. **Q3 = Google Calendar, BUILD against Google API.** Service-account OAuth with domain-wide delegation; `events.list` + `syncToken`; lands raw events in `psm_raw.google_calendar_*`. Outlook fallback is documented in §3.6 but NOT IMPLEMENTED in Tier 0.5 v1.

If a step below references "Q1 vendor", read "SFDC Service Cloud". If it references "Q2 vendor", read "SFDC CPQ". If it references "Q3 vendor", read "Google Calendar".

---

## 3. The deliverable — exactly these files

20+ files. Each is `CREATE` unless marked otherwise.

### 3.1 Snowflake DDL

| # | File | Action | Purpose |
|---|---|---|---|
| 1 | `plugins/data-platform/scripts/snowflake-ddl/00-account-objects.sql` | CREATE | `CREATE DATABASE psm_raw; CREATE DATABASE psm_conformed;` + role + warehouse DDL. **Four warehouses: `WH_PSM_DASHBOARD`, `WH_DBT_TRANSFORM`, `WH_INGEST`, `WH_PLANHAT_SYNC`** — all `WAREHOUSE_SIZE='XSMALL'`, `WAREHOUSE_TYPE='STANDARD'`, `AUTO_SUSPEND=60`, `AUTO_RESUME=TRUE`, `INITIALLY_SUSPENDED=TRUE`. |
| 2 | `plugins/data-platform/scripts/snowflake-ddl/01-raw-schemas.sql` | CREATE | `CREATE SCHEMA psm_raw.salesforce; CREATE SCHEMA psm_raw.planhat; CREATE SCHEMA psm_raw.google_calendar;` |
| 3 | `plugins/data-platform/scripts/snowflake-ddl/02-conformed-schemas.sql` | CREATE | `CREATE SCHEMA psm_conformed.staging; CREATE SCHEMA psm_conformed.intermediate; CREATE SCHEMA psm_conformed.marts; CREATE SCHEMA psm_conformed.semantic;` |
| 4 | `plugins/data-platform/scripts/snowflake-ddl/03-grants.sql` | CREATE | Grants per role: `ROLE_FIVETRAN`, `ROLE_PLANHAT_SVC`, `ROLE_DBT_BUILD`, `ROLE_DBT_QUERY`, `ROLE_DASHBOARD_RO`. Service-user posture per `planhat-integration.md` § "Configuration steps (warehouse side)". |
| 5 | `plugins/data-platform/scripts/snowflake-ddl/04-clustering-keys.sql` | CREATE | Cluster `fct_partner_health(account_uid, snapshot_date::date)`, `fct_calendar_event(account_uid, start_utc::date)`, `fct_support_ticket(account_uid, opened_at::date)`. Per `snowflake-operational-dashboard-patterns.md` § "Clustering keys — the partner-keyed access pattern". |

### 3.2 dbt project

| # | File | Action | Purpose |
|---|---|---|---|
| 6 | `plugins/data-platform/dbt/psm_dashboard/dbt_project.yml` | CREATE | dbt project name, version, model paths, target schema. |
| 7 | `plugins/data-platform/dbt/psm_dashboard/profiles.yml.example` | CREATE | Snowflake profile template (use env vars: `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PRIVATE_KEY_PATH`, etc.). Key-pair auth ONLY — no password. |
| 8 | `plugins/data-platform/dbt/psm_dashboard/models/sources/_sources.yml` | CREATE | Sources for `salesforce`, `planhat`, `google_calendar`. Per-table freshness declarations (T1 = 1h warn / 2h err; T2 = 4h / 12h; T3 = 24h / 48h). |
| 9 | `plugins/data-platform/dbt/psm_dashboard/models/staging/stg_salesforce__account.sql` | CREATE | Typed staging; `WHERE _fivetran_deleted = FALSE`; surface `Id AS sfdc_account_id`. |
| 10 | `plugins/data-platform/dbt/psm_dashboard/models/staging/stg_salesforce__contact.sql` | CREATE | Typed staging; surface role mapping (champion/exec_sponsor heuristics from a custom `Role__c` field). |
| 11 | `plugins/data-platform/dbt/psm_dashboard/models/staging/stg_salesforce__opportunity.sql` | CREATE | Typed staging; for renewal-opp signal. |
| 12 | `plugins/data-platform/dbt/psm_dashboard/models/staging/stg_salesforce__contract.sql` | CREATE | Typed staging; derives `notice_window_opens_at = EndDate - TerminationNoticeDays` per `salesforce-cpq-integration.md`. **`Contract.EndDate` is the renewal anchor, NOT `Contract.RenewalDate`.** |
| 13 | `plugins/data-platform/dbt/psm_dashboard/models/staging/stg_salesforce__quote.sql` + `_quote_line.sql` + `_sbqq_subscription.sql` | CREATE (3 files) | Typed staging from `SBQQ__*` namespace. Explicit field allow-list per CPQ guidance (NOT `SELECT *`). |
| 14 | `plugins/data-platform/dbt/psm_dashboard/models/staging/stg_salesforce__case.sql` | CREATE | Typed staging from `Case`. Derives `age_days = DATEDIFF('day', CreatedDate, COALESCE(ClosedDate, CURRENT_TIMESTAMP()))`. `is_escalation = (Priority = 'High' OR Type = 'Escalation' OR Status = 'Escalated')`. |
| 15 | `plugins/data-platform/dbt/psm_dashboard/models/staging/stg_planhat__company.sql` + `__enduser.sql` + `__health_score.sql` + `__nps.sql` + `__metric.sql` | CREATE (5 files) | Typed staging; `sourceId` surfaced as `sfdc_account_id` (the SFDC bridge anchor per `planhat-integration.md`); `externalId` surfaced as `partner_key_candidate`. NPS verbatim **masked** (PII). |
| 16 | `plugins/data-platform/dbt/psm_dashboard/models/staging/stg_google_calendar__event.sql` | CREATE | Typed staging; UTC start/end via `singleEvents=true` expansion; identity bridge via attendee email → `bridge_account_xref`. |
| 17 | `plugins/data-platform/dbt/psm_dashboard/snapshots/snap_contract.sql` | CREATE | SCD2 snapshot on `Contract.LastModifiedDate` for amendment-chain modeling. Strategy `timestamp`, `invalidate_hard_deletes=True`. Per `salesforce-cpq-integration.md`. |
| 18 | `plugins/data-platform/dbt/psm_dashboard/models/intermediate/int_partner_signals.sql` | CREATE | Per-partner intermediate combining `stg_salesforce__account` + Planhat health + ticket counts. Outputs the raw signals (not the score). |
| 19 | `plugins/data-platform/dbt/psm_dashboard/models/intermediate/int_contract_amendment_chain.sql` | CREATE | Walks `SBQQ__AmendedContract__c` linked list to reconstruct current-vs-original contract per partner. |
| 20 | `plugins/data-platform/dbt/psm_dashboard/models/marts/dim_partner.sql` | CREATE | Vendor-agnostic partner dimension. Joined via `bridge_account_xref`. Materialized as **Dynamic Table** `target_lag='15 min'`, `snowflake_warehouse='WH_DBT_TRANSFORM'`. |
| 21 | `plugins/data-platform/dbt/psm_dashboard/models/marts/dim_contract.sql` | CREATE | Vendor-agnostic contract dim from `snap_contract`. Schema mirrors `clm-integration-ironclad-docusign.md` § "Cross-vendor `dim_contract` normalization" for forward-compatibility (even though Tier 0.5 v1 is CPQ-only). |
| 22 | `plugins/data-platform/dbt/psm_dashboard/models/marts/fct_partner_health.sql` | CREATE | Per-partner per-day health snapshot. Health components: `adoption`, `touchpoint`, `outcome`, `sentiment`, `champion`, `usage`. Dynamic Table `target_lag='15 min'`. **Does NOT compute `priority_score` — that's `derived_at_render`.** |
| 23 | `plugins/data-platform/dbt/psm_dashboard/models/marts/fct_support_ticket.sql` | CREATE | Per-ticket fact from `stg_salesforce__case`. Vendor-agnostic shape (cross-source ready). |
| 24 | `plugins/data-platform/dbt/psm_dashboard/models/marts/fct_calendar_event.sql` | CREATE | Per-event fact from `stg_google_calendar__event`. UTC storage + IANA timezone on `dim_partner`. |
| 25 | `plugins/data-platform/dbt/psm_dashboard/models/marts/fct_renewal_pipeline.sql` | CREATE | Per-contract `notice_window_opens_at`-based renewal-pipeline fact. The dashboard's 180/120/90/60/30-day buckets render from this. |
| 26 | `plugins/data-platform/dbt/psm_dashboard/models/marts/mart_connector_health.sql` | CREATE | The three-state badge table per `elt-freshness-sla-patterns.md` § "Connector health table". One row per source: `salesforce | planhat | google_calendar`. |
| 27 | `plugins/data-platform/dbt/psm_dashboard/models/marts/_marts.yml` | CREATE | Generic + custom dbt tests per mart. `not_null` + `unique` on every uid column; cross-source reconciliation tests; `accepted_values` on every enum. |
| 28 | `plugins/data-platform/dbt/psm_dashboard/models/semantic/psm_semantic.yml` | CREATE | MetricFlow semantic-layer config. **Measures only — NO `priority_score`.** Measures: `health_score`, `sentiment_score`, `engagement_score`, `open_escalations`, `open_tickets`, `arr`, `days_since_touchpoint`. Entities: `partner`, `contract`. **`priority_score` is `derived_at_render` per Tier 0's `field-classifications.json` — it does NOT belong in MetricFlow.** |
| 29 | `plugins/data-platform/dbt/psm_dashboard/seeds/seed_nces_districts.csv` | CREATE | Top-2000 US public school districts subset from the NCES CCD flat file. Used by `dim_lea` for LEAID matching. (A pruned subset, not the full file — full ingest is a Tier 0.5 v2 concern.) |
| 30 | `plugins/data-platform/dbt/psm_dashboard/seeds/_seeds.yml` | CREATE | Seed config + tests. |

### 3.3 Identity loader

| # | File | Action | Purpose |
|---|---|---|---|
| 31 | `plugins/data-platform/scripts/load-bridge-account-xref.py` | CREATE | Splink-driven loader implementing the 7-tier ladder. Stdlib + `splink` + `snowflake-connector-python` only. Walks T0 (LEAID exact) → T1 (compound deterministic) → T2 (fuzzy ≥0.92) → T3 (probabilistic) → T4 (Planhat `sourceId == sfdc_account_id`) → T5 (email-domain) → T6 (reject). Writes to `psm_conformed.marts.bridge_account_xref`. |
| 32 | `plugins/data-platform/dbt/psm_dashboard/models/marts/bridge_account_xref.sql` | CREATE | dbt-managed view over the table the loader writes. Carries `match_method` + `confidence` + `manual_override_reason` + `overridden_by` + `last_verified_at`. |
| 33 | `plugins/data-platform/dbt/psm_dashboard/models/marts/dim_lea.sql` | CREATE | SCD2 dimension over `seed_nces_districts`. `effective_from`/`effective_to`/`is_current` discipline per the SKILL. |
| 34 | `plugins/data-platform/dbt/psm_dashboard/models/marts/dim_partner_lea_link.sql` | CREATE | Many-to-many SCD2 between `partner_key` and `leaid`. Survives district consolidation. |

### 3.4 Export + gate + config

| # | File | Action | Purpose |
|---|---|---|---|
| 35 | `plugins/data-platform/scripts/export-psm-dashboard.py` | CREATE | The drop-in replacement for the synthetic fixture. **Python stdlib + `snowflake-connector-python` only — no other third-party deps.** Reads from `psm_conformed.marts.*`, writes a `data.json` validating against `data.export.schema.json`. Idempotent. Single-command. CLI: `--out <path>`, `--as-of <ISO date>`, `--org-uid <UUIDv4>`, `--validate` (runs jsonschema). |
| 36 | `plugins/data-platform/scripts/export-psm-dashboard.test.py` | CREATE | Stdlib unittest. Mocks the snowflake connector; asserts the export shape matches `data.export.schema.json`; asserts `partners[].priority_score` and `priority_breakdown` are `null` in the export (proves `derived_at_render` discipline). |
| 37 | `plugins/data-platform/.env.example` | CREATE | Documents required env vars: `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PRIVATE_KEY_PATH`, `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_DATABASE`, `SNOWFLAKE_SCHEMA`, `SNOWFLAKE_ROLE`, `PSM_ORG_UID`, `PSM_AS_OF` (optional, defaults to `CURRENT_DATE`). |
| 38 | `.gitignore` | EDIT (append) | Add `plugins/data-platform/.env`, `plugins/data-platform/dbt/psm_dashboard/profiles.yml`, `plugins/data-platform/dbt/psm_dashboard/target/`, `plugins/data-platform/dbt/psm_dashboard/dbt_packages/`, `plugins/data-platform/dbt/psm_dashboard/logs/`. |
| 39 | `.repo-layout.json` | EDIT | Add globs: `plugins/*/dbt/**`, `plugins/*/scripts/snowflake-ddl/**`. (`plugins/*/scripts/**` is already covered for the loader + export.) |
| 40 | `scripts/audit-gates.sh` | EDIT (append) | Wire Gate 53 — `must_pass` on `export-psm-dashboard.py --validate`; `must_fail` on a known-bad mart fixture (synthetic-bridge file with an orphan `account_uid`). |
| 41 | `plugins/data-platform/dbt/psm_dashboard/README.md` | CREATE | One-pager: how to run `dbt deps`, `dbt seed`, `dbt run`, `dbt test`, then the export. Onboarding-friendly. |

### 3.5 Gap knowledge files (NONE)

**Q1/Q2 ride the existing SFDC connector (no new vendor knowledge file).** Q3 (Google Calendar) is covered by the existing `calendar-integration-google-outlook.md`. The original plan flagged three gap-files; **none are needed in Tier 0.5 v1** because the pre-stocked answers all land on existing-knowledge paths.

**Nothing else.** No new agent. No new skill. No plugin version bump. No `marketplace.json` change. No `report.html` edit.

### 3.6 Documented-but-not-implemented (forward-references)

- **Outlook (Microsoft Graph) calendar fallback** — if the wife later confirms Outlook, v2 swaps `stg_google_calendar__event.sql` for `stg_microsoft__calendar_view.sql` per the existing knowledge file.
- **Ironclad / DocuSign CLM** — `dim_contract.sql` is vendor-agnostic per `clm-integration-ironclad-docusign.md` so a future CLM swap is additive.
- **Zendesk fallback** — `fct_support_ticket.sql` is vendor-agnostic so swapping `stg_salesforce__case.sql` for `stg_zendesk__ticket.sql` is additive.
- **Multi-PSM row-access policies** — documented in `snowflake-operational-dashboard-patterns.md`. **Single-tenant in v1; no RLS.**

---

## 4. Step-by-step build order

### Step 1 — Snowflake DDL (the foundation)

Apply `00-account-objects.sql` → `01-raw-schemas.sql` → `02-conformed-schemas.sql` → `03-grants.sql` → `04-clustering-keys.sql` in order.

**Concrete acceptance:**
- `SHOW DATABASES LIKE 'PSM_%'` returns `PSM_RAW` and `PSM_CONFORMED`.
- `SHOW WAREHOUSES LIKE 'WH_%'` returns the four warehouses, each `XSMALL`, `AUTO_SUSPEND=60`.
- `SHOW ROLES LIKE 'ROLE_%'` returns the five roles.
- `SHOW SCHEMAS IN DATABASE PSM_RAW` returns `salesforce`, `planhat`, `google_calendar`.
- `SHOW SCHEMAS IN DATABASE PSM_CONFORMED` returns `staging`, `intermediate`, `marts`, `semantic`.

**MUST NOT counterpart:**
- Do NOT use `WAREHOUSE_TYPE='SNOWPARK-OPTIMIZED'` — the cost shape doesn't fit a dashboard read pattern.
- Do NOT skip `AUTO_SUSPEND=60` — a left-running XS warehouse wastes ~$2/day per warehouse idle.
- Do NOT grant `ACCOUNTADMIN` or `SYSADMIN` to `ROLE_PLANHAT_SVC` or `ROLE_FIVETRAN` — minimum-necessary only.

### Step 2 — Fivetran Salesforce connector

Configure Fivetran connection to Snowflake destination `PSM_RAW.SALESFORCE`. Connector config:

- Connector: Salesforce.
- Tables (explicit allow-list, NOT auto-select): `account`, `contact`, `opportunity`, `contract`, `quote`, `quoteLineItem`, `case`, `sbqq__quote__c`, `sbqq__quoteline__c`, `sbqq__subscription__c`, `sbqq__contractedprice__c`.
- Field selection per `salesforce-cpq-integration.md` § "Field-set management" — explicit per-field allow-list scoped to the `dim_partner` / `dim_contract` / `fct_support_ticket` source fields.
- Sync cadence: 6h (per `connector-patterns.md` §1.3 — adequate for a "last-night-fresh" dashboard).

**Concrete acceptance:**
- Fivetran UI shows connection green; first sync completes; `SELECT COUNT(*) FROM psm_raw.salesforce.account` > 0.
- `_fivetran_synced` column present on every table.
- `SBQQ__SubscriptionTerm__c` and `SBQQ__AmountRolledUp__c` present in `psm_raw.salesforce.contract` (proves CPQ field allow-list ran).
- `Case` table populated (proves Q1 = Service Cloud is wired).

**MUST NOT counterpart:**
- Do NOT enable `SELECT *` on `sbqq__*` objects — 10MB payload risk per `salesforce-cpq-integration.md`.
- Do NOT skip `_fivetran_deleted = FALSE` filter in any staging model.
- Do NOT use `Contract.RenewalDate` as the renewal anchor — it's the auto-renewal target (often null).

### Step 3 — Planhat ↔ Snowflake native bidirectional integration

Per `planhat-integration.md` § "Configuration steps (warehouse side)":

1. Create the dedicated Snowflake user `USR_PLANHAT_SVC` of type `SERVICE` (NOT `PERSON`).
2. Generate RSA keypair; set the public key on the user via `ALTER USER USR_PLANHAT_SVC SET RSA_PUBLIC_KEY = '...'`; store the private key in Planhat's integration UI.
3. Grant per Step 1's `03-grants.sql`: `USAGE` on `WH_PLANHAT_SYNC` + `PSM_RAW` + `PSM_RAW.PLANHAT`; `SELECT` on outbound tables; `INSERT/UPDATE/DELETE` on inbound tables.
4. In Planhat's UI, configure per-model direction:
   - `Company` → `Receive from Provider` (Planhat is the source of truth for the CS dim).
   - `End User` → `Receive from Provider`.
   - `License` → `Receive from Provider`.
   - `Metrics` (warehouse-owned product usage) → `Send to Provider` (warehouse → Planhat; 5–24h cadence).
5. Set `externalId` convention: `externalId = sfdc_account_id` (the warehouse identity hook) and `sourceId = sfdc_account_id` (the SFDC bridge — per `planhat-integration.md` § "Keyable hierarchy — externalId / sourceId / _id").

**Concrete acceptance:**
- Planhat UI shows connection status `Connected`, last sync within 1h.
- `SELECT COUNT(*) FROM psm_raw.planhat.company` > 0.
- `SELECT externalId FROM psm_raw.planhat.company LIMIT 1` returns an SFDC-shaped 18-char ID.
- Snowflake `LOGIN_HISTORY` shows `USR_PLANHAT_SVC` authenticating successfully via key-pair (NOT password).

**MUST NOT counterpart:**
- Do NOT use OAuth + password "person" user — Snowflake MFA breaks it; key-pair on a SERVICE user is the only supported path.
- Do NOT invert `sourceId` and `externalId` — that silently breaks Planhat ↔ SFDC sync.
- Do NOT set Metrics direction to `Both` — warehouse owns the metric; Planhat receives only.
- Do NOT skip the 90-day key-pair rotation calendar reminder (per `planhat-integration.md` § "Auth rotation").

### Step 4 — Google Calendar ingest

Per `calendar-integration-google-outlook.md` § "Google Calendar API":

1. Create a Google Cloud service account; enable Calendar API.
2. Workspace admin grants domain-wide delegation; scopes: `calendar.events.readonly` + `calendar.readonly`. NOT write scope (read-only first, per § "Read-only-first then write-back discipline").
3. Build `plugins/data-platform/scripts/ingest-google-calendar.py` — service-account JWT auth; `events.list` with `syncToken` (steady-state) or `timeMin` (backfill); `singleEvents=true`; pagination via `nextPageToken`; idempotent MERGE on `event.id` into `psm_raw.google_calendar.events`.
4. Schedule via cron (`@hourly`) or Snowflake task — pick whichever the engagement is already using.

**Concrete acceptance:**
- First run with `--mode=backfill --since=2026-01-01` populates `psm_raw.google_calendar.events` with `event_id`, `i_cal_uid`, `summary`, `start_utc`, `end_utc`, `attendees_json`, `organizer_email`, `status`.
- Subsequent runs with `--mode=incremental` use `syncToken`; on 410 GONE, restart with `timeMin = last_loaded_at - 7d`.
- `SELECT COUNT(DISTINCT event_id) FROM psm_raw.google_calendar.events` matches Google's UI count within ±0.5%.

**MUST NOT counterpart:**
- Do NOT grant Mail or Drive scopes on the same service account (scope creep — per § "Common gotchas" #5).
- Do NOT skip `singleEvents=true` — mixed mode produces double-counts.
- Do NOT store local time without timezone — UTC + IANA only.
- Do NOT ship write-back in v1 (read-only first; write-back is Tier 0.5 v2 at earliest).
- Do NOT skip the 60s `pageToken` discipline — partial pages without idempotency keys produce duplicate rows.

### Step 5 — dbt project skeleton

Scaffold `plugins/data-platform/dbt/psm_dashboard/` per `dbt-project-scaffolding/SKILL.md`. Run:

```sh
cd plugins/data-platform/dbt/psm_dashboard
dbt deps                                                      # install dbt_utils + fivetran/dbt_salesforce + dbt_expectations
dbt parse --target=dev                                        # parse only — catches YAML errors
```

**Concrete acceptance:**
- `dbt parse` exits 0.
- `dbt list --resource-type source` shows `salesforce.*`, `planhat.*`, `google_calendar.*`.
- `dbt list --resource-type model` shows the staging + intermediate + marts hierarchy.

**MUST NOT counterpart:**
- Do NOT use the default `dev` schema name `dbt_<user>` — set explicit `staging` / `intermediate` / `marts` schemas via `+schema:` config.
- Do NOT skip `dbt deps` — `fivetran/dbt_salesforce` package is non-negotiable for the Case ticket-aging math.

### Step 6 — Staging models (typed, sourced, tested)

Build the 13 staging models (§3.2 #9–#16) following the per-vendor knowledge files. Every model:

- Selects from `source('<vendor>', '<table>')` — not raw refs.
- Filters `_fivetran_deleted = FALSE` (Fivetran convention) or vendor-specific delete column (Planhat per `planhat-integration.md` § "Deletion handling").
- Renames vendor-native columns to vendor-agnostic names (`Id` → `<entity>_id`).
- Applies PII masking on NPS verbatim, email, calendar event titles/descriptions.
- Has at least `not_null` + `unique` test on the surrogate key.

**Concrete acceptance:**
- `dbt run --select staging` exits 0.
- `dbt test --select staging` exits 0 (all generic tests pass).
- `dbt source freshness` warns/errors per the declared thresholds; passes for fresh data.

**MUST NOT counterpart:**
- Do NOT use `SELECT *` on any source — explicit column allow-list (per `salesforce-cpq-integration.md` discipline).
- Do NOT skip the `_fivetran_deleted` filter — ghost rows in marts is the failure mode.
- Do NOT expose NPS verbatim or Calendar event title/description to non-privileged roles.
- Do NOT use string-equality on `Account.AccountType__c` or any custom field without confirming the org's enum (always-present source-spec gotcha).

### Step 7 — Identity loader + `bridge_account_xref`

Build `plugins/data-platform/scripts/load-bridge-account-xref.py`. The script implements the 7-tier ladder from the SKILL:

| Tier | Logic | `match_method` | `confidence` | Auto-resolve? |
|---|---|---|---|---|
| **T0** | SFDC `Account.NCES_LEAID__c` populated AND matches `dim_lea.leaid` | `leaid_exact` | 1.00 | Yes |
| **T1** | `(state_fips, normalize_district_name(name), city)` exact match | `leaid_compound` | 0.95 | Yes (with audit) |
| **T2** | Jaro-Winkler on normalized name within state ≥ 0.92 (via Splink) | `leaid_fuzzy_high` | 0.85–0.95 | Yes (review at first sync) |
| **T3** | Splink probabilistic multi-signal (name + city + zip + enrollment) ≥ 0.70 | `leaid_probabilistic` | 0.70–0.85 | **NO — stewardship** |
| **T4** | Planhat `Company.sourceId == sfdc_account_id` | `external_id` | 1.00 | Yes |
| **T5** | Email-domain match (excluding generic domains) | `email_domain` | 0.75 | Yes (with audit) |
| **T6** | Below threshold | `unresolved` | 0.00 | NO — reject |

Splink is used for T2 + T3 (the fuzzy + probabilistic tiers). T0/T1/T4/T5 are deterministic SQL. The loader writes to `psm_conformed.marts.bridge_account_xref` per the SKILL's DDL.

**Census Same-Name guard (per the SKILL § "Why tighter than consumer identity"):** the script maintains a list of district names that occur ≥ 2 times across distinct LEAIDs in the NCES seed. For any T2 match where the normalized name matches a same-name district, automatically downgrade to T3 (stewardship review) regardless of similarity score.

**Concrete acceptance:**
- `python3 plugins/data-platform/scripts/load-bridge-account-xref.py --dry-run` prints per-tier counts.
- `python3 ... --apply` writes to `bridge_account_xref`.
- `SELECT match_method, COUNT(*) FROM psm_conformed.marts.bridge_account_xref GROUP BY 1` shows non-zero T0 and T4 counts (deterministic anchors fired).
- Any T3 row has `account_key IS NULL` until stewardship-approved (per the SKILL's Step 5).
- A same-name district pair (e.g., two "Lincoln Public Schools" in different states) lands at T3, not T2.

**MUST NOT counterpart:**
- Do NOT write `JOIN ON LOWER(TRIM(company_name)) = LOWER(TRIM(account_name))` anywhere — that bypasses the bridge.
- Do NOT auto-publish a T3 match without `reviewed_by IS NOT NULL`.
- Do NOT skip the Census same-name guard — false-positive cost is high in a small entity universe (~13.5k districts).
- Do NOT drop unresolved records — null FK, retain, alert.
- Do NOT embed LEAID directly in fact tables — use `partner_key` + `dim_partner_lea_link`.

### Step 8 — Intermediate models

Build `int_partner_signals.sql` and `int_contract_amendment_chain.sql`. The first joins partner-level signals across sources; the second walks the `SBQQ__AmendedContract__c` linked list.

**Concrete acceptance:**
- `dbt run --select intermediate` exits 0.
- `int_partner_signals` row count equals `dim_partner` row count (1:1 per partner).
- `int_contract_amendment_chain` correctly identifies amendment chains in the SFDC sandbox.

**MUST NOT counterpart:**
- Do NOT compute `priority_score` or `priority_breakdown` here (or anywhere in dbt).
- Do NOT use a HAVING clause to silently drop unresolved partners — they show up in the final marts with explicit-null markers.

### Step 9 — Marts: dimensions

Build `dim_partner.sql`, `dim_contract.sql`, `dim_lea.sql`, `dim_partner_lea_link.sql`, `bridge_account_xref.sql`. Materialize `dim_partner` and `dim_contract` as **Dynamic Tables** with `target_lag='15 min'`, `snowflake_warehouse='WH_DBT_TRANSFORM'`.

**Concrete acceptance:**
- `dbt run --select marts.dim_*` exits 0.
- `SHOW DYNAMIC TABLES IN SCHEMA psm_conformed.marts` shows `dim_partner` and `dim_contract` with `target_lag='15 minutes'`.
- `dim_partner.account_uid` is strict UUIDv4 (regex check in a custom dbt test).

**MUST NOT counterpart:**
- Do NOT use `target_lag='1 minute'` — 15 min is the cost/freshness sweet spot per `snowflake-operational-dashboard-patterns.md` § "TL;DR".
- Do NOT use `materialized='materialized_view'` for cross-source joins — falls behind Dynamic Tables on multi-source.
- Do NOT skip `org_uid` on every entity (it's `production_required` per Tier 0).

### Step 10 — Marts: facts

Build `fct_partner_health.sql`, `fct_support_ticket.sql`, `fct_calendar_event.sql`, `fct_renewal_pipeline.sql`. All Dynamic Tables `target_lag='15 min'`.

**Concrete acceptance:**
- `dbt run --select marts.fct_*` exits 0.
- `fct_partner_health` rows per `(account_uid, snapshot_date)` are unique.
- `fct_calendar_event.start_utc < fct_calendar_event.end_utc` for every row (dbt assertion test).
- `fct_renewal_pipeline.notice_window_opens_at == DATEADD('day', -COALESCE(notice_period_days, 90), contract_end_date)` (the CPQ-derived field).

**MUST NOT counterpart:**
- Do NOT store local time on calendar events — UTC + IANA timezone on `dim_partner`.
- Do NOT compute `priority_score` — Tier 0's `field-classifications.json` says `derived_at_render`.
- Do NOT skip `account_uid` as the cluster-key leading column.

### Step 11 — Marts: `mart_connector_health`

Build `mart_connector_health.sql` per `elt-freshness-sla-patterns.md` § "Connector health table". One row per source. Drives the dashboard's Live/Stale/Paused badge.

**Concrete acceptance:**
- `SELECT * FROM mart_connector_health` returns one row per `salesforce | planhat | google_calendar`.
- Each row carries `last_sync_at`, `last_success_at`, `last_error_at`, `consecutive_errors`, `sla_freshness_target_minutes`, `current_tier`, `status`.
- A simulated connector error (manually flip `last_error_at`) causes `status` to flip to `degraded`.

**MUST NOT counterpart:**
- Do NOT use `ACCOUNT_USAGE` for the freshness query (90 min stale per `snowflake-operational-dashboard-patterns.md` § "Common gotchas").
- Do NOT skip per-source rows — global-only badge breaks per-panel granularity.

### Step 12 — MetricFlow semantic layer

Build `models/semantic/psm_semantic.yml` per `dbt-project-scaffolding/SKILL.md`. Measures:

```yaml
semantic_models:
  - name: partner_signals
    model: ref('fct_partner_health')
    entities:
      - name: partner
        type: primary
        expr: account_uid
    measures:
      - name: health_score
        agg: average
        expr: health_score
      - name: sentiment_score
        agg: average
        expr: sentiment_score
      - name: engagement_score
        agg: average
        expr: engagement_score
      - name: open_escalations
        agg: sum
        expr: open_escalations
      - name: open_tickets
        agg: sum
        expr: open_tickets
      - name: arr
        agg: sum
        expr: arr
      - name: days_since_touchpoint
        agg: average
        expr: days_since_touchpoint
    dimensions:
      - name: snapshot_date
        type: time
        type_params: {time_granularity: day}
      - name: lifecycle_phase
        type: categorical
      - name: lifecycle_substage
        type: categorical
      - name: segment
        type: categorical
      - name: state
        type: categorical
```

**Concrete acceptance:**
- `dbt parse` exits 0 (parses the semantic models).
- `mf list metrics` (MetricFlow CLI) lists the seven measures.
- `mf query --metrics health_score --group-by partner__account_uid` returns row-per-partner with averaged health.

**MUST NOT counterpart:**
- Do NOT define a `priority_score` measure here. Per Tier 0's `field-classifications.json` it's `derived_at_render` — the renderer computes it from raw signals.
- Do NOT skip `entities:` declaration — joins fail without them.
- Do NOT define metrics with arithmetic — measures only at this layer.

### Step 13 — `export-psm-dashboard.py`

Build `plugins/data-platform/scripts/export-psm-dashboard.py`. Stdlib + `snowflake-connector-python` + `jsonschema` only.

**CLI:** `python3 export-psm-dashboard.py --out <path> --as-of <ISO date> --org-uid <UUIDv4> [--validate]`

**Contract:**
- Reads from `psm_conformed.marts.*`. Writes JSON validating against `data.export.schema.json`.
- Drops in as byte-shape replacement for the synthetic fixture.
- Emits `null` for `partners[].priority_score` and `priority_breakdown` (`derived_at_render`).
- Emits `null` for `partners[].engagement_score` (`synthetic_only`).
- Per Tier 0's `--export-mode`, skips: `synthetic_only`, `derived_at_render`, the `Demo:` prefix, the `synthetic-` ID prefix (real names + real IDs land here).
- Idempotent: same warehouse state + same `--as-of` ⇒ byte-identical output.

**Determinism:** all queries `ORDER BY` uid; `json.dumps(..., indent=2, sort_keys=False, ensure_ascii=False)`; floats rounded at construction; dates as `YYYY-MM-DD` strings.

**Connector-failure handling:** if a source is `failed` in `mart_connector_health`, that block is emitted **empty with `last_succeeded_at`** (NOT a crash) — the renderer's three-state badge renders Paused.

**Output blocks:** top-level metadata (`schema_version=1`, `org_uid`, `as_of`, `report{}`), then `partners[]`, `contacts[]`, `timeline_events[]` (UNION across sources), `usage_daily[]`, `usage_daily_school[]`, `success_plans[]` (Planhat), `contracts[]` (current + history), `tickets[]` (Case-backed), `calendar_events[]`, `bridge_account_xref[]`, `priority_weights{}` (copy verbatim from Tier 0 fixture — the wife tunes these). Validate if `--validate`. Write atomically (temp file + rename — never partial-write).

**Concrete acceptance:**
- `python3 export-psm-dashboard.py --out /tmp/data.json --validate` exits 0.
- `python3 -m jsonschema -i /tmp/data.json plugins/edtech-partner-success/bi-report/data.export.schema.json` exits 0.
- The file drops into `plugins/edtech-partner-success/bi-report/data.json` and `python3 -m jsonschema -i plugins/edtech-partner-success/bi-report/data.json plugins/edtech-partner-success/bi-report/data.export.schema.json` exits 0.
- For every partner, `priority_score` is `null` and `priority_breakdown` is `null` in the export (renderer fills them).
- Run-time budget: full export under 5 min on the production-shaped warehouse (Tier 0.5 budget per `plan.md` Acceptance: "Run-time budget: full ELT + export under 15 min").

**MUST NOT counterpart:**
- Do NOT introduce a third-party Python dep beyond `snowflake-connector-python` and `jsonschema`.
- Do NOT use `password` auth — key-pair only.
- Do NOT compute `priority_score` here — that's the renderer's job.
- Do NOT crash if one source is `failed` — emit empty block with `last_succeeded_at`.
- Do NOT print row contents to stderr/stdout on PII fields.
- Do NOT skip atomic write — partial-write corrupts the fixture.

### Step 14 — Gate 53 in `audit-gates.sh`

Append to `scripts/audit-gates.sh`:

```bash
echo "── Gate 53: PSM dashboard real-connector export ──────────────────────"

# must-pass: export validates against export schema
rc=0
python3 plugins/data-platform/scripts/export-psm-dashboard.py \
    --out "$TMP/data-real.json" \
    --as-of 2026-06-04 \
    --org-uid 11111111-2222-4333-8444-555555555555 \
    --validate >/dev/null 2>&1 || rc=$?
gate "psm-real-export-validates" must_pass "$rc"

# must-fail: a fixture with an orphan account_uid in contacts[] fails the
# orphan-refs check (re-uses Tier 0's check #2).
DI_BAD="$TMP/data-real-orphan.json"
python3 - <<'PY' > "$DI_BAD"
import json
d = json.load(open("$TMP/data-real.json"))
c = dict(d["contacts"][0])
c["contact_uid"] = "22222222-3333-4444-8555-666666666666"  # valid UUIDv4
c["account_uid"] = "deadbeef-cafe-4dad-8bad-baadc0debaad"  # orphan UUIDv4
d["contacts"].append(c)
print(json.dumps(d, indent=2))
PY
rc=0
python3 scripts/check-psm-data-integrity.py --data "$DI_BAD" --export-mode >/dev/null 2>&1 || rc=$?
gate "psm-real-export-orphan-detected" must_fail "$rc"
```

(`--export-mode` is the Tier 0 integrity script's flag that skips synthetic-only checks like the `Demo:` prefix and the `synthetic-` ID prefix.)

**Concrete acceptance:**
- `bash scripts/audit-gates.sh` exits 0 with Gate 53 passing both must-pass and must-fail.
- Gate 53 fails LOUDLY if Snowflake credentials are absent (loud-skip with `THIS IS NOT A PASS`, exit code 2, NOT 0).

**MUST NOT counterpart:**
- Do NOT silent-skip Gate 53 on missing credentials.
- Do NOT use Tier 0's must-fail orphan UUID — pick a different UUIDv4 to avoid collision audit theater.

### Step 15 — Layout + gitignore + README + .env.example

Edit `.repo-layout.json` to add `plugins/*/dbt/**` and `plugins/*/scripts/snowflake-ddl/**`. Edit `.gitignore` to add the dbt artifacts + `.env`. Create `plugins/data-platform/dbt/psm_dashboard/README.md` and `plugins/data-platform/.env.example`.

**Concrete acceptance:**
- Layout-snippet check (§5 #10) shows "Layout OK".
- `.env` is gitignored: `git check-ignore plugins/data-platform/.env` returns success.
- `dbt/psm_dashboard/target/` is gitignored.

**MUST NOT counterpart:**
- Do NOT commit `.env` (real secrets).
- Do NOT commit `profiles.yml` (Snowflake creds); only `profiles.yml.example` is committed.
- Do NOT commit `target/` or `dbt_packages/` (dbt artifacts).

---

## 5. Verification

| # | Command | Expected |
|---|---|---|
| 1 | `npx prettier --write . && npx prettier --check .` | exit 0 |
| 2 | `python3 -m json.tool` on each new JSON file | exit 0 |
| 3 | `cd plugins/data-platform/dbt/psm_dashboard && dbt deps && dbt parse` | exit 0 |
| 4 | `dbt build --target=ci` against a Snowflake CI account | exit 0 (all models build, all tests pass) |
| 5 | `dbt source freshness` | exit 0 (or warn within tier thresholds) |
| 6 | `python3 plugins/data-platform/scripts/load-bridge-account-xref.py --dry-run` | exit 0; per-tier counts printed |
| 7 | `python3 plugins/data-platform/scripts/export-psm-dashboard.py --out /tmp/data.json --validate` | exit 0 |
| 8 | `python3 -m jsonschema -i /tmp/data.json plugins/edtech-partner-success/bi-report/data.export.schema.json` | exit 0 |
| 9 | `python3 scripts/check-psm-data-integrity.py --data /tmp/data.json --export-mode` | exit 0 (all 16 checks pass in export mode) |
| 10 | `bash scripts/audit-gates.sh` | clean, including Gate 53 |
| 11 | Layout snippet from §6 | "Layout OK" |
| 12 | `mf query --metrics health_score --group-by partner__account_uid` (MetricFlow) | returns 1 row per partner |

---

## 6. Layout snippet (verbatim from Tier 0)

```sh
python3 - <<'PY'
import fnmatch, json, subprocess
allowed = json.load(open(".repo-layout.json"))["allowed_globs"]
new = subprocess.run(
    ["git", "diff", "--name-only", "--diff-filter=A", "main"],
    capture_output=True, text=True,
).stdout.splitlines()
violations = [f for f in new if not any(fnmatch.fnmatchcase(f, g) for g in allowed)]
print("VIOLATIONS:" if violations else "Layout OK")
for v in violations: print(" ", v)
PY
```

---

## 7. PR shape

```sh
git add plugins/data-platform/scripts/snowflake-ddl/00-account-objects.sql \
        plugins/data-platform/scripts/snowflake-ddl/01-raw-schemas.sql \
        plugins/data-platform/scripts/snowflake-ddl/02-conformed-schemas.sql \
        plugins/data-platform/scripts/snowflake-ddl/03-grants.sql \
        plugins/data-platform/scripts/snowflake-ddl/04-clustering-keys.sql \
        plugins/data-platform/scripts/load-bridge-account-xref.py \
        plugins/data-platform/scripts/export-psm-dashboard.py \
        plugins/data-platform/scripts/export-psm-dashboard.test.py \
        plugins/data-platform/scripts/ingest-google-calendar.py \
        plugins/data-platform/dbt/psm_dashboard/dbt_project.yml \
        plugins/data-platform/dbt/psm_dashboard/profiles.yml.example \
        plugins/data-platform/dbt/psm_dashboard/README.md \
        plugins/data-platform/dbt/psm_dashboard/models/sources/_sources.yml \
        plugins/data-platform/dbt/psm_dashboard/models/staging/ \
        plugins/data-platform/dbt/psm_dashboard/models/intermediate/ \
        plugins/data-platform/dbt/psm_dashboard/models/marts/ \
        plugins/data-platform/dbt/psm_dashboard/models/semantic/psm_semantic.yml \
        plugins/data-platform/dbt/psm_dashboard/snapshots/snap_contract.sql \
        plugins/data-platform/dbt/psm_dashboard/seeds/seed_nces_districts.csv \
        plugins/data-platform/dbt/psm_dashboard/seeds/_seeds.yml \
        plugins/data-platform/.env.example \
        scripts/audit-gates.sh \
        .repo-layout.json \
        .gitignore

git commit -m "feat(data-platform): PSM dashboard Tier 0.5 — Snowflake + dbt + MetricFlow + bridge_account_xref + drop-in export (Q1=SFDC Service Cloud, Q2=SFDC CPQ, Q3=Google Calendar)"
git push -u origin feat/psm-dashboard-tier-0.5-real-connectors
```

**Open as DRAFT PR. PR body MUST include:**

1. **Q1/Q2/Q3 verification block:**

   ```
   ## Settling-step answers verified
   - Q1 (support tool) = SFDC Service Cloud (Case object via existing SFDC Fivetran)
   - Q2 (contract system) = SFDC CPQ (SBQQ__* via existing SFDC Fivetran)
   - Q3 (calendar) = Google Calendar (BUILD per knowledge file)

   Evidence:
   - `SELECT COUNT(*) FROM psm_raw.salesforce.case` = <NNN>
   - `SELECT COUNT(*) FROM psm_raw.salesforce.contract` = <NNN>
   - `SELECT COUNT(*) FROM psm_raw.salesforce.sbqq__subscription__c` = <NNN>
   - `SELECT COUNT(*) FROM psm_raw.google_calendar.events` = <NNN>
   ```

2. **Gate 53 output paste:**

   ```
   ## Gate 53 output
   ── Gate 53: PSM dashboard real-connector export ──────────────────────
   ✓ psm-real-export-validates (must_pass)
   ✓ psm-real-export-orphan-detected (must_fail)
   ```

3. **Bridge resolution summary:**

   ```
   ## bridge_account_xref tier distribution
   T0 leaid_exact:        <NNN>
   T1 leaid_compound:     <NNN>
   T2 leaid_fuzzy_high:   <NNN>
   T3 leaid_probabilistic (stewardship queue): <NNN>
   T4 external_id:        <NNN>
   T5 email_domain:       <NNN>
   T6 unresolved:         <NNN>
   ```

4. **MetricFlow measure list:** `mf list metrics` output.

5. **Drift table** showing the exported `data.json` validates against Tier 0's `data.export.schema.json` byte-for-byte at the shape level (per-field type match).

Do NOT mark PR ready-for-review without Matt's say-so.

---

## 8. Wall-handling

When a step does not move (Snowflake connection refused, dbt parse fails, Splink throws):

1. **Re-read the prior knowledge file FIRST** — the gotchas section answers ~80% of wall failures. Specifically:
   - Planhat connection refused → re-read `planhat-integration.md` § "Auth rotation" + § "Common gotchas" #2.
   - dbt source freshness failing → re-read `elt-freshness-sla-patterns.md` § "Common gotchas" #1 (pipeline success ≠ data freshness).
   - Splink runtime error → re-read the SKILL § "Step 6 — `resolution_audit`" + Splink's own docs.
   - Calendar duplicate rows → re-read `calendar-integration-google-outlook.md` § "Recurring events" (`singleEvents=true` discipline).
2. If the wall remains: take the documented default per `plan.md` Alternatives table with an inline comment in the PR body.
3. If silent AND no default: `AskUserQuestion`. Tier 0.5 should NOT hit Q1/Q2/Q3 (they're pre-stocked).

**Four worked examples (these have all happened on prior dashboard builds; the agent notes capture the resolution):**

1. **"Planhat sync is green but Snowflake `psm_raw.planhat.company` row count is 0."** Cause: per-model direction misconfigured to `Send to Provider` (the warehouse-owned default) instead of `Receive from Provider`. Fix: flip the direction in Planhat UI; first sync within 1h reconciles.

2. **"dbt build fails with `Compilation Error: 'fct_partner_health' not found`."** Cause: the model references `ref('int_partner_signals')` but the intermediate folder wasn't included in `models/` paths in `dbt_project.yml`. Fix: add `intermediate` to `model-paths:` in the project config.

3. **"`bridge_account_xref` T2 fires hundreds of false-positive matches across states."** Cause: Splink was run without the state-FIPS partition. Fix: per the SKILL § "Why tighter than consumer identity", the Jaro-Winkler comparison must be **state-bounded** (only compare names within the same state FIPS). Re-run with the partition.

4. **"`export-psm-dashboard.py` crashes mid-run with `KeyError: 'priority_score'`."** Cause: the export script tried to read `priority_score` from a mart that doesn't compute it (per Tier 0's `field-classifications.json`, it's `derived_at_render`). Fix: emit `null` for `priority_score` and `priority_breakdown` everywhere in the export; the renderer fills them.

---

## 9. What Codex MUST NOT do

(24 items.)

1. Add rendering changes to this PR (no `report.html`, no `generate-bi-report.py` edit, no `dashboard.html`).
2. Compute `priority_score` or `priority_breakdown` in any dbt model, in any Snowflake view, in the MetricFlow semantic layer, or in `export-psm-dashboard.py`. They are `derived_at_render` per Tier 0.
3. Bump any plugin's `version` in `plugin.json` or `marketplace.json`.
4. Add a CLAUDE.md milestone (Tier 1 owns that).
5. Re-author the priors flagged "do not re-author" in §1 (`planhat-integration.md`, `salesforce-cpq-integration.md`, etc. — extend with inline pointers, never copy).
6. Use Planhat OAuth + password auth — key-pair on a SERVICE user is the only supported path.
7. Invert Planhat's `sourceId` vs `externalId` convention.
8. Use `Contract.RenewalDate` as the renewal anchor — `Contract.EndDate` is.
9. Use `SELECT *` on any `SBQQ__*` table (10MB payload risk).
10. Skip the `_fivetran_deleted = FALSE` filter on any staging model.
11. Land any Planhat NPS verbatim, Calendar event title/description, or Contact email to a non-privileged role unmasked.
12. Store calendar events as local time without IANA timezone.
13. Mix `singleEvents=true` and `singleEvents=false` modes in the same staging pipeline.
14. Skip the Census Same-Name guard in the Splink loader.
15. Auto-publish a T3 (probabilistic) match without `reviewed_by IS NOT NULL`.
16. Embed LEAID directly in fact tables (use `dim_partner_lea_link`).
17. Use Dynamic Tables with `target_lag='1 minute'` — 15 min is the cost/freshness target.
18. Use `materialized='materialized_view'` for any cross-source join.
19. Use `ACCOUNT_USAGE` for any live freshness telemetry (90 min stale).
20. Skip clustering keys on `fct_partner_health`, `fct_calendar_event`, `fct_support_ticket`.
21. Introduce a third-party Python dep beyond `snowflake-connector-python`, `jsonschema`, and (for the bridge loader only) `splink`.
22. Crash `export-psm-dashboard.py` on a single-source failure — emit empty block with `last_succeeded_at`.
23. Commit `.env`, `profiles.yml`, `dbt_packages/`, or `target/`.
24. Mark PR ready-for-review without Matt's say-so. (Draft PR only at the end of this brief.)

End of Tier 0.5 brief.
