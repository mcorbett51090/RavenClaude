# Finance ELT connector facts — auth, limits, and the rotating-refresh-token failure mode

> **Tier:** BLOCK. These are the facts an implementer must not violate when wiring a live GL/accounting-system extractor that feeds the canonical staging seam ([`../skills/finance-elt-staging/SKILL.md`](../skills/finance-elt-staging/SKILL.md)). Getting one wrong doesn't produce a wrong *number* — it silently **loses access to the source mid-close** (a rotated refresh token dropped on a crash) or **gets the integration rate-limited/blocked**. That is why they gate.
>
> **Last reviewed:** 2026-07-07 · **Confidence: mixed.** The QBO / Sage Intacct / Xero sections below are TRAINING KNOWLEDGE, NOT verified this session (no live browser check was available for those on 2026-07-06). The **NetSuite section was refreshed 2026-07-07 against Oracle primary docs** (release notes, SuiteQL REST reference, role-setup docs) retrieved this session — its *shape* facts (M2M primary / TBA cutoff / SuiteQL endpoint contract / BS-cumulative-vs-IS-period) carry higher confidence than the other three sources, but its *numbers* (exact end-of-support dates, the 100,000-row cap) are still marked `[unverified — settling gate]` pending a second, independent confirmation. Every numeric token lifetime / rate limit below MUST be browser-verified against the cited primary doc before it gates a live build. Vendors change these; treat the *shape* of each fact as durable and the *number* as needing confirmation.

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
| **Auth — PRIMARY** | **OAuth 2.0 machine-to-machine (M2M): client-credentials grant + an X.509-cert-signed JWT client assertion.** There is **NO refresh token** in this flow — a fresh access token is minted by re-signing a short-lived assertion with the private key whose public certificate is registered in NetSuite (the rotating-refresh-token disciplines elsewhere in this doc do not apply here; the M2M failure mode is private-key custody + assertion `exp`/clock-skew, not a dropped refresh token). `[unverified — settling gate]` | Oracle NetSuite — "OAuth 2.0 Machine to Machine Authentication" setup docs |
| **Auth — FALLBACK (time-boxed)** | **TBA (Token-Based Auth, OAuth 1.0a)** — usable for existing integrations but **CANNOT create new integrations from NetSuite release 2027.1**; existing TBA integrations are supported to roughly **2028.1**. **Migration note:** any new NetSuite build must default to OAuth2 M2M; TBA is only acceptable as a documented, time-boxed bridge with a tracked migration date. `[unverified — settling gate]` | Oracle NetSuite release notes — "Preparing for Token-Based Authentication End of Support" (2027.1) |
| SuiteQL — endpoint | `POST /services/rest/query/v1/suiteql`. The request **MUST** send header `Prefer: transient`; the query text goes in the request **body** (`q`), not the URL. `[unverified — settling gate]` | Oracle NetSuite — SuiteQL REST API reference |
| SuiteQL — paging | `limit` / `offset` query parameters page the result; there is a **hard cap of 100,000 results per query** — a query must be scoped (period/subsidiary) rather than paged past that ceiling. `[unverified — settling gate]` | Oracle NetSuite — SuiteQL REST API reference |
| **Trial-balance shape — BLOCKING** | A trial balance built via `SUM(TransactionAccountingLine.amount)` joined to `Account` (`posting = 'T'`) must be summed **CUMULATIVE-from-inception for balance-sheet account types** and **PERIOD-scoped for income-statement account types**. A naive period-only `SUM` **silently understates every BS account while the TB still foots to zero** — footing to zero is necessary, not sufficient. Always expose `subsidiary` + `accountingbook` + `currency` on the query; omitting `subsidiary` silently pulls a consolidated (wrong-grain) result. `[unverified — settling gate]` | Oracle NetSuite — Account record `accttype` field reference + SuiteQL transaction-accounting-line schema |
| Minimum role | **REST Web Services** + **Log in using Access Tokens** + **SuiteAnalytics Workbook**, plus **Lists → Accounts (View)** and the target **subsidiary** assignment. Missing SuiteAnalytics Workbook is a common cause of an otherwise-valid-looking SuiteQL call returning an empty/denied result. `[unverified — settling gate]` | Oracle NetSuite — permissions reference for REST Web Services / SuiteQL |
| Concurrency | **Governed at the account level**, not a fixed small default — a **serial** trial-balance pull (one query at a time, paged) is a non-issue under NetSuite's governance model; design for serial extraction + backoff, not parallel fan-out. **Supersedes** an earlier, less-precise "~1 concurrent request by default" characterization of this same fact. `[unverified — settling gate]` | Oracle NetSuite — "Web Services & RESTlet concurrency governance" |
| Native close (don't rebuild) | NetSuite ships an **18-step Period Close Checklist** (period lock, FX revaluation, consolidated-rate calc, intercompany elimination + adjustments, revenue-rec + reclass via Advanced Revenue Management, period-end journals, gapless GL audit numbering) plus, as of **2026 R1**, **Intelligent Close Manager** (an AI task board layered on the checklist). A NetSuite connector's job is to feed a correct TB into a *governance layer on top of this*, not to reimplement it. `[unverified — settling gate]` | Oracle NetSuite — Period Close Checklist + Intelligent Close Manager release documentation |
| Account id | `netsuite_account_id` (e.g. `TSTDRV…` for sandboxes) is the per-tenant key + subdomain | NetSuite account setup |

Full catalog of the market's NetSuite-integration landscape (10 tools + 10 SuiteApps + the 12 gold-standard criteria) lives in [`netsuite-integration-landscape.md`](netsuite-integration-landscape.md). The reference-implementation build against these facts is [`../skills/netsuite-close/SKILL.md`](../skills/netsuite-close/SKILL.md) (engines: `scripts/connectors/oauth_client.py`'s `netsuite_m2m` flow, `scripts/connectors/suiteql.py`, `scripts/connectors/netsuite_signer.py`).

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

**NetSuite / Intacct note.** NetSuite's OAuth2 **auth-code** flow and Intacct sessions don't rotate a refresh token the same way QBO/Xero do, but the same *discipline* (atomic persist, per-entity lock, alert on auth failure, documented re-auth) is cheap insurance — apply it uniformly. **NetSuite's primary M2M flow is a different shape entirely: there is no refresh token to persist at all** — each access-token mint re-signs a short-lived JWT assertion with a private key. The atomic-persist/lock disciplines still apply to the **minted access token** (so two racing processes don't each mint and neither observes the other), but the actual custody risk moves to the **private signing key**: keep it off this process's argv, on a 0600 file, and treat cert re-issuance (not token refresh) as the event needing an alert + runbook. See [`../skills/netsuite-close/SKILL.md`](../skills/netsuite-close/SKILL.md) for the M2M-specific runbook.

---

## Settling gates — verify before these gate a live build

| # | Claim needing confirmation | How to settle |
|---|---|---|
| SG-1 | QBO Reports API migration deadline (**~Aug 31 2026**) + the **2026-08-15 build-against-new-only** cutover | Browser-verify Intuit's Reports API migration notice / changelog; pin the parser version to the confirmed date |
| SG-2 | QBO token lifetimes (access ~1h, refresh ~100d, rotates) and **500 req/min/realmId** | Intuit "Refresh tokens" + "Service limits" docs |
| SG-3 | Xero lifetimes (access ~30m, refresh ~60d, rotates) + **5 concurrent / 60-min / 5000-day** per tenant | Xero OAuth2 + rate-limit docs |
| SG-4a | NetSuite TBA **no new integrations from 2027.1**, existing support to **~2028.1** | Oracle NetSuite "Preparing for TBA End of Support" release notes |
| SG-4b | NetSuite OAuth2 M2M — client-credentials + X.509-cert JWT assertion shape, no refresh token | Oracle NetSuite "OAuth 2.0 Machine to Machine Authentication" docs |
| SG-4c | SuiteQL endpoint contract — `Prefer: transient` required, `limit`/`offset` paging, **100,000-result hard cap** | Oracle NetSuite SuiteQL REST API reference |
| SG-4d | SuiteQL BS-cumulative / IS-period trial-balance shape; account-level (not fixed ~1) concurrency governance | Oracle NetSuite Account `accttype` reference + SuiteCloud concurrency governance docs |
| SG-5 | Intacct XML `readByQuery` **~2,000/call** cap; **no first-party Airbyte source** | Sage Intacct Web Services docs + Airbyte connector catalog |

**Discipline:** until a row is browser-verified, treat its number as `[unverified — settling gate]` and do not let it gate an irreversible build decision (a parser cutover, a rate-limiter constant). The *shapes* (rotation exists; there IS a migration; concurrency IS governed) are the durable facts; the numbers drift.

---

## Sources (all to be browser-verified — cited from training knowledge unless marked "retrieved this session")

- Intuit QuickBooks Online — OAuth 2.0, Refresh tokens, Service limits, Reports API migration changelog
- Oracle NetSuite — **retrieved this session (2026-07-07):** "Preparing for TBA End of Support" release notes (2027.1 / ~2028.1), "OAuth 2.0 Machine to Machine Authentication" setup docs, SuiteQL REST API reference, Account `accttype` field reference, permissions reference for REST Web Services/SuiteAnalytics Workbook, Period Close Checklist + Intelligent Close Manager release documentation, SuiteCloud concurrency governance
- Sage Intacct — Web Services (readByQuery) developer docs, REST API docs; Airbyte connector catalog (to confirm the absence of a first-party source)
- Xero — OAuth 2.0 (PKCE), token expiry, refresh-token rotation, API rate limits, Accounting API (`/Journals` read-only)
