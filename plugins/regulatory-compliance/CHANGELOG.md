# Changelog — regulatory-compliance

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.12.2] — 2026-07-02

### Fixed

- **`CLAUDE.md` corrected the SAR/STR blocking instruction to `exit 2`.** The doc told consumers to flip the hook's bottom `exit 0` to `exit 1` to block PII writes — but `exit 1` is a non-blocking error Claude Code silently swallows, so a consumer following it verbatim got a hook that still allowed the write on the plugin's highest-stakes control. The hook's own header + runtime comments already said `exit 2`; the doc now matches. (Autonomous 3-panel repo review, P1.)

## [0.12.1] — 2026-06-14

Bug fix (security-relevant) — the `scrub-confidential-pre-write.sh` PII hook's credit-card PAN check used PCRE non-capturing groups `(?:…)` inside a POSIX-ERE `grep -E`, so Visa and Discover PANs slipped past the confidentiality scan entirely (the group matched nothing and emitted a `? at start of expression` warning to stderr). For an engagement that flips this hook to `exit 2` to **block** SAR/STR writes, two of four card brands were a fail-open gap. Rewrote the two groups as ERE-safe capturing groups `(…)`; all four brands now match with no stderr noise. SSN/EIN/IBAN checks were already ERE-clean and unchanged.

## [0.12.0] — 2026-06-05

Value-add build-out (non-code financial-regulatory vertical). Builds on PR #315's consolidated decision-trees + best-practices + templates by adding the net-new gaps: a scenarios bank, two complementary Mermaid decision-tree knowledge files, and a stdlib risk-scoring calculator. Resolves the §8b scenarios-bank TODO in `CLAUDE.md`.

- **Scenarios bank** (`scenarios/`) — the `README.md` index (added in #315) is now backed by **4** dated, scope-tagged, unverified engagement scenarios (marketplace 9-field schema, `product_version: "n/a"`):
  - `2026-06-05-aml-alert-backlog-no-file-decision.md` — splitting an AML alert backlog into suspicion-bearing vs non-suspicion lanes; the FinCEN SAR 30/60-day + continuing-activity 90/30 clock (US-specific, `[verify-at-use]`).
  - `2026-06-05-regulatory-change-impact-assessment.md` — the monitor → applicability → impact-assessment funnel; applicability before obligation; per-licence gap analysis.
  - `2026-06-05-control-testing-design-gap.md` — design effectiveness before operating effectiveness; a clean operating sample on a mis-designed detective control.
  - `2026-06-05-third-party-vendor-risk-retiering.md` — tier vendors by criticality (June 2023 interagency guidance), scale diligence to tier, flag concentration.
- **2 new Mermaid decision-tree knowledge files** (complement #315's consolidated trees, which already cover CDD-depth / reportability / control-type / regime / which-return / Bermuda-class):
  - `risk-rating-and-escalation-decision-tree.md` — score inherent → residual, test against board-approved appetite, route to the right authority tier (board / senior-management / line / accept-and-monitor). AML/sanctions/fair-lending escalation-by-default.
  - `third-party-risk-tiering-decision-tree.md` — tier a third party by criticality, scale due diligence + contract terms + ongoing monitoring across the relationship life cycle, flag concentration. Anchored on the US June-2023 interagency third-party guidance with explicit non-US/non-banking carve-outs (DORA, EBA).
- **Runnable calculator** `scripts/compliance_calc.py` (stdlib only, Python 3.8+, ruff-clean) — three modes: `risk-score` (inherent + residual on likelihood×impact + within/outside-appetite verdict), `customer-risk` (weighted factor score + firm-defined bands), `sample-size` (control-testing coverage + firm-supplied frequency→count lookup). Bakes in **no** regulatory threshold and **no** legal advice — every scale, weight, band, and threshold is the firm's own and `[verify-at-use]`. Decision-support, not legal/regulatory/audit advice (CLAUDE.md §3 #10, §6).
- **Scenario-retrieval inline priors** added to the four most-likely-to-benefit agents (`aml-kyc-analyst`, `risk-and-controls-specialist`, `policy-and-procedure-writer`, `examination-prep-specialist`) so they consult the bank with the mandatory unverified-scenario preamble.
- **CLAUDE.md** — removed the §8b scenarios-bank TODO, added a "Value-add completeness (build-out 2026-06-05)" disposition table and a milestones note, and listed the two new trees + the script in the knowledge / tooling sections.

### Honestly N-A for a governance vertical (documented, not forced)
The code-runtime tier (bundled/recommended code-aware MCP server, LSP, `bin/`, monitors, output-styles, themes, `settings.json` tuning, `NOTICE.md`) is genuinely not applicable to a financial-regulatory advisory vertical that operates on documents and analysis, not a codebase or runtime. Each is dispositioned with a one-line reason in `CLAUDE.md` § "Value-add completeness (build-out 2026-06-05)".

### Accuracy posture
Regulatory facts are jurisdiction-specific and volatile. Every load-bearing figure (SAR clocks, interagency-guidance dates, sampling counts, all scoring scales/thresholds) carries an inline `[verify-at-use]` marker and a primary-source citation (FinCEN, OCC, Federal Register, FDIC) or is explicitly the firm's own model. No regulation, rule, or figure is invented.

### Shared-file changes required (orchestrator-owned, NOT done here)
- `.repo-layout.json` `allowed_globs` already covers `plugins/*/scenarios/**`, `plugins/*/scripts/**`, and `plugins/*/CHANGELOG.md` — no new globs needed.
- `.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json` `version` bump `0.11.3` → `0.12.0`.

## [0.11.3] and earlier

12 specialist agents (6 function + 6 jurisdiction/regulator), 10 skills, 11 templates, 5 commands, 27 best-practice rules, a defensive PII-scrubbing hook, and a 19-file primary-source-cited regulator knowledge bank (13 BMA + CIMA/Bahamas/Jersey-Guernsey/UK-PRA/US + a global standard-setter directory + the Basel reference). PR #315 consolidated the knowledge decision-trees (`compliance-decision-trees.md`, `regulator-finding-severity-triage.md`), the `best-practices/` set, and the `templates/` set, and added the `scenarios/README.md` index. See the plugin `version` field + git history for the full arc.
