# Changelog — finance

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.17.4] — 2026-07-08

Docstring accuracy fix from the autonomous 3-panel repo review (run 2026-07-08). No behavior change.

- **P3 — `scripts/connectors/oauth_client.py` docstring corrected.** The error-cause routing table promised "429 (throttled) → BACKOFF_RETRY (honor Retry-After, then retry)", but the shipped API (`refresh` / `get_access_token`) raises `TokenRefreshError` on a 429 and never itself backs off or retries (`honor_retry_after` is a helper for the caller to drive). The docstring now states accurately that the client _classifies_ the cause while the caller honors Retry-After and re-invokes — removing a "then retry" promise the component didn't keep. (Whether to implement the retry loop inside the client is a design question deferred to the maintainer.)

## [0.17.1] — 2026-07-06

Hardening + evidence for the live-integration tier (no new skills; W3 warehouse RLS moves from *specified* to *executed* at the DB layer).

- **Postgres FORCE-RLS is now PROVEN, not just specified.** `skills/warehouse-dashboard/models/rls/run_rls_denial_test.sh` stands up a disposable `postgres:16` container, applies the shipped `close_rls_policies.sql`, and runs the cross-entity denial test — no live creds. Result (see `RLS_TEST_EVIDENCE.md`): a controller granted entity A sees only A; an explicit `WHERE entity_id=B` **leaks zero rows**; unset/empty grants deny all; and the array claim `{A,C}` returns exactly the 2-entity portfolio. Answers the security review's open question *"is the FORCE-RLS actually reached?"* — yes.
- **Two fixes surfaced by executing it, folded into the shipped SQL:** `rls_cross_entity_denial_test.sql` now wraps each grant+query in `BEGIN/COMMIT` (a bare `SET LOCAL` is a silent no-op in autocommit → false-fail); and `close_rls_policies.sql` coerces the tenant GUC via `NULLIF(current_setting('app.entity_ids', true), '')::uuid[]` so a lingering empty-string `SET LOCAL` fail-closes to zero rows instead of aborting the query with a cast error.
- **Knowledge correction (dated, cited):** `finance-elt-connector-facts.md` — NetSuite concurrency was wrong (`~1`); corrected to the account-level **pooled 5 / 15 / 20 (+10 per SuiteCloud Plus)** limit, flagged doc-sourced / re-confirm before go-live.
- **Pitch refreshed** (`docs/controller-autopilot-pitch.html`) — the four live-tier capabilities move from "Next" to shipped, with the honest reference-impl framing and the Postgres-RLS-proven note; genuinely-remaining work (record provider fixtures, stand up Cube, wire the IdP) is stated as the consumer's step.

Still specified-not-executed (needs infra a container can't cheaply supply): the Cube `access_policy` denial test (needs a running Cube) and the live IdP/JWKS. Consolidated suite unchanged: 272 tests green + the containerized RLS runner passing.

## [0.17.0] — 2026-07-06

Feature — **controller-autopilot live-integration tier** (FORGE `fca-live-integration-tier`; four workstreams built in parallel, cross-model critic + red-team, mandatory security-reviewer). Skills 18 → 22.

- **W1 multi-currency (fully-tested real logic)** — `scripts/remeasure.py`: ASC 830 / IAS 21 **remeasurement (temporal)** + **translation (current-rate)** producing a CTA plug (→OCI) or remeasurement G/L (→net income); per-account `rate_class` COA column with a lint gate, a CTA analytical self-check (per-equity-account historical rates, dividend-aware), hyperinflation refusal (IAS 29 out of scope), and a byte-identical zero-drift no-op on all-USD groups. The FORGE critic **independently reconfirmed** both goldens (current-rate **CTA +200**; temporal **loss −80**). Skill `multi-currency-translation`.
- **W2 connectors (reference impl + mock/replay)** — `scripts/connectors/`: OAuth2 GL extractor for QBO/NetSuite/Sage Intacct/Xero (atomic persist-then-use rotating refresh, per-entity lock, error-cause routing, Xero 30-min grace), a record/replay transport that never opens a live socket, and a GL-lineage emitter whose first 6 columns are byte-identical to `statement_engine --gl-detail`. Skill `live-connectors`.
- **W3 warehouse/RLS (reference + tested claims core)** — `scripts/close_package_to_rows.py` (close-package → fact/dim), `scripts/entity_rls.py` (entity-level **array-claim** RLS), and a semantic model (dbt marts + Cube + Postgres FORCE-RLS) **reusing data-platform** wholesale. Skill `warehouse-dashboard`.
- **W4 IdP-SoD (reference impl)** — `scripts/close_identity.py`: evolves `close_state.py`'s config-asserted `--actor` into an OIDC-verified identity (claim + signature validation; HS256 dev/fixture, RS256/ES256/JWKS via optional PyJWT that **refuses loudly** when absent; `alg:none`/alg-confusion rejected), token-level preparer≠approver SoD keyed on `sub@iss`, and a signature-bound step-up token for LOCK. Skill `idp-segregation`.

**Security review (mandatory gate).** A `security-reviewer` pass returned must-fix-before-merge; all addressed before this release: a 🔴 Cube `portfolio_close` view shipped without its own `access_policy` (now filters `entity_id ∈ allowed_entities`, `operator: in`); `entity_rls.resolve()` now fails closed on non-list input; a `bind_entitlement_to_identity()` seam binds the RLS entitlement token and the SoD identity token to one issuer+subject (closing the split-brain gap); and `assert_fresh_stepup` now verifies the step-up token's signature + subject and rejects `iat`-only tokens.

**Honest scope.** W1 is fully-tested logic. W2/W3/W4 are **assumption-complete reference implementations with mock/replay harnesses + consumer first-light checklists — NOT verified against any live provider, warehouse, or IdP** (none exist in this environment). Every W2/W3/W4 artifact badges this. Consolidated suite: **272 acceptance tests across 11 files, all green**; ruff-clean; stdlib-first.

## [0.16.1] — 2026-07-06

Bug fix (P3) — the advisory `flag-finance-anti-patterns.sh` IBAN PII check used `grep -Eni` (case-insensitive), so `[A-Z]{2}` also matched lowercase and over-flagged ordinary `<2 letters><2 digits><alnum>` tokens (e.g. commit hashes) as plaintext IBANs. Dropped `-i` (real IBANs are uppercase; the sibling SSN/card checks are already case-sensitive). No behavior change for any other check.

## [0.16.0] — 2026-07-06

Feature — **controller-autopilot full build** (FORGE roadmap P6–P12, built in parallel and consolidated). Extends the v0.15.0 first slice to the full governed cycle:

- **5 skills** (18 total) — `finance-elt-staging`, `reconciliation-automatch`, `consolidate-entities`, `per-entity-dashboard`, `close-schedules`.
- **5 stdlib engines** — `tb_stage.py` (raw QBO/NetSuite/Sage/Xero export → canonical trial-balance staging, **byte-identical to a dbt `stg_trial_balance` model**, with close-period watermark + entity/currency dims + atomic write); `recon_match.py` (GL↔subledger auto-match: exact / tolerance / grouped, with threshold auto-certification + explainable match trail); `consolidate.py` (multi-entity roll-up + **intercompany elimination** worksheet + CTA note, reusing `statement_engine`); `entity_dashboard.py` (self-contained per-entity dashboard from a close-package JSON); `schedule_engine.py` (fixed-asset depreciation rollforward, prepaid amortization, deferred-revenue waterfall — each ties beginning + movements = ending).
- **3 knowledge docs** — `finance-elt-connector-facts` (sourced QBO/NetSuite/Sage Intacct/Xero auth + rate-limit facts, rotating-refresh-token failure mode + mitigation, dated QBO Reports-API gate, settling gates for unverified lifetimes), `tax-close-calendar` (coordination checklist, not tax advice), `secrets-pii-gate`.
- **2 templates** — `connector-config.template.json` (env-var NAMES only, never values), `tax-calendar.md`.
- **2nd advisory hook** — `scan-finance-secrets.sh` (secret/PII shape scan; advisory by default, `--ci` for a non-zero pre-merge gate; excludes env-var references + well-known test placeholders). The FORGE red-team's P0 follow-up. Wired into `hooks.json`.
- **Tests** — consolidated suite now **7 files / 121 acceptance tests, all green**; ruff-clean; stdlib-only.

Counts: skills 13→18, knowledge 13→16, templates 8→10, hooks 1→2. Deferred to its own decoupled PR: the `accounting-bookkeeping` scope-down.

## [0.15.0] — 2026-07-06

Feature — **controller-autopilot** first slice (FORGE plan `financial-controller-autopilot`). Adds a governed close-to-report cycle a financial controller installs and runs, leaving only review + approve:

- **4 skills** — `produce-gaap-statements`, `author-coa-mapping`, `reconciliation-summary`, `close-approval-workflow` (skill count 9 → 13).
- **1 command** — `run-controller-cycle` (the submit-only orchestration front door).
- **5 stdlib scripts** — `statement_engine.py` (TB → IS/BS/draft CF, classification-tested, blocks on unmapped accounts), `entity_config.py`, `reconcile_summary.py`, `close_state.py` (review→approve→lock state machine with enforced SoD + append-only hash-chained audit log), `controller_cycle.py` (orchestrator + self-contained HTML close package). Plus `test_controller_autopilot.py` — an 18-test acceptance/regression suite (all passing).
- **Synthetic worked entity** (`Meridian Robotics Inc.`) with a hand-derived golden + a deliberate-misclassification negative fixture, and a `controller-autopilot-architecture` knowledge doc (knowledge 12 → 13).
- **Honesty by design:** statement production is treated as a commodity (every GL emits statements natively) — the moat is the governed cycle + enforced controls + the COA-mapping asset. Local-tier identity is config-asserted (tamper-evident, not tamper-preventing); TB-only output is badged not-audit-traceable; CF is an unaudited draft. No false competitive claims.
- **Deferred (roadmap):** finance-shaped ELT (QBO/NetSuite/Sage Intacct/Xero), reconciliation auto-match/auto-cert, consolidation + intercompany, productized per-entity dashboard (reuse `data-platform`), secrets/PII scan gate.

No breaking change — all prior agents/skills/templates unchanged; the corrected catalog skill count (was a stale "46 skills" boilerplate → now 13) only fixes drift.

## [0.14.2] — 2026-06-22

Bug fix — the advisory `flag-finance-anti-patterns.sh` hook's credit-card PAN check used PCRE non-capturing groups `(?:…)` inside a POSIX-ERE `grep -E`, so Visa and Discover PANs were never flagged (the group matched nothing and `grep` printed a `? at start of expression` warning to stderr on every run). Rewrote the two groups as ERE-safe capturing groups `(…)`; all four card brands (Visa/MC/Amex/Discover) now match cleanly with no stderr noise. No behavior change for any other check.

## [0.14.1] — 2026-06-14

Maintenance — agent-description length cap (≤300 chars for the orchestrator budget) + README touch. No behavior change.

## [0.14.0] — 2026-06-05

Non-code-vertical value-add build-out — adds the scenarios bank, two new Mermaid decision-tree knowledge files, and a runnable corporate-finance / FP&A calculator. Net-new against PR #315 (which added the consolidated decision-trees, best-practices, and templates); honestly dispositions the code-runtime tier as N-A.

- **Scenarios bank** (`scenarios/`) — new directory + README + **4** dated, scope-tagged engagement scenarios (mirrors the marketplace 9-field schema, `product_version: "n/a"` for a non-code vertical): budget-vs-actual variance investigation, 13-week cash crunch, driver-based forecast rebuild, unit-economics / contribution-margin teardown. Each carries an "Action for the next analyst" lesson and cited public benchmarks. §8b TODO retired; inline **scenario-retrieval priors** added to `fpa-analyst`, `treasury-analyst`, and `financial-modeler`.
- **2 new Mermaid decision-tree knowledge files** (complementing #315's `finance-decision-trees.md`, not duplicating it — forecast-method and capex/build-vs-buy-NPV trees already existed there):
  - `scenario-vs-sensitivity-vs-simulation-decision-tree.md` — how to model uncertainty on a base case: sensitivity/tornado (find the levers) → scenario analysis (one switch, base/upside/downside) → Monte-Carlo (only on data-sourced distributions, else fall back to scenarios + state the gap).
  - `reforecast-vs-hold-the-budget-decision-tree.md` — whether to revise the plan when actuals diverge: reconcile/triage first → hold (one-time) / update rolling forecast only (late-year) / reforecast-budget-held / formal re-plan with governance. Keeps the budget as the yardstick.
- **Runnable calculator** `scripts/finance_calc.py` (stdlib only, Python 3.8+, ruff-clean) — four modes: `npv-irr` (DCF NPV + bisection-solved IRR for capex / build-vs-buy / lease-vs-buy), `variance-bridge` (price/volume/mix decomposition that sums exactly to the total), `runway` (direct-method weekly cash trough + run-out + min-buffer/covenant breach), `unit-economics` (gross-margin LTV + CAC payback + LTV:CAC on defensible definitions). Decision-support, not accounting/audit/tax/investment advice.

### Honestly N-A for a non-code vertical (documented, not forced)
The code-runtime tier (bundled code-aware MCP server, LSP / `.lsp.json`, `bin/`, monitors, output-styles, themes, `settings.json`) is genuinely not applicable to a corporate-finance / FP&A advisory vertical. Each is dispositioned with a one-line reason in `CLAUDE.md` § "Value-add completeness (build-out 2026-06-05)". The one runtime item with real non-code value — a runnable calculator — **was** built (`scripts/finance_calc.py`).

### Shared-file changes required (orchestrator-owned, NOT done here)
- `.repo-layout.json` `allowed_globs` already covers the new paths — `plugins/*/scenarios/**`, `plugins/*/scripts/**`, `plugins/*/knowledge/**`, and `plugins/*/CHANGELOG.md` all exist; no new glob needed.
- `.claude-plugin/marketplace.json` `version` bump to `0.14.0` to mirror `.claude-plugin/plugin.json` (CI fails on drift).

## [0.13.x] and earlier — pre-build-out

7 specialist agents (`fpa-analyst`, `financial-modeler`, `controller`, `treasury-analyst`, `valuation-analyst`, `audit-prep-specialist`, `board-pack-composer`), 9 skills, 8 templates, 5 commands, an advisory anti-pattern hook, a cited best-practices set, and a research-grounded knowledge bank (variance triage, consolidated decision-trees, ASC 805 / 718 / 740, accrual & cutoff, cost accounting, WACC sourcing, FP&A operating model + unit economics). PR #315 added the consolidated decision-trees, the `best-practices/` set, and `templates/`.
