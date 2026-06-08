# Changelog — legal-ops-clm

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

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
