# QuickBooks Online integration

> **Last reviewed:** 2026-05-21. Sources: Intuit QuickBooks Online API docs (via Truto, Knit, Satva Solutions, Coefficient practitioner write-ups — primary developer.intuit.com docs are member-gated). Refresh when: (a) Intuit changes rate limits or auth mechanics, (b) refresh token expiration policy changes (currently 100-day rolling), (c) a new "Reconnect URL" or similar mandatory field appears in the developer portal, (d) QuickBooks Desktop becomes meaningfully relevant to the consulting practice.

## QBO vs QB Desktop — the critical distinction

**QuickBooks Online (QBO)** has a documented REST API with broad ELT-connector support (Fivetran ✅, Airbyte ✅, Hevo ✅, Stitch ✅, every major workflow tool). **All scope in this plugin's v0.1.0 is QBO.**

**QuickBooks Desktop** is materially different: far fewer ELT connectors; usually requires QuickBooks Web Connector + CData / Transaction Pro / Synder. **QB Desktop is deferred to v0.2.0 of this plugin.** When a Desktop engagement surfaces, route to `etl-pipeline-engineer` for the workaround pattern and flag the engagement as Desktop-specific in the decision record.

## Auth — OAuth 2.0 Authorization Code

1. **Access token lifetime:** 1 hour
2. **Refresh token lifetime:** **100-day rolling expiry** with notifications emailed to the developer at 30 days and 7 days before expiration
3. **Reconnect flow** triggers when refresh token expires — user must re-authorize the app
4. **Realm ID** is the QBO company identifier; included in every API call

### The token-refresh discipline

- **Refresh proactively**, not reactively — refresh the access token at ~50 minutes (before the 1-hour expiry), not after the API returns 401
- **Rotate the refresh token on every use** — the API returns a new refresh token in each token-exchange response; failure to persist the new one breaks the 100-day rolling window
- **Monitor refresh-token age** — alerting at 60 / 30 / 7 days before expiry; the developer email isn't sufficient for a production system

### 2026 watch — "Reconnect URL"

A new "Reconnect URL" field became mandatory in the Intuit developer portal in January 2026 (single-source claim from Truto blog; not corroborated against Intuit's release notes in this research pass). **Verify against Intuit Developer portal directly when implementing.**

## Rate limits

| Endpoint | Limit | Notes |
|---|---|---|
| Standard API | **10 req/s per realm-ID & app** | Concurrent ~10 |
| Batch endpoint | **120 req/min per realm-ID** | Each batch can have up to 30 operations |
| Bulk operations | Use batch wherever possible | Reduces request count materially |

**HTTP 429 / 403 on exceed.** Honor `Retry-After` header. Exponential backoff with ceiling.

**These figures come from practitioner write-ups** (Satva Solutions, Coefficient); the Intuit docs themselves use "subject to throttling" language. **Verify against Intuit Developer portal directly before quoting to a client.**

## Connector availability

| Vendor | QBO connector | Notes |
|---|---|---|
| Fivetran | ✅ | MAR-billed; deletes count toward MAR as of Jan 1, 2026 (cost-predictability risk) |
| Airbyte | ✅ | OSS + Cloud; credit-billed in Cloud |
| Hevo | ✅ | Event-based pricing |
| Stitch | ✅ | Maintenance mode under Qlik/Talend; don't recommend for new |
| Estuary | (verify) | Real-time CDC angle if it exists |
| n8n / Zapier | ✅ | Workflow tools; OK for low-volume SaaS-to-SaaS |
| Custom | ✅ | Airbyte CDK is the path when an ELT vendor's connector misses a needed entity |

## Common entities a dashboard needs

| Entity | Use case |
|---|---|
| `Customer` | Customer dimension |
| `Invoice` | Revenue fact |
| `Payment` | Cash-receipt fact |
| `Bill` / `BillPayment` | A/P fact |
| `Item` | Product / service dimension |
| `Account` | Chart of accounts |
| `JournalEntry` | GL adjustments |
| `Vendor` | Vendor dimension |
| `Employee` | Payroll dimension (limited; Payroll add-on has separate API) |
| `Transaction` | Cross-cutting transaction log |
| `Report` (P&L, Balance Sheet, Cash Flow) | Server-side rendered statements |

**Pattern:** ELT the transactional entities (Customer, Invoice, Payment, etc.) into the warehouse and build derived statements in dbt. Don't ELT the rendered `Report` endpoints — they're pre-aggregated by QBO and lose granularity.

## Modeling layer (dbt) — common marts

| Mart | Purpose |
|---|---|
| `dim_customer` | Customer dimension with active/inactive flag, segment, geography |
| `dim_account` | Chart of accounts with hierarchy + functional categorization |
| `dim_date` | Calendar dimension with fiscal-year alignment |
| `fact_invoice_lines` | Invoice-line-level revenue grain |
| `fact_payment` | Cash-receipt fact |
| `fact_bill_lines` | Bill-line-level expense grain |
| `fact_journal_entry` | GL adjustments |
| `mart_revenue_by_customer` | Aggregated revenue cube |
| `mart_ap_aging` | AP aging schedule |
| `mart_cash_flow` | Cash flow statement |
| `mart_pl_by_month` | Monthly P&L roll-up |

## PII / PHI considerations

QBO data includes customer PII (names, addresses, EINs/SSNs in some cases, payment-method references). Treat with care:

- **Field-level encryption** for stored PII (Postgres native or app-layer)
- **TLS in transit** (Intuit only allows HTTPS — but verify the destination DB / warehouse also enforces it)
- **Don't log raw API responses** containing PII
- **HIPAA scope:** QBO itself is NOT a HIPAA-covered service. If the engagement involves PHI (rare with QBO directly, but possible via custom fields), route through `ravenclaude-core/security-reviewer`

## Common gotchas

1. **Sandbox vs production realm-IDs are different** — `OAUTH_BASE_URL` differs between sandbox-quickbooks.api.intuit.com and quickbooks.api.intuit.com
2. **Multi-currency** — QBO Plus/Advanced support multi-currency; pulling FX-converted values requires explicit query parameter
3. **Cleared vs Reconciled** — `Payment.CleardDate` is settled bank-reconciliation; `Payment.TxnDate` is recorded. Don't confuse them in cash-flow reports.
4. **Voided vs deleted transactions** — voided entries remain queryable (with status), deleted are gone. Dashboards should respect status.
5. **Custom fields** — accessible but require explicit fetching; not always returned by default

## Pattern recommendation for a typical QBO engagement

1. **Source:** Airbyte Cloud Standard OR Fivetran free tier (if <500k MAR and client takes over)
2. **Sync cadence:** Daily (nightly) for most engagements; hourly only if the dashboard's value depends on intraday updates
3. **Destination:** Supabase Pro or client's existing Postgres / warehouse
4. **Modeling:** dbt Core with the marts above
5. **Dashboard:** Evidence.dev for case-study marketing site; Apache Superset / Metabase for client deliverable; Cube + custom React if productizing
6. **Embed (if Case B):** JWT-secured iframe with tenant scoping via JWT claim → RLS on `tenant_id`

## Refresh triggers

- Intuit changes rate limits or auth mechanics
- Refresh token expiration policy changes
- New mandatory developer-portal field appears
- QuickBooks Desktop becomes a relevant engagement (would trigger a new `quickbooks-desktop-integration.md` file)
- A primary-source verification fails (rate limit numbers change, etc.)
