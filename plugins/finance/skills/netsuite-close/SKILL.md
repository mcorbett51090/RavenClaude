---
name: netsuite-close
description: "Wire NetSuite as a controller-autopilot source: OAuth2 M2M (cert-signed JWT, no refresh token) or time-boxed TBA fallback, a SuiteQL BS-cumulative/IS-period trial balance, tie-out, changed-after-sign-off drift check. Reference impl. Used by `controller`."
---

# Skill: netsuite-close

**Purpose:** turn "a controller has a NetSuite admin who can grant access" into a governed close package, in two phases — a **one-time, admin-assisted setup** (measured in days, because it needs real change control) and a **recurring close-day pull** (once wired, can approach a day for a layperson). This skill is the NetSuite-specific front door onto the generic `live-connectors` + `controller-autopilot` machinery: it wires NetSuite's OAuth2 M2M auth and SuiteQL trial-balance query correctly, then hands off to the same `run-controller-cycle` → `close_state.py` spine every other source uses.

> **HONEST BOUNDARY — read first.** This is a **reference implementation + offline harness**, NOT a live-verified or certified NetSuite connector. No live credentials are used by the shipped code; no live socket is ever opened by it. Every NetSuite fact cited here — the M2M shape, the SuiteQL endpoint contract, the minimum role, the BS-cumulative/IS-period rule — was retrieved from Oracle primary docs on 2026-07-07 and is still `[unverified — settling gate]` per [`../../knowledge/finance-elt-connector-facts.md`](../../knowledge/finance-elt-connector-facts.md); re-confirm against a sandbox before it gates a live build. **Live wiring — the real NetSuite account, the real certificate, the real integration record, a real warehouse to land into — is the consumer's step.** The value-add here is an **ERP-neutral tamper-evident control ledger** with NetSuite wired as the first source system — not a claim that NetSuite lacks governance of its own (it doesn't; see [`../../knowledge/netsuite-integration-landscape.md`](../../knowledge/netsuite-integration-landscape.md) for what NetSuite already ships natively). Outputs are decision-support scaffolding, not an accounting/audit/tax opinion (see [`../../CLAUDE.md`](../../CLAUDE.md) §3).

## What's in the box (verified present in this checkout, 2026-07-07)

| File | Role |
|---|---|
| [`../../scripts/connectors/oauth_client.py`](../../scripts/connectors/oauth_client.py) | Token client. Adds the `netsuite_m2m` provider: client-credentials + a cert-signed JWT assertion via an **injected signer seam** (`build_jwt_assertion`). Falls back to plain OAuth2 `netsuite` (TBA-era auth-code) for the time-boxed migration path. |
| [`../../scripts/connectors/suiteql.py`](../../scripts/connectors/suiteql.py) | `build_tb_query` (BS-cumulative / IS-period trial balance), governed serial `pull` (100,000-result hard cap, loud on breach), `tie_out` (net-to-zero assertion). |
| [`../../scripts/connectors/netsuite_signer.py`](../../scripts/connectors/netsuite_signer.py) | Reference signer for the M2M JWT assertion — optional PyJWT[crypto], key read from a 0600 **file** (never argv), `--self-test` for an offline sign/verify round-trip. |
| [`../../scripts/connectors/adapters/netsuite.py`](../../scripts/connectors/adapters/netsuite.py) | `export_via_suiteql` — runs the TB query, ties it out, emits the raw-export shape `tb_stage.py` already normalizes. |
| [`../../scripts/close_state.py`](../../scripts/close_state.py) | `submit(..., source_tb_sha256=...)` + `verify_source()` — pins the pulled TB's hash at sign-off and flags a **changed-after-sign-off** drift if a later NetSuite re-pull disagrees. |

The higher-level front-door scripts (`netsuite_coa_draft.py`, `netsuite_doctor.py`, `netsuite_lineage.py`, `netsuite_connect.py`) are present in `scripts/connectors/` alongside the table above; run any with `--help` for its flags. The whole chain runs offline with `--replay` (zero live credentials) before your first live pull.

---

## BEFORE CLOSE DAY (one-time, admin-assisted — budget days, not hours)

This phase needs a **NetSuite ADMIN** and your org's change-control process. Do not attempt to compress it into close day — cert issuance and role provisioning are the parts that take real calendar time, not engineering time.

1. **Enable the OAuth 2.0 feature.** In NetSuite: *Setup → Company → Enable Features → SuiteCloud* → enable OAuth 2.0. `[unverified — confirm exact menu path against your NetSuite version]`

2. **Create an Integration record → get the `client_id`.** *Setup → Integration → Manage Integrations → New*. Select **Token-Based Authentication: OFF**, **OAuth 2.0: ON**, and machine-to-machine (client-credentials) if your NetSuite version exposes that toggle explicitly. Save and copy the generated `client_id` — you'll need it in the config (below). `[unverified — confirm exact field labels against your NetSuite version]`

3. **Generate the certificate — run this in YOUR shell, not this agent's.** The private key must never leave your machine or land on this process's command line. Run:

   ```shell
   openssl req -x509 -newkey rsa:2048 -sha256 -nodes -days 730 \
       -keyout netsuite-<entity>.key -out netsuite-<entity>.cert.pem
   ```

   This produces a private key (`netsuite-<entity>.key` — keep this **0600**, off-box, never in version control) and a public certificate (`netsuite-<entity>.cert.pem` — this is the one you upload). Source: [`netsuite_signer.py`](../../scripts/connectors/netsuite_signer.py) docstring, which documents this exact command for the same reason — key custody stays off this process's argv.

4. **Upload the certificate.** *Setup → Integration → Manage Integrations → OAuth 2.0 → Certificate* → upload `netsuite-<entity>.cert.pem`. Note the **certificate id** NetSuite assigns — this becomes the JWT `kid` (key id) in your config.

5. **Assign the read-only role.** The role needs, at minimum: **REST Web Services**, **Log in using Access Tokens**, **SuiteAnalytics Workbook**, **Lists → Accounts (View)**, and the target **subsidiary** assignment. A role missing SuiteAnalytics Workbook is the most common cause of an otherwise-valid SuiteQL call returning an empty or denied result.

6. **Fill in the config.** Copy [`../../templates/connector-config.template.json`](../../templates/connector-config.template.json)'s NetSuite M2M variant block and fill in `netsuite_account_id`, `client_id_env` (the env-var **name**, never the value), `cert_id`, `private_key_path` (the 0600 file from step 3), `scope`, and `subsidiary_id`. Credentials are referenced by env-var name only — see §3 #10 of [`../../CLAUDE.md`](../../CLAUDE.md).

**TBA fallback (time-boxed — read before choosing it).** NetSuite's older Token-Based Authentication (OAuth 1.0a) still works for **existing** integrations, but **cannot create new integrations from release 2027.1**, with existing TBA support running to roughly **2028.1** `[unverified — settling gate]`. If you're standing up a *new* NetSuite integration today, default to M2M (steps 1–6 above); only use TBA if you're extending an integration that predates this cutoff, and track its migration date explicitly — don't let TBA become the permanent path by default.

---

## CLOSE DAY (recurring — can approach a day once wired)

1. **First run only: draft the chart-of-accounts mapping.** `python3 scripts/connectors/netsuite_coa_draft.py` (run with `--help` for its flags). This produces a starting `coa-mapping.csv` from NetSuite's account list, which you then review and correct — the COA mapping is the reusable-per-entity asset (see [`../author-coa-mapping/SKILL.md`](../author-coa-mapping/SKILL.md)); you author it once per entity, not every close.

2. **Pull the trial balance.** `python3 scripts/connectors/netsuite_connect.py` — the one-command front door that mints the M2M access token, runs the BS-cumulative/IS-period SuiteQL query via [`suiteql.py`](../../scripts/connectors/suiteql.py), ties it out, and stages it. It accepts `--replay` to run against the offline `ReplayTransport` fixtures with zero live credentials (useful for a dry run before your first live pull). Under the hood this is the same `export_via_suiteql` path in [`adapters/netsuite.py`](../../scripts/connectors/adapters/netsuite.py).

3. **If it won't tie, diagnose before you escalate.** `python3 scripts/connectors/netsuite_doctor.py diagnose` — this is where the ranked NetSuite-specific causes live, starting with the #1 tie-out failure mode: an omitted `subsidiary` filter silently pulling a consolidated (wrong-grain) result. `suiteql.tie_out()` itself only tells you the pull didn't net to zero; the doctor is where you find out *why*.

4. **Run the close-to-report cycle.** `python3 scripts/controller_cycle.py --entity ... --coa ... --tb <the staged NetSuite pull> ...` (see [`../../commands/run-controller-cycle.md`](../../commands/run-controller-cycle.md) for the full argument list). This produces the single HTML review surface — statements, reconciliation, flux — and **submits** the package. It does not approve or lock.

5. **Review → approve → lock.** The human, SoD-enforced steps, unchanged from every other source:

   ```shell
   python3 scripts/close_state.py --run-dir <dir> review  --actor <reviewer>
   python3 scripts/close_state.py --run-dir <dir> approve --actor <approver> --threshold <sod_threshold>
   python3 scripts/close_state.py --run-dir <dir> lock    --actor <approver> --approval-token <out-of-band>
   ```

   If the submit step pinned `--source-tb-sha256 <hash of the NetSuite pull>`, a later re-run of `close_state.py verify-source --current-hash <hash>` tells you whether NetSuite's numbers **changed after sign-off** — the cross-system drift control this skill adds on top of NetSuite's own audit trail.

(Optional) **Drill-through lineage.** [`netsuite_lineage.py`](../../scripts/connectors/netsuite_lineage.py) extends the generic [`gl_lineage.py`](../../scripts/connectors/gl_lineage.py) pattern with NetSuite-specific source-document keys so each statement line traces back to the originating NetSuite transaction.

---

## The honest close-in-a-day framing

**Do not sell "close in a day" for a first-time build.** The BEFORE-CLOSE-DAY phase — certificate issuance, integration-record creation, role provisioning — needs a NetSuite ADMIN and your change-control process, and realistically takes **days**, not hours, the first time. What *can* approach a day, once wired, is the **recurring** close: a layperson running steps 1–5 above against an already-provisioned NetSuite account. Conflating the two is the single most common overclaim in this space — say "one-time setup: days; recurring close, once wired: can approach a day" every time this skill's speed is discussed.

## What this is NOT

- **Not** a certified or NetSuite-verified connector. It is a reference implementation exercised against synthetic, offline fixtures.
- **Not** proof that the source GL is correct, reconciled, or complete. A tying trial balance is necessary, not sufficient — [`reconciliation-summary`](../reconciliation-summary/SKILL.md) / [`reconciliation-automatch`](../reconciliation-automatch/SKILL.md) and the governed review→approve→lock spine ([`close-approval-workflow`](../close-approval-workflow/SKILL.md)) still apply.
- **Not** a replacement for NetSuite's own native close tooling (Period Close Checklist, Intelligent Close Manager, Advanced Revenue Management, OneWorld eliminations) — see [`../../knowledge/netsuite-integration-landscape.md`](../../knowledge/netsuite-integration-landscape.md) for what NetSuite ships natively vs. this skill's whitespace.
- **Not** an accounting/audit/tax opinion — outputs are decision-support (see [`../../CLAUDE.md`](../../CLAUDE.md) §3).
- **Not** an automated way around SoD sign-off — `run-controller-cycle` submits only; approval and lock stay separate, human-invoked, SoD-enforced steps.

## Verify before you trust the numbers

Run the connector acceptance suite: `python3 scripts/test_connectors.py` (proves the M2M assertion build, the persist/mint paths, the SuiteQL BS-cumulative/IS-period query shape, the tie-out hard-fail, and the 100,000-result cap breach path — all against synthetic fixtures, zero live credentials). Before a **live** build, browser-verify the settling-gated NetSuite facts in [`../../knowledge/finance-elt-connector-facts.md`](../../knowledge/finance-elt-connector-facts.md) against your own NetSuite sandbox.
