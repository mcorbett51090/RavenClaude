# G1 — Research + Fact-Verification (Unified Data Hub Platform)

> Saved verbatim from the G1 deep-researcher pass (2026-06-24). Two panels read this before planning.

## A. Competitive scan + ideas to steal

### Reverse-ETL / data activation
- **Hightouch** — *Steal: upsert + dedupe-key idempotency and first-class sync observability.* Reruns
  must not double-write; per-sync diffing syncs only changed rows; every destination-API op/error is
  surfaced. (hightouch.com/platform/reverse-etl)
- **Census** — *Steal: "sync = model + mapping + dedupe key + schedule"* so each outbound integration
  is configuration, not code.

### iPaaS / workflow automation
- **n8n** — *Steal: node SDK + "custom API action on an existing node."* A connector is a typed node
  (auth descriptor + operations); new operations against an already-authed source are cheap. Closest
  model to "core connections live in the app."
- **Workato** — declarative connector SDK (constrained Ruby DSL) — cautionary data point on
  code-native vs declarative.
- **Make / Zapier** — *Steal: trigger/action + polling-vs-webhook taxonomy and per-step run-log replay UX.*

### Unified-API layers (study the abstraction even though we build from scratch)
- **Nango** — *Steal the 3-primitive split: Auth (managed OAuth + refresh + storage), Proxy (credential
  injection + retries + rate-limit), Functions (per-source sync/action logic).* Most directly
  borrowable architecture: separate reusable auth+transport from per-source logic. Sync engine also
  does pagination, batch save, delete-tracking.
- **Merge.dev / Apideck** — *Steal the Common Data Model:* normalize "a contact is a contact" across
  Salesforce/HubSpot; Apideck adds a field-mapping UI for custom fields. A small Common Model per
  category (CRM, accounting, calendar) lets dashboards target a stable schema.

### Connector-SDK pattern (the from-scratch enabler)
- **Airbyte** — *Steal the declarative low-code connector manifest (YAML: streams, pagination, cursors,
  auth) compiled by a CDK.* No-code Builder → connector in <10 min; YAML/CDK escape hatch covers the
  weird 20%. Canonical answer to "make each new connector cheap."

### Embedded analytics / semantic layer
- **Cube** — *Steal the headless semantic layer:* define metrics/dimensions/joins/access once, expose
  via SQL/REST/GraphQL. Claude builds against `get_metric(mrr)`, not raw joins.
- **Evidence.dev** — *Steal "BI-as-code":* dashboards = SQL + Markdown in Git → static sites. Fits
  "Claude builds the dashboard per customer" (versioned `.md`/`.sql`, not GUI clicks).
- **Lightdash** — metrics in the dbt model layer, Git-native, diff-able per customer.
- **Metabase** — dead-simple non-technical exploration + embedding as a self-serve fallback.

### Low-code internal tools
- **Retool** — *Steal app-builder UX:* connect-any-source + drag components + SQL/JS + AI-generates the
  app from a prompt. Mirrors the "vibecoder builds dashboards with Claude" persona.
- **Budibase** — open-source, self-hostable, built-in DB, per-instance deploy — essentially the
  single-tenant delivery model productized.

### CDP / customer-success (consumer-side use case)
- **Planhat / Pocus** — *Steal the "blend product + billing + CRM signals into one health view" data
  model.* Planhat is itself a source — study what joined shapes customers want (health scores,
  usage-to-billing, renewal risk).

### IDEAS THE USER IS LIKELY LEAVING OUT
1. **Declarative connector SDK / manifest** so each new connector = config + thin logic, not a bespoke
   service. Without it, "from scratch" silently means "N hand-built microservices to maintain."
2. **Semantic / metrics layer** between raw data and dashboards — define `MRR`/`churn`/`health` once.
3. **Common Data Model per category** so a HubSpot→Salesforce swap doesn't rewrite every dashboard.
4. **Incremental sync with cursors/CDC, not full refresh** (per-stream cursor; pull deltas).
5. **Sync observability + freshness SLA per source** ("last successful sync," row counts, staleness badge).
6. **Idempotent outbound writes** (upsert keys + dedupe so reverse-ETL is safe to retry).
7. **Schema-drift handling** (detect source field add/remove/rename; surface, don't silently drop).
8. **Per-source rate-limit + backoff + retry budget** centralized in the transport layer.
9. **OAuth token refresh + revocation + re-consent ("reconnect this source") UX.**
10. **Field-mapping UI** (map source field → model field without code, incl. custom fields).
11. **Dead-letter queue + replayable run log** (failed records land somewhere inspectable + re-runnable).
12. **Audit log** of every connection, token grant, sync, and outbound write (trust + client compliance).
13. **Per-customer data + key isolation** (one DEK per customer environment).
14. **Dry-run / preview** before first sync and before any outbound write.
15. **Connector health registry** — version each connector, track which instance runs which version, so
    an API-breakage fix rolls out + audits across instances. (Critical for the from-scratch problem.)

## B. Claims table

| # | Claim | Tier | Source/marker (retrieved 2026-06-24) | Settling gate |
|---|-------|------|--------------------------------------|---------------|
| 1a | Baseline for storing 3rd-party tokens/keys = app-level AES-256-GCM, DEK-per-secret/tenant, KEK in a KMS separate from app+DB (envelope encryption). | BLOCK | cloud.google.com/kms envelope-encryption; Google OAuth2 best-practices | KEK must NOT live in app DB; 1 DEK/customer env. |
| 1b | Per-tenant DEK is the recommended isolation pattern; matches single-tenant. | WARN | scalekit.com OAuth-token-security | Aligns with one-instance-per-customer. |
| 1c | Supabase Vault valid (libsodium AEAD); pgsodium TCE/Server-KM pending deprecation — target Vault interface, not raw pgsodium. | WARN | supabase.com/docs vault + pgsodium | If Supabase chosen, use Vault, not pgsodium TCE. |
| 1d | HashiCorp Vault equally valid for the KEK/secret tier. | WARN | [unverified — training knowledge] | Any KMS keeping KEK off app DB satisfies 1a. |
| 2a | OAuth 2.0 Authorization Code grant is the correct flow (confidential server-side client; issues access+refresh). | BLOCK | RFC 6749 §4.1/§1.5 | App is a confidential client. |
| 2b | Apply PKCE even for confidential clients; follow OAuth 2.1 (6749+7636+9700). | BLOCK | oauth.net/2.1; Auth0 authcode+PKCE | Per-connector auth descriptor records PKCE yes/no (older providers need plain authcode). |
| 2c | Revocation is a separate spec (RFC 7009); refresh-failure → re-consent UX required. | WARN | RFC 6749 (revocation out of scope) | Implement refresh + reconnect on invalid_grant. |
| 3a | Reverse-ETL idempotent writes = upsert + dedupe/primary key. | BLOCK | hightouch.com; datagibberish idempotent-reverse-etl | Outbound path defines an upsert key per destination object. |
| 3b | Incremental sync (cursor/CDC) is the norm; full-refresh doesn't scale. | WARN | hightouch.com; nango sync engine | Per-stream cursor (updated_at/sequence). |
| 4 | **Building+maintaining from-scratch connectors is a recurring high burden — why Fivetran/Airbyte exist (Fivetran: 600+ eng / 700+ connectors).** Estimate (Medium): initial non-trivial OAuth connector ≈ days-to-2wk; ongoing each source breaks 1–4×/yr × #sources × #instances. | **BLOCK — red-team's primary risk** | fivetran.com vs-airbyte; kestra.io why-ingestion-never-solved | **Plan must answer with: declarative connector SDK + versioned connector registry + explicit maintenance budget.** No hand-wave. |
| 5a | Per-customer Claude-built dashboards are sound ONLY backed by a metrics/semantic layer; else degrades to hand-coded SQL per customer. | WARN | cube.dev headless-bi; evidence-dev | Choose a semantic-layer posture before freehand SQL. |
| 5b | Semantic layer buys: single source of metric truth, change-in-one-place, consistent numbers, access-control + caching. | WARN | cube.dev; venturebeat headless-vs-native | Pick Cube headless vs dbt+Lightdash vs Evidence. |
| 5c | BI-as-code (Evidence: SQL+MD in Git) fits Claude-authoring better than a GUI builder (versioned, diff-able). | WARN | evidence-dev | Decide code-as-dashboard vs semantic-layer+GUI. |

## Competing hypothesis the panels must weigh
"From-scratch is a fatal mistake; use a unified-API/iPaaS vendor and spend saved effort on dashboards."
**Why the plan still proceeds from-scratch (Matt's pinned call):** single-tenant = a *small curated*
source set per instance (not 700); the declarative-SDK pattern makes the curated set cheap; "core
connections live in the app" is an explicit product differentiator. **But** the plan MUST budget
connector maintenance explicitly and adopt the SDK + versioned-registry mitigations.

## Gaps / blind spots
- No authoritative per-connector $ figure found — B.4 estimate is reasoned (Medium), not cited.
- RFC 7009 + HashiCorp Vault asserted from training knowledge, not fetched this run.
- Granola / long-tail source API maturity unassessed — not all sources equally stable to build against.
