# Planhat integration

> **Last reviewed:** 2026-06-03. Sources: Planhat public documentation (developers.planhat.com) `[unverified — training knowledge; confirm endpoints and limits at build time]`. Refresh when: (a) a first-class managed Fivetran/Airbyte Planhat connector ships and reaches production-ready status, (b) Planhat changes its REST API surface or rate limits, or (c) the Planhat `externalId` → Salesforce Account ID sync behavior changes.

## Connector strategy — BUILD (custom Python loader)

Planhat is a niche Customer Success platform. As of 2026, **no first-class production Fivetran or Airbyte connector exists for Planhat** `[unverified — verify both catalogs at build time; this is the single most important thing to check before scoping the loader]`. The strategy is a **BUILD** — a Codex-authored Python loader using Planhat's REST API, following the connector-developer pattern.

This is the one custom connector worth building for the CS-health platform. The API surface is well-documented relative to the niche, the data volume is low (one row per company/user per sync, not billions of events), and the critical identity-resolution field (`externalId`) is a first-class API field.

**Before building:** search the Airbyte Hub ([hub.airbyte.com](https://hub.airbyte.com)) and Fivetran connector catalog for a current Planhat listing. If a managed connector has shipped since this file was last reviewed, prefer BUY over BUILD for the standard objects.

## Auth

- **API key** (bearer token) — Planhat issues a per-workspace API key from the API settings page `[unverified — confirm current auth mechanism in Planhat docs]`
- Include as `Authorization: Bearer <API_KEY>` on every request
- Store in a secrets vault; never in the repo or Codex-generated output

## API surface — entities relevant to CS health

All endpoints are relative to `https://api.planhat.com` `[unverified — confirm base URL]`.

| Entity | Endpoint | CS-health use |
|---|---|---|
| **Companies** | `GET /companies` | The account spine — one row per customer company |
| **End-users / Contacts** | `GET /endusers` | Contact dimension; secondary to companies for health scoring |
| **Metrics / Usage** | `GET /metrics`, `GET /analytics` | Product usage — DAU, feature adoption; the strongest churn-leading signal |
| **NPS answers** | `GET /npsAnswers` | NPS score + verbatim (verbatim is PII — mask in warehouse) |
| **Conversations** | `GET /conversations` | CSM-to-customer interactions; touch-cadence signal |
| **Tasks** | `GET /tasks` | Open/overdue CSM tasks; cadence discipline signal |
| **Health scores** | Embedded on `GET /companies` as `health` sub-object | Planhat's native health score — surface as `planhat_health_score` anchor |

`[unverified — confirm all endpoint paths and response shapes in Planhat API docs; the analytics/metrics endpoint path in particular varies across Planhat versions]`

## Incremental sync — cursor strategy

- **Cursor field:** `updatedAt` on every entity (ISO 8601 timestamp) `[unverified — confirm the exact field name; Planhat may use `updatedAt`, `updated`, or `_updatedAt` depending on entity]`
- **Query parameter:** `updatedAfter=<ISO8601>` to pull only records changed since the last watermark `[unverified — confirm param name]`
- **Watermark discipline:** read `last_loaded_at` from a control table; pull `updatedAt > last_loaded_at`; write via MERGE on the Planhat-native `_id`; advance the watermark only after a successful commit (see [`../best-practices/ingest-idempotent-and-replayable.md`](../best-practices/ingest-idempotent-and-replayable.md))
- **Backfill path:** chunked by 30-day windows; each chunk independently retryable (see [`../best-practices/connector-incremental-with-backfill.md`](../best-practices/connector-incremental-with-backfill.md))

## Rate limits

Planhat's rate limits are approximately **1,000 requests/hour per workspace** for the standard REST API `[unverified — training knowledge; confirm from Planhat rate-limit docs or by observing `X-RateLimit-*` response headers in Phase 0]`. Practical impact:

- For the CS-health build (hundreds, not millions, of companies), daily incremental syncs fit easily under the ceiling
- Apply exponential backoff on `429` responses; honor `Retry-After` headers if present
- Dead-letter log failed records rather than silently dropping them

## Raw JSON landing strategy

**Land the full raw API response as JSON in Snowflake RAW.** Parse fields in dbt staging models. Rationale: Planhat's API shape has drifted across product versions; if the landing layer is the raw JSON blob, an API field rename breaks only the dbt staging parse, not the loader itself. This is the load-then-transform ELT discipline applied to a niche API.

```python
# Loader pseudocode shape — Codex fills in the real implementation
# See ingestion/_lib/ for watermark.py, upsert.py, backoff.py
for entity in ['companies', 'endusers', 'npsAnswers', 'tasks']:
    records = planhat_client.fetch_incremental(
        entity=entity,
        updated_after=watermark.read(entity),
    )
    upsert.merge(
        table=f'raw.planhat_{entity}',
        records=records,
        primary_key='_id',        # Planhat's native primary key
        raw_json_column='_raw',   # full response blob
    )
watermark.advance(entity, current_run_at)
```

## The `externalId` field — the identity-resolution master key

**The single most important Planhat field for the CS-health build.** Planhat's `externalId` on a Company record is designed to carry the Salesforce Account ID when the Planhat ↔ Salesforce native sync is configured. If this field is populated:

- Resolution between Planhat and Salesforce is **exact and deterministic** — level 1 in the precedence ladder
- The `bridge_account_xref` entry for this Planhat company gets `match_method = 'external_id'` and `confidence = 'high'`
- No fuzzy matching is needed for these records

**Phase 0 verification task (Open Question #1 from the build plan):** `GET /companies` for a sample of known accounts and inspect the `externalId` field. If it is populated with Salesforce Account IDs, the identity-resolution problem collapses from hard to trivial for the Planhat source. If it is empty, configuring the Salesforce sync in Planhat settings is a cheap ops task that should happen before writing any matching code.

See [`../best-practices/resolve-identity-deterministic-keys-before-fuzzy.md`](../best-practices/resolve-identity-deterministic-keys-before-fuzzy.md) for the full resolution ladder.

## Health score — surface as anchor, do not recompute

Pull Planhat's native `health` score (the numeric/tier value on the Company record) as `planhat_health_score` in the mart. **Do not recompute or replace it in Phase 1.** The CS team anchors on this score; replacing it with a custom composite on day one invites "why doesn't this match Planhat?" challenges that undermine adoption. The Phase 1 strategy: surface Planhat's score as the anchor alongside discrete Intercom and Slack sub-indicators. See the build plan §3 Conflict 3.

## dbt modeling — common staging + mart models

| Model | Purpose |
|---|---|
| `stg_planhat__companies` | Company dimension seed — typed, 1:1 with raw; `externalId` surfaced as `sfdc_account_id_candidate` |
| `stg_planhat__nps_answers` | NPS responses — NPS score surfaced; verbatim field **masked / excluded** (PII) |
| `stg_planhat__metrics` | Usage/DAU metrics per company per period |
| `stg_planhat__tasks` | Open + overdue CSM tasks per company |
| `stg_planhat__conversations` | CSM touch history |
| `dim_planhat_company` | Intermediate — adds `account_key` via `bridge_account_xref` |
| `fct_account_health_snapshot` | Mart — `planhat_health_score` + usage signals (see build plan §3.2) |

## PII / data sensitivity

- **NPS verbatim** — customer-written text; treat as PII. Apply Snowflake dynamic masking on the verbatim column; restrict raw access to the `loader` role. Surface only the NPS score (0–10) and response date to the `analyst` / dashboard roles.
- **End-user records** — contain name, email. Treat as PII; use Snowflake column-level masking for email in non-privileged roles.
- **Retention:** align with the engagement's documented compliance regime (GDPR/CCPA) — NPS verbatim and contact details may be subject to right-to-erasure requests. Document the deletion path in Phase 0.

## Common gotchas

1. **`externalId` empty** — the most common issue. Check before assuming deterministic resolution is available; configure the Planhat↔Salesforce sync if needed.
2. **Health score composition is opaque** — Planhat's native health score is a black box composed of rules the CS team configured. Document what it is (rules or ML, if known) so a future custom composite is additive, not a replacement.
3. **Metrics endpoint shape** — the `/metrics` or `/analytics` endpoint may return time-series data in a different shape than the entity endpoints (company ID + date + metric name + value, not one-object-per-company). Parse carefully in the dbt staging layer.
4. **`npsAnswers` verbatim is PII** — new analysts will assume it is safe to surface. Add a masking policy before Phase 0 is done, not after.
5. **Company record vs. end-user record** — Planhat has both; CS-health metrics live at the Company grain. End-user records are used for contact-level NPS attribution and CSM assignment; don't conflate the two in the staging model.
6. **Historical health score backfill** — Planhat may not support pulling historical health score values via the API `[unverified — confirm whether the health-score history endpoint exists; this affects Phase 2 trend analysis]`.

## Refresh triggers

- A first-class managed Planhat connector ships on Fivetran or Airbyte (moves strategy from BUILD to BUY)
- Planhat changes its REST API base URL, auth mechanism, or entity structure
- Planhat rate limits are confirmed or updated from the Phase 0 API inspection
- The Planhat ↔ Salesforce native sync behavior for `externalId` changes
