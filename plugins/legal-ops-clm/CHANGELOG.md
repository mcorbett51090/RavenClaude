# Changelog — legal-ops-clm

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

## 0.2.0 — 2026-06-08

Depth build-out to the v0.2.0 standard. Still the operational / process layer of a corporate (in-house)
legal function and CLM — explicitly **not legal advice**; a qualified lawyer owns every legal-judgement call.

- **Best-practices: 8 → 12.** Added `the-key-clauses-carry-the-risk`, `the-repository-is-a-schema-not-a-drawer`,
  `ambiguity-is-a-flag-not-a-guess`, and `cycle-time-is-measured-in-business-days`; `best-practices/README.md`
  index reconciled to all 12.
- **Knowledge bank: 2 → 5 Mermaid decision trees** in `legal-ops-clm-decision-trees.md` (added intake-triage,
  redline flag/note/escalate, and obligation-extraction track-or-flag trees), alongside the kept, dated 2026
  CLM / e-signature capability map (`[verify-at-build]`).
- **Scenarios bank: 2 → 5 field notes** (9-field schema, `reviewed: false`). Added `redline-escalated-every-comma`,
  `repository-was-a-folder-drawer`, and `obligation-leaked-after-signature`; `scenarios/README.md` index reconciled.
- **Runnable calculator — `scripts/clm_calc.py`** (stdlib only, Python 3.8+, argparse; ruff-clean F,E9,B,C4,I,UP):
  `renewal-window` (expiry + notice deadline + tiered 90/60/30 auto-renew alert dates from effective + term + notice),
  `cycle-time` (intake→signed business-day duration + per-class SLA breach flag, weekend/holiday-aware),
  `obligation-aging` (days-to-due buckets: overdue / 0-30 / 31-60 / 61-90 / 90+). A **calculator, not a data source** —
  the user supplies every date; outputs are operational decision-support, **not** legal advice.
- Description count updated (12 best-practices); counts reconciled in `CLAUDE.md` (new v0.2.0 milestone).

## 0.1.0 — 2026-06-08

Initial release. The operational / process layer of a corporate (in-house) legal function and contract
lifecycle management (CLM) — explicitly **not legal advice**; a qualified lawyer owns every legal-judgement call.

- **3 agents** — `legal-ops-lead` (legal intake & triage, request workflow, contract playbooks, matter management,
  legal-ops metrics & reporting), `contract-review-specialist` (clause libraries, redline review vs. standard/fallback,
  risk flagging, key-term extraction, approval routing), `obligations-and-renewals-analyst` (obligation extraction &
  tracking, renewal/expiry/auto-renew tracking with notice-window alerts, contract repository & metadata, reporting).
  Each carries the full scenario-authoring frontmatter.
- **3 skills** — `legal-intake-and-playbooks`, `contract-review-and-redline`, `obligations-and-renewals`.
- **Knowledge bank** — `legal-ops-clm-decision-trees.md`: 2 Mermaid trees (self-serve-vs-escalate; renew / renegotiate / exit)
  + a dated 2026 CLM / e-signature capability map (`[verify-at-build]`).
- **8 best-practices**, **3 commands** (`design-legal-intake`, `review-contract`, `track-obligations-renewals`),
  **2 templates** (contract playbook, obligations-and-renewals register), **1 advisory hook**
  (`check-legal-ops-clm-anti-patterns.sh`; `CLM_STRICT=1` to make it blocking), and a **scenarios bank** (2 field notes).
- Seams: a law firm's own business → `legal-small-firm`; procurement/supplier contracts → `procurement-sourcing`;
  data-privacy/DPA clauses → `data-governance-privacy`; any legal opinion → a human lawyer. Requires `ravenclaude-core@>=0.7.0`.
