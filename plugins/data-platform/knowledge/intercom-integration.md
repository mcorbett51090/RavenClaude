# Intercom integration

> **Last reviewed:** 2026-06-03. Sources: Intercom developer documentation (developers.intercom.com), Fivetran Intercom connector docs, Airbyte Intercom connector docs `[unverified — training knowledge; confirm connector versions and API limits at build time]`. Refresh when: (a) Intercom changes its REST API version, pagination model, or rate-limit tiers, (b) the Intercom ↔ Salesforce native integration behavior for the `company_id` field changes, or (c) a material change in the managed connector's supported objects.

## Connector strategy — BUY (managed connector)

Intercom is well-supported by all major ELT vendors. This is a **BUY** decision — use Fivetran or Airbyte Cloud's managed Intercom connector. Do not build a custom loader. The managed connector handles OAuth token management, API version pinning, incremental cursor management, and schema evolution.

**Connector selection:** check the current Fivetran MAR pricing implications before enabling, particularly if the Intercom workspace has high conversation volume — Fivetran's 2026 pricing counts rows including deletes/updates as MAR, which can be cost-surprising on busy support orgs (see [`../knowledge/ipaas-connector-landscape-2026.md`](../knowledge/ipaas-connector-landscape-2026.md)).

## Auth

- **OAuth 2.0** — the standard for managed connectors; the ELT vendor handles the token exchange
- **API key (bearer)** — available for custom/script access `[unverified — confirm Intercom still supports API keys for non-OAuth access in the current version]`
- The Intercom app must have the correct scopes: `read_conversations`, `read_users`, `read_companies` at minimum

## API surface — entities relevant to CS health

| Entity | Managed connector model | CS-health use |
|---|---|---|
| **Conversations** | `conversation` (with `conversation_parts`) | Support volume, priority, resolution time, CSAT, PII-containing bodies |
| **Conversation parts** | Sub-object of `conversation` | Individual messages within a conversation; needed for first-response-time calculation |
| **Contacts** | `contact` (unified contacts/leads model) | Customer contact dimension |
| **Companies** | `company` | The account-level join surface; carries the cross-reference to Salesforce |
| **Admins (agents)** | `admin` | Support rep dimension for assignment/workload analysis |
| **Tags** | `tag` | Classification/triage signal (e.g., `escalation`, `churn-risk` tags) |

**Pull conversation parts, not just conversation headers.** The first-response time (a key CS health signal) requires the timestamp of the first admin reply in `conversation_parts` — it is not available on the conversation header alone.

## Identity resolution — the `company_id` field

The `company_id` field on an Intercom Company record is the **primary cross-reference hook to Salesforce**. When Intercom's native Salesforce integration is configured, this field is populated with the Salesforce Account ID `[unverified — confirm the Intercom Salesforce integration sets company_id vs. a custom attribute; behavior may depend on integration version and which direction the sync flows]`.

**Phase 0 verification task (Open Question #1 from the build plan):** `GET /companies` for a sample of known accounts and inspect `company_id`. If populated with Salesforce Account IDs, resolution between Intercom and Salesforce is exact and deterministic — level 1 in the precedence ladder. If not, configuring the Salesforce integration in Intercom is a cheap ops task before writing any matching code.

See [`../best-practices/resolve-identity-deterministic-keys-before-fuzzy.md`](../best-practices/resolve-identity-deterministic-keys-before-fuzzy.md) for the full resolution ladder and `bridge_account_xref` pattern.

## Rate limits

Intercom's rate limits depend on the workspace plan `[unverified — training knowledge; confirm current tiers from Intercom developer docs before building the loader or sizing syncs]`. Approximate guidance:

- **REST API:** ~500 requests / minute per workspace at standard tiers; higher for premium `[unverified]`
- The managed connector handles rate-limit-aware retry; for any custom scripts (e.g., Phase 0 verification calls), apply exponential backoff on `429` responses and honor `Retry-After` headers
- Conversation-parts fetches are per-conversation; for high-volume workspaces, the page-through of conversations is the rate-limit bottleneck, not the company/contact pulls

## Incremental sync

- **Conversations:** incremental on `updated_at`; managed connector handles cursor
- **Contacts / Companies:** incremental on `updated_at`
- **Soft deletes:** Intercom may soft-delete contacts/companies; verify deleted-record handling in the managed connector configuration — a silently dropped deletion looks like a healthy account with zero activity

## PII / data sensitivity — CRITICAL

**Conversation bodies are PII.** Every `conversation_part.body` contains customer-written or support-agent-written free text. This is the most sensitive data in the CS-health build.

**Required controls before Phase 1:**
1. Apply **Snowflake dynamic data masking** on the `body` column in `stg_intercom__conversation_parts` — restrict raw body access to the `loader` role only
2. The `analyst` role and all Sigma users see the body column as `[MASKED]` or `NULL`
3. The CS-health dashboard surfaces only **derived signals** from conversations (count, priority, resolution time, CSAT score, tag — never free text)
4. Include Intercom data in the Phase 0 PII inventory and retention/deletion plan
5. Route through `ravenclaude-core/security-reviewer` if the engagement is subject to GDPR, CCPA, or SOC 2

**NPS verbatim:** if Intercom surfaces NPS verbatim text (via the built-in NPS tool), treat it with the same masking discipline as conversation bodies.

## CS health signals from Intercom

These are the derived signals the CS-health mart should compute from Intercom data — never the raw conversation text:

| Signal | Computation | Health interpretation |
|---|---|---|
| `open_support_tickets` | Count open conversations per company per snapshot date | Volume spike pre-renewal = risk |
| `p1_p2_tickets_30d` | Count conversations tagged high-priority / P1 / P2 in last 30 days | P1/P2 rate matters more than raw volume |
| `median_first_response_hrs` | Median of (first admin reply `created_at` − conversation `created_at`) per company | Slow support erodes trust at renewal |
| `csat_score_30d` | Average CSAT rating per company in last 30 days | Direct satisfaction signal |
| `ticket_resolution_rate_30d` | Resolved / total conversations in last 30 days | Chronic open tickets = unresolved issues |
| `ticket_volume_trend_7d` | 7-day rolling count vs prior 7-day period | Direction beats absolute level |
| `reopened_conversations_30d` | Conversations marked resolved then re-opened | Re-opens signal failed resolution |
| `intercom_support_load` | Derived tier (Low / Medium / High) from the above signals | Additive sub-indicator alongside Planhat health anchor |

## dbt modeling — common staging + mart models

| Model | Purpose |
|---|---|
| `stg_intercom__conversations` | Conversation grain — metadata, priority, status, tags, CSAT; `body` masked |
| `stg_intercom__conversation_parts` | Message-part grain — timestamps for first-response calculation; `body` masked |
| `stg_intercom__companies` | Company dimension — `company_id` surfaced as `sfdc_account_id_candidate` |
| `stg_intercom__contacts` | Contact dimension — PII columns masked for non-privileged roles |
| `int_intercom__conversation_metrics` | Intermediate — compute ticket volume, first-response time, CSAT per company |
| `dim_intercom_company` | Adds `account_key` via `bridge_account_xref` |
| `fct_support_conversations` | Mart — one row per conversation; resolved, priority, first_response_at, csat |
| `fct_account_health_snapshot` | Mart — contributes `intercom_support_load` sub-indicator (joined from int layer) |

## Common gotchas

1. **Conversation parts required for first-response time** — the conversation header alone does not carry the first-admin-reply timestamp; you must join to `conversation_parts` filtered to the first `admin`-type part.
2. **Contact vs. Company grain** — Intercom contacts are individuals; companies are the account-level entity. The health signals live at the company grain; don't compute them at the contact grain and aggregate up (you'll double-count conversations where multiple contacts are involved).
3. **Deleted companies** — if a company is merged or deleted in Intercom, the managed connector may soft-delete or hard-delete. A silently dropped company looks like zero ticket volume; verify deletion handling.
4. **CSAT only if enabled** — CSAT is an optional feature; verify it is turned on before relying on it as a health signal. If disabled, surface `NULL` explicitly (never zero — zero CSAT and no CSAT are very different).
5. **Tag taxonomy** — Intercom tags are workspace-specific; audit the existing tag set before relying on tags like `escalation` or `churn-risk` in the health tier logic. The tags may not exist or may have inconsistent usage.
6. **`company_id` field vs. custom attributes** — some Intercom workspaces store the Salesforce Account ID in a custom company attribute rather than the built-in `company_id` field. Inspect the actual API response in Phase 0.
7. **Conversation volume at renewal time** — the health signal is not just raw volume but volume relative to renewal proximity; build the mart to support `support_load AND days_to_renewal < 90` as a compound signal.

## Recommended sync configuration

- **Cadence:** every 6 hours for conversations (support events move fast); daily for companies/contacts
- **Backfill:** 90+ days for ticket history (the CS-health signals reference 30/60/90d windows)
- **Incremental cursor:** `updated_at` (managed connector handles this)
- **Field selection:** if the managed connector allows column exclusion, exclude raw `body` columns at the connector level to avoid landing PII in raw — alternatively, rely on Snowflake masking at the staging layer

## Refresh triggers

- Intercom changes its API version or rate-limit tiers
- The Intercom ↔ Salesforce native integration behavior changes (affects `company_id` identity resolution)
- The managed connector adds or removes objects relevant to CS health
- PII/compliance posture changes (new data residency requirement, GDPR DPA update)
