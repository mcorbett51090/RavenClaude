# Finance ELT connector facts — auth, limits, and the rotating-refresh-token failure mode

> **Tier:** BLOCK. These are the facts an implementer must not violate when wiring a live GL/accounting-system extractor that feeds the canonical staging seam ([`../skills/finance-elt-staging/SKILL.md`](../skills/finance-elt-staging/SKILL.md)). Getting one wrong doesn't produce a wrong *number* — it silently **loses access to the source mid-close** (a rotated refresh token dropped on a crash) or **gets the integration rate-limited/blocked**. That is why they gate.
>
> **Last reviewed:** 2026-07-06 · **Confidence: these values are TRAINING KNOWLEDGE, NOT verified this session** (no live browser check was available in this session). Every numeric token lifetime / rate limit below is therefore marked `[unverified — settling gate]` and MUST be browser-verified against the cited primary doc before it gates a live build. Vendors change these; treat the *shape* of each fact as durable and the *number* as needing confirmation.

## Why this doc exists (the honest framing)

The staging transform (`tb_stage.py`) is deterministic and credential-free. **Extraction is not.** Pulling a trial balance from QBO / NetSuite / Xero / Sage Intacct means OAuth2, tokens that expire in minutes-to-hours, refresh tokens that expire in weeks-to-months (and for two of the four **rotate on every use**), per-tenant rate limits, and paginated report/query APIs. The single highest-consequence failure in this tier is a **dropped rotating refresh token** — it is unrecoverable without a human re-auth, and it tends to happen at the worst time (a crash mid-refresh). The mitigation is at the bottom; read it before you write a token to disk.

This is scaffolding guidance, not a certified integration. It is decision-support, not an accounting/audit/tax opinion (see [`../CLAUDE.md`](../CLAUDE.md) §3).

---

## Per-source blocking facts

### QuickBooks Online (QBO)

| Fact | Value `[confidence]` | Source to verify |
|---|---|---|
| Auth | OAuth2 **authorization-code** flow | Intuit developer docs — OAuth 2.0 |
| Access token lifetime | **~1 hour (3600 s)** `[unverified — settling gate]` | Intuit "Refresh tokens" doc |
| Refresh token lifetime | **~100 days**, and it **ROTATES** — a new refresh token is returned on (nearly) every refresh; the old one is invalidated `[unverified — settling gate]` | Intuit "Refresh tokens" doc |
| Rate limit | **500 requests/min per `realmId`** (plus a lower concurrent cap) `[unverified — settling gate]` | Intuit "Service limits" / throttling doc |
| TB data | Reports API — `TrialBalance` report | Intuit Accounting API — Reports |
| **Migration gate** | Intuit is migrating the **Reports API**; a deadline around **~Aug 31, 2026** is on the roadmap. **VERSION THE PARSER.** Dated gate: **after 2026-08-15, build against the NEW Reports API only** and treat the legacy shape as read-only/deprecated. `[unverified — settling gate]` | Intuit changelog / Reports API migration notice |

`realmId` is the QBO company id — it is the per-tenant key for both routing and the rate limit.

### NetSuite

| Fact | Value `[confidence]` | Source to verify |
|---|---|---|
| Auth | **OAuth2** (M2M client-credentials or auth-code). **TBA (Token-Based Auth) is being retired for NEW setups — no new TBA integrations from ~2027.1.** Prefer OAuth2 for anything new. `[unverified — settling gate]` | Oracle NetSuite release notes (2027.1) |
| Concurrency | **Account-level POOLED limit — Shared 5 / Tier 1 15 / Tier 2 & Ultimate 20 concurrent (+10 per SuiteCloud Plus license)**, shared across SOAP + REST + RESTlet — NOT the ~1 this row previously stated (corrected v0.17.1). Discover the tier at runtime; design for the pool with backoff, not a hardcoded number. `[doc-sourced 2026-07-06 — Oracle "NetSuite Concurrency Limits" + SuiteCloud governance cheat sheet; not live-observed — re-confirm for the account's actual tier before go-live]` | Oracle "NetSuite Concurrency Limits" |
| TB / query | **SuiteQL** (REST) — paginated, **~1000 rows/page** `[unverified — settling gate]` | NetSuite SuiteQL / REST records docs |
| Account id | `netsuite_account_id` (e.g. `TSTDRV…` for sandboxes) is the per-tenant key + subdomain | NetSuite account setup |

### Sage Intacct

| Fact | Value `[confidence]` | Source to verify |
|---|---|---|
| Auth / API (classic) | **XML Web Services** (session-based). `readByQuery` returns a paged result — **cap ~2,000 records/call**, page the rest via `resultId`/`readMore`. `[unverified — settling gate]` | Sage Intacct Web Services developer docs |
| Auth / API (newer) | **REST API with OAuth2** is the newer surface — prefer it for new builds where available, but the classic XML WS still covers more objects. `[unverified — settling gate]` | Sage Intacct REST API docs |
| **Connector gate** | **NO first-party Airbyte source for Sage Intacct.** Do **not** assume an off-the-shelf open-source connector exists. Use **Fivetran** (managed) or a **custom XML extractor** against Web Services. `[unverified — settling gate]` | Airbyte connector catalog (confirm absence) |

### Xero

| Fact | Value `[confidence]` | Source to verify |
|---|---|---|
| Auth | OAuth2 **+ PKCE** (authorization-code with PKCE) | Xero OAuth 2.0 docs |
| Access token lifetime | **~30 minutes** `[unverified — settling gate]` | Xero "OAuth2 token expiry" |
| Refresh token lifetime | **~60 days**, and it **ROTATES** on every refresh (new refresh token returned each time; persist it or lose access) `[unverified — settling gate]` | Xero "Refresh access tokens" |
| Rate limits | **5 concurrent**, **60 calls/min**, **5,000 calls/day — per tenant** `[unverified — settling gate]` | Xero "API rate limits" |
| TB data | `/Reports/TrialBalance`; note **`/Journals` is READ-ONLY** (use it for GL-detail pulls, not writes) | Xero Accounting API |
| Tenant | `xero_tenant_id` is the per-organization key (from the connections endpoint) | Xero connections |

---

## THE failure mode: a dropped ROTATING refresh token (QBO + Xero)

**Setup.** For QBO and Xero, the refresh token is **single-use-ish**: each successful token refresh returns a **new** refresh token and invalidates the previous one. If your process obtains the new access+refresh pair, **uses the access token**, and then **crashes or fails to persist the new refresh token**, you are locked out — the old refresh token is already dead and you never saved the new one. Recovery requires a **human re-auth** (interactive OAuth consent). Mid-close, that is an outage.

**Mitigation (all four are required — this is the blocking part):**

1. **Persist the new refresh token ATOMICALLY *before* using the new access token.** Write the new token pair to a temp file and `os.replace()` it into place (same atomic pattern `tb_stage.py`/`close_state.py` use for their outputs) **first**; only after the rename succeeds do you make the first API call with the new access token. Order matters: persist → then use. Never use-then-persist.
2. **Per-entity file lock around the refresh.** Two concurrent processes refreshing the same entity's token will each rotate it and invalidate the other's — a self-inflicted lockout. Hold an exclusive lock (per-entity token-store path) for the read-refresh-write critical section so only one refresh is in flight per entity at a time.
3. **Alert on `invalid_grant`.** An `invalid_grant` on refresh means the refresh token is dead (expired past its ~60/100-day window, revoked, or rotated-and-lost). This is **not** retryable with backoff — it needs the re-auth runbook. Fire an alert immediately (do not silently retry forever).
4. **Re-auth runbook.** Document the interactive re-consent path per source (authorize URL → consent → capture the new auth code → exchange for a fresh token pair → persist atomically) so an on-call controller can restore access without an engineer. Store which env-var NAMES hold the client credentials (never the values) so the runbook is followable from the config alone — see [`../templates/connector-config.template.json`](../templates/connector-config.template.json).

**NetSuite / Intacct note.** NetSuite OAuth2 and Intacct sessions don't rotate a refresh token the same way, but the same *discipline* (atomic persist, per-entity lock, alert on auth failure, documented re-auth) is cheap insurance — apply it uniformly.

---

## Settling gates — verify before these gate a live build

| # | Claim needing confirmation | How to settle |
|---|---|---|
| SG-1 | QBO Reports API migration deadline (**~Aug 31 2026**) + the **2026-08-15 build-against-new-only** cutover | Browser-verify Intuit's Reports API migration notice / changelog; pin the parser version to the confirmed date |
| SG-2 | QBO token lifetimes (access ~1h, refresh ~100d, rotates) and **500 req/min/realmId** | Intuit "Refresh tokens" + "Service limits" docs |
| SG-3 | Xero lifetimes (access ~30m, refresh ~60d, rotates) + **5 concurrent / 60-min / 5000-day** per tenant | Xero OAuth2 + rate-limit docs |
| SG-4 | NetSuite **no new TBA from 2027.1**, POOLED concurrency **5 / 15 / 20 (+10 per SuiteCloud Plus)** (corrected v0.17.1 — not ~1), SuiteQL **~1000 rows/page** | Oracle NetSuite 2027.1 release notes + SuiteCloud concurrency governance |
| SG-5 | Intacct XML `readByQuery` **~2,000/call** cap; **no first-party Airbyte source** | Sage Intacct Web Services docs + Airbyte connector catalog |

**Discipline:** until a row is browser-verified, treat its number as `[unverified — settling gate]` and do not let it gate an irreversible build decision (a parser cutover, a rate-limiter constant). The *shapes* (rotation exists; there IS a migration; concurrency IS governed) are the durable facts; the numbers drift.

---

## Sources (all to be browser-verified — cited from training knowledge)

- Intuit QuickBooks Online — OAuth 2.0, Refresh tokens, Service limits, Reports API migration changelog
- Oracle NetSuite — 2027.1 release notes (TBA retirement), SuiteQL/REST records, concurrency governance
- Sage Intacct — Web Services (readByQuery) developer docs, REST API docs; Airbyte connector catalog (to confirm the absence of a first-party source)
- Xero — OAuth 2.0 (PKCE), token expiry, refresh-token rotation, API rate limits, Accounting API (`/Journals` read-only)
