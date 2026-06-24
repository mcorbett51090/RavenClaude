# Plan A — Architecture-First Build Plan: Unified Data Hub Platform

**Panel:** A (Opus) · **Lens:** build-it-right-for-the-long-haul · **Date:** 2026-06-24 · **Slug:** data-hub-platform

## North-star principle
Two kinds of code: **platform code identical across every instance**, and **per-customer artifacts
(connector versions enabled, dashboards, metric defs) that vary**. The architecture's job is to keep
that line bright. The B.4 maintenance disaster happens when a connector fix lives in one instance's
code and rots in the others. So: **connectors are versioned data published from one registry, never
per-instance code.**

## 1. Target architecture (stack)
| Layer | Choice | Why |
|---|---|---|
| Runtime | **TypeScript / Node 22 LTS** | one language across SDK/API/dashboards; Nango/n8n prior art is TS; Claude authors TS well |
| Framework | **NestJS modular monolith** | DI + module seams (auth/sync/vault/registry) inside one deployable; no premature microservices |
| Control-plane DB | **Postgres 16 (one per instance)** | connections, cursors, audit, run-log, registry pins |
| Analytics landing | **Postgres `raw`/`staging`/`marts`**, DuckDB+Parquet escape hatch for >~10M-row sources | single-tenant data is small-medium; one Postgres trivial per customer |
| Sync orchestration | **Temporal (self-hosted, in-instance)**; BullMQ+Redis fallback at P3 gate | durable execution = free retry/backoff/heartbeat/replay = run-log+DLQ backbone |
| Vault | **app-level AES-256-GCM, per-customer DEK, KEK in KMS off the app DB** | satisfies G1 1a/1b |
| Object store | **S3-compatible (MinIO if self-host)** | DLQ payloads, Parquet, dry-run previews, raw capture |
| Layman UI | **React served by the app** | small form-heavy surface |
| Dashboards | **Evidence.dev (BI-as-code) over the semantic layer** | versioned `.md`+`.sql`, Claude-native |
| Deploy unit | **one Docker Compose/Helm release per customer** | whole instance is one artifact |

**Vault:** envelope encryption — one DEK per customer instance; every token AES-256-GCM under it
(unique nonce + GCM tag). DEK stored **wrapped** by a KEK that lives in a KMS the app DB cannot reach
(AWS/GCP KMS or HashiCorp Vault Transit). App calls `KMS.Decrypt` at boot, holds plaintext DEK
in-memory only. If Supabase is mandated → target the Vault interface, not raw pgsodium TCE (G1 1c).
Every decrypt/grant/refresh/revoke → immutable hash-chained audit log. Single-tenant + per-customer
DEK means one instance's compromise can't decrypt another's.

## 2. Connector framework (the crux — answers B.4)
Thesis: **~80% reused platform + ~20% per-source declaration; the per-source part is versioned data
from one registry, never per-instance code.**
- **Three-primitive split (steal Nango):** **Auth** (OAuth2.1+PKCE, refresh, revoke, reconnect) +
  **Transport/Proxy** (credential injection, pagination, rate-limit, backoff, retry budget, raw
  capture) written **once** in the SDK; **Functions** (extract→normalize→load inbound; map→upsert
  outbound) is the thin per-source layer — the only surface that varies, the only surface that breaks.
- **Declarative-first, code escape-hatch (steal Airbyte CDK):** a connector = **YAML manifest +
  optional thin TS hooks**. Manifest declares auth (incl. per-connector `pkce` flag for older
  providers), transport (rate_limit/retry/pagination), streams (primary_key, `cursor_field`,
  `cdm_entity`), outbound (`upsert_key`, `dry_run_required`). `defineConnector(manifest)` compiles
  YAML→`Connector`; common case is zero hand-written TS. An upstream change is usually a one-line
  manifest edit.
- **Versioned connector REGISTRY (idea #15 — the survival mechanism):** publish `{id}@{semver}` with
  content hash, changelog, `api_break_class`. Each instance records its `connector_pin` per source →
  **fleet view** ("which instances run `stripe@<3.2.0`?"). Break-fix: bump → publish → registry emits a
  **fleet advisory** → controlled per-instance upgrade (canary → dry-run → promote); rollback re-pins.
  **No instance is ever hand-patched.** Audit trail serves client-compliance.

## 3. Reporting / semantic layer
**Cube (headless semantic layer) as the metric contract + Evidence.dev as the authoring surface.**
Cube = single source of metric truth (`MRR`/`churn`/`health` defined once, joins+access+caching);
Claude calls `query({measures:['Revenue.mrr']})`, can't reinvent MRR per customer. Evidence = `.md`+
`.sql` in Git, Claude-native, diff-able. **Contract:** dashboards query only Cube measures —
**a CI lint fails any dashboard SQL referencing a raw/staging table.** dbt still does transforms
(raw→staging→marts) but **metrics live in Cube, not scattered in dbt**. Chosen over dbt+Lightdash
(couples metrics to dbt DAG + a Lightdash server per instance; Cube is lighter + API-first for a
programmatic Claude author).

## 4. Persona UX
- **Layman wizard:** pick source (curated catalog) → guided OAuth (PKCE per manifest) → **dry-run
  preview** (sample + counts, no write) → **freshness/observability** (last sync, row counts,
  staleness badge vs SLA) → **reconnect** on `invalid_grant` (re-consent; RFC 7009 revoke where
  supported) → **replayable run log** (failed records link to DLQ).
- **Vibecoder:** Evidence project (Git) + Cube model + Claude. Claude reads Cube schema, writes
  Evidence pages querying Cube SQL API, previews, commits; vibecoder reviews diff + merges. CI lint
  enforces metric-layer-only. Reusable dashboard templates (CRM health, AR aging, calendar util).

## 5. Data model
- **Common Data Model per category** (idea #3): CRM (`account`/`contact`/`opportunity`/`activity`),
  Accounting (`customer`/`invoice`/`payment`/`subscription`), Calendar (`event`/`attendee`),
  Messaging/notes (`message`/`channel`/`note`). Each entity = stable columns + `source_custom` JSONB;
  **field-mapping UI** (idea #10) maps source→CDM (incl. custom) without code, versioned per connector.
- **Storage:** `raw.{source}_{stream}` → `staging.{cdm_entity}` (dbt) → `marts.*` (feed Cube).
- **Sync:** incremental per-stream cursors (3b); schema-drift detector off raw capture (surface, never
  silently drop; structural change → registry advisory); idempotent outbound upsert (3a); DLQ in S3;
  append-only hash-chained audit (idea #12).

## 6. Phased delivery
- **P0 Foundation & vault** — skeleton + correct vault before any token. Accept: encrypt→store→decrypt
  round-trip; DB dump has **no plaintext secret, no KEK** (prove by denying KMS → decrypt fails);
  audit append-only + hash verifies. Exit: security-reviewer sign-off on 1a/1b.
- **P1 Thin vertical** — one connector (**Stripe**) → store → CDM accounting → Cube `mrr` → **one
  Evidence dashboard Claude authors**. Accept (scope success signal): layman connects via OAuth,
  zero hand-edited secrets; dry-run counts accurate; re-run = no dupes (cursor); dashboard SQL uses
  only Cube measures (lint passes).
- **P2 SDK hardening + registry v1** — expressive manifest; escape-hatch hooks; registry (publish,
  pin, fleet advisory, canary, rollback); +2–3 connectors (CRM + accounting + calendar). Accept: a new
  declarative connector → synced data **<1 day**; fleet view correct; canary+rollback clean; HubSpot→
  Salesforce swap doesn't change dashboard SQL (CDM stability).
- **P3 Durable engine + observability + drift + DLQ** — Temporal workflows; central rate-limit/retry;
  freshness SLA/badges; drift detector; DLQ + replayable run log; reconnect/revocation. Accept: kill
  mid-sync → resumes from cursor, no loss/dupes; 429 → backs off in budget; field added → surfaced not
  dropped; failed record → DLQ → replays; token expiry → reconnect restores.
- **P4 Reverse-ETL outbound + semantic maturity** — outbound (map + idempotent upsert), per-dest
  `upsert_key`, mandatory dry-run, per-sync diffing; Cube for all CDM categories; dashboard template
  library + CI lint. Accept: run twice → no dupes; dry-run aborts write nothing; unchanged source →
  zero outbound rows; raw-table dashboard PR fails CI.
- **P5 Per-customer ops + fleet operability** — one-command provisioning (+DEK/KEK bootstrap);
  backup/restore; fleet dashboard (versions/health/advisory); fleet upgrade orchestration. Accept:
  `provision <customer>` working instance **<30 min**, no manual secrets; fleet-wide fix via registry
  with per-instance audit; restore intact.

## 7. Dependency DAG
`P0 → P1 → {P2, P3}`; `P2 → P3`; `P2 → P5`; `P3 → P4 → P5`; `P3 → P5`. Critical path
**P0→P1→P2→P3→P4→P5**. Parallel: after P1, CDM defs + Cube models parallel with P2 SDK; within P2 each
connector independent once SDK frozen; P3 observability UI parallel with Temporal swap; P5 fleet
dashboard can start once P2 pin model exists. Hard blockers: no real token before P0 green; no outbound
(P4) before durable execution (P3).

## 8. Alternatives (trade-offs)
1. **Warehouse:** Postgres+DuckDB (chosen — trivial per instance) vs Snowflake/BigQuery per customer
   (elastic but adds billing+ops surface most instances won't need).
2. **Sync engine:** Temporal (chosen — free durability) vs BullMQ+Redis (lighter, hand-build resume).
3. **Semantic layer:** Cube+Evidence (chosen — enforced metric API) vs dbt+Lightdash (couples to dbt +
   server per instance) vs Evidence-only (no enforced layer → SQL sprawl, rejected).
4. **Connector packaging:** declarative manifest+SDK (chosen) vs service-per-connector (more ops) vs
   hand-coded monolith (the B.4 trap).
5. **Connector logic:** build from scratch (Matt's pin) **borrowing** Nango/Airbyte patterns vs
   vendoring an OSS engine as a library (less control, vendor dep).

## 9. Hardest risks + mitigations
Connector maintenance × instances (**highest** — three-primitive split + manifests + registry fleet
roll-out); secret blast radius (per-customer DEK + KEK off-DB + negative tests); per-customer ops toil
(one artifact + `provision`<30min + fleet dashboard/upgrade); dashboard SQL sprawl (Cube + CI lint);
reverse-ETL double-write (durable engine gate + upsert + dry-run); schema drift (raw capture + detector
+ advisory); long-tail API immaturity (SDK escape-hatch + `api_break_class` + freshness SLA visibility);
token refresh failures (Auth primitive + reconnect UX).

## 10. Definition of done
(1) Security floor: all creds AES-256-GCM/per-customer DEK/KEK off-DB; DB dump no plaintext/KEK; full
audit; security-reviewer sign-off. (2) Thin vertical generalized: layman connects ≥2 sources, zero
hand-edited secrets, Claude dashboard on semantic layer. (3) From-scratch sustainable: new declarative
connector <1 day; registry versioning; fleet-wide break-fix with canary+rollback, no per-instance code.
(4) Production ingestion: incremental, resumable, rate-limit-aware, drift-detecting, DLQ + run log +
freshness. (5) Safe reverse-ETL: idempotent, dry-run-gated, diff-minimized, durable. (6) Metric
contract enforced (CI fails raw-table dashboards; CDM swap stability). (7) Fleet operability:
`provision`<30min; fleet dashboard; registry fix with audit; clean restore.
