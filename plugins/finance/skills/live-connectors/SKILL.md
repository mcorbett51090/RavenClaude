---
name: live-connectors
description: "Wire a live GL/accounting-system OAuth2 extractor (QuickBooks Online / NetSuite / Sage Intacct / Xero) that feeds the canonical trial-balance staging seam, using the reference-implementation token client in scripts/connectors/ — atomic persist-then-use rotating refresh, per-entity lock, error-cause routing (401 refresh / 429 backoff / invalid_grant re-auth), Xero 30-min grace — plus drill-through GL lineage that feeds statement_engine --gl-detail unchanged. Reference impl + record/replay harness; NOT live-verified. Used by `controller`."
---

# Skill: live-connectors

**Purpose:** turn "a controller has OAuth access to their GL" into "a raw export lands in the
canonical staging seam, with drill-through provenance" — safely. The single highest-consequence
failure in this tier is a **dropped rotating refresh token** (QBO + Xero): lose it on a crash and
you are locked out mid-close until a human re-auths. This skill's reference implementation encodes
the four disciplines that prevent that, and a **record/replay harness** so you can develop and test
the whole path with **zero live credentials and zero network**.

> **HONEST BOUNDARY — read first.** Everything here is a **reference implementation + offline
> harness**, NOT a live-verified, certified connector. No live credentials are used; no live socket
> is ever opened by this code. **Every provider "fact" in this skill and in
> [`../../knowledge/finance-elt-connector-facts.md`](../../knowledge/finance-elt-connector-facts.md) —
> token lifetimes, rate limits, the QBO/Xero rotating-refresh behavior, the Xero 30-minute grace
> window, error-code semantics — is `doc-sourced, not live-observed; re-confirm before go-live`.**
> It is **training knowledge**, **settling-gated**: browser-verify each against its primary provider
> doc before it gates a live build; do not treat any of it as observed from a running integration.
> Live wiring — the real IdP, the real client credentials, the real token/report endpoints,
> and the real warehouse to land into — is **the consumer's step**. Outputs are decision-support
> scaffolding, not an accounting/audit/tax opinion and not a competitive claim of a working
> integration (see [`../../CLAUDE.md`](../../CLAUDE.md) §3).

## What's in the box

| File | Role |
|---|---|
| [`../../scripts/connectors/oauth_client.py`](../../scripts/connectors/oauth_client.py) | Token-lifecycle client. Providers-as-data; **atomic persist-then-use** rotating refresh; **per-entity `fcntl` lock**; **error-cause routing**; **Xero 30-min grace**. **security_review target — token handling.** |
| [`../../scripts/connectors/replay_transport.py`](../../scripts/connectors/replay_transport.py) | Stdlib **record/replay** transport. Serves recorded synthetic fixtures; **fails loudly on a missing fixture**; **never opens a socket**. |
| [`../../scripts/connectors/adapters/`](../../scripts/connectors/adapters/) | Per-provider adapters (QBO / NetSuite / Sage Intacct / Xero). Each emits a **raw export file** that `tb_stage.py` already normalizes — staging is **not** re-implemented. |
| [`../../scripts/connectors/gl_lineage.py`](../../scripts/connectors/gl_lineage.py) | Drill-through lineage: first 6 columns **byte-identical** to `statement_engine --gl-detail`, plus `source_system,source_type,source_id,source_doc_url`. Feeds the engine **unchanged**. |
| [`../../scripts/connectors/fixtures/`](../../scripts/connectors/fixtures/) | Synthetic, obviously-fake recorded fixtures (fake realm/tenant ids; fake token values) per provider. |
| [`../../scripts/test_connectors.py`](../../scripts/test_connectors.py) | 31-test acceptance suite (all the invariants below). |

## The rotating-refresh failure mode and the four disciplines

For **QBO and Xero** the refresh token **rotates**: a successful refresh returns a NEW refresh
token and kills the old one. The client encodes all four required mitigations:

1. **Persist-then-use, atomically.** The new token pair is written to a temp file and
   `os.replace()`d into the store **before** the new access token is ever used. Consequence:
   a crash **after** the rename leaves the NEW token durable; a crash **during** the write leaves
   the OLD token fully intact. There is never a half-written store and never a silent lockout.
2. **Per-entity exclusive lock.** An `fcntl.flock` on a per-entity lockfile wraps the
   read-refresh-write critical section; a recheck-under-lock collapses two racing refreshes to
   **one** rotation (two processes can't each rotate and invalidate the other).
3. **Error-cause routing — the cause selects the fix, and they are not interchangeable.**
   `401` (expired access) → refresh + retry the same route; `429` → backoff honoring `Retry-After`;
   `400 invalid_grant` (dead refresh) → **REAUTH_REQUIRED**, non-retryable, **fire the alert hook**,
   never backoff. Guessing the cause picks the wrong fix.
4. **Xero 30-min grace.** A refresh whose response is lost leaves you unsure whether the server
   rotated; within the provider grace window the client retries with the **existing** refresh token
   rather than assuming a rotation it never observed.

## Consumer OAuth wiring runbook

1. **Copy the config template per entity** — [`../../templates/connector-config.template.json`](../../templates/connector-config.template.json).
   Set `source_system`, the one matching `source_ids.*`, the `token_store_path`, and — critically —
   set `rotating_refresh_token: true` for **QBO and Xero**.
2. **Provision credentials as ENV-VAR NAMES only.** The template stores `client_id_env`,
   `client_secret_env`, `refresh_token_env` — the **names** of environment variables, never the
   values. Populate the actual secrets in your runtime's secret manager. **Never commit a token
   value or a `.token.json` store.**
3. **First-time auth (interactive).** Run the provider's authorization-code flow (Xero: **+ PKCE**)
   to obtain the first access+refresh pair, and write it to `token_store_path` (0600). This is the
   one step that needs a human/browser; automate the rest.
4. **Implement the live transport.** `oauth_client.OAuthClient` takes an injected `transport` with a
   `token_request(url, data) -> (status, body, headers)` seam. For development/tests use
   `ReplayTransport`; for production supply a real HTTPS transport (e.g. stdlib `urllib`/`http.client`
   or your HTTP library) that calls the provider `token_url`. **The token-lifecycle disciplines live
   in `OAuthClient`, so the live transport stays thin.**
5. **Wire the alert hook + re-auth runbook.** Pass `alert_hook=` so an `invalid_grant` pages an
   on-call controller. Document the interactive re-consent path per source (authorize URL → consent →
   capture code → exchange → persist atomically) so access is restorable without an engineer.
6. **Extract → adapter → stage.** Pull the TB/report, hand it to the provider adapter to emit a raw
   export file, then normalize with `tb_stage.py stage` using that provider's column-map. The staged
   CSV flows straight into `statement_engine.py --tb`.
7. **(Optional) drill-through lineage.** Build a lineage file with `gl_lineage.py build` (a
   `--gl-detail` file + a source-doc sidecar) and pass it to `statement_engine.py --gl-detail`; the
   badge lifts to `GL-detail-traced` and the source-doc keys ride into the reasoning trail.

```shell
# Offline (replay) end-to-end, zero credentials:
python3 scripts/connectors/gl_lineage.py build \
  --gl-detail skills/produce-gaap-statements/examples/gl-detail-2026-06.csv \
  --source-system qbo \
  --docs scripts/connectors/fixtures/lineage/source-docs.csv \
  --out /tmp/lineage.csv
python3 scripts/statement_engine.py --entity <entity.json> --coa <coa.csv> \
  --tb <staging.csv> --gl-detail /tmp/lineage.csv   # badge -> GL-detail-traced
```

## Verify before you trust the numbers

Run the acceptance suite: `python3 scripts/test_connectors.py` (31 tests, stdlib-only). It proves
the persist-then-use ordering, crash-safety both ways, the one-rotation lock, the invalid_grant
re-auth path, the three-way error routing, the Xero grace retry, the replay transport's loud
missing-fixture failure + no-socket guarantee, and the lineage byte-identity + badge lift. Before a
**live** build, also browser-verify the settling-gated provider facts in
[`../../knowledge/finance-elt-connector-facts.md`](../../knowledge/finance-elt-connector-facts.md).

## What this is not

Not a certified or live-verified connector; not an accounting/audit/tax opinion. The harness proves
the **token-handling and lineage disciplines** against synthetic fixtures — it does **not** prove the
source GL is correct, reconciled, or complete. A clean extract is a necessary, not sufficient,
condition for a trustworthy close: reconciliation ([`../reconciliation-summary/SKILL.md`](../reconciliation-summary/SKILL.md) /
[`../reconciliation-automatch/SKILL.md`](../reconciliation-automatch/SKILL.md)) and the governed
review→approve→lock spine ([`../close-approval-workflow/SKILL.md`](../close-approval-workflow/SKILL.md))
still apply.
