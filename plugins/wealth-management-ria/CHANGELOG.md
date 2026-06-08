# Changelog — wealth-management-ria

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

## 0.1.0 — 2026-06-08

Initial release. The personal financial-advisory / RIA-practice layer — educational and operational
support for a Registered Investment Adviser serving individual clients, **explicitly not personalized
investment advice**.

- **3 agents** — `financial-planner` (goal-based planning, retirement & withdrawal strategy — 4% rule /
  guardrails / sequence-of-returns risk, tax-aware account use IRA/Roth/401k/taxable/HSA, estate basics),
  `portfolio-analyst` (asset allocation, the Investment Policy Statement, calendar/threshold rebalancing,
  risk/factor basics, tax-loss harvesting & asset location), `advisory-compliance-and-client-review-lead`
  (fiduciary duty & Reg BI, Form ADV basics, suitability/KYC, periodic client reviews, books-and-records,
  marketing-rule basics). Each carries the full scenario-authoring frontmatter.
- **3 skills** — `goal-based-financial-plan`, `portfolio-construction-and-ips`, `client-review-and-suitability`.
- **Knowledge bank** — `wealth-management-ria-decision-trees.md`: Mermaid trees (tax-aware account-funding
  order, retirement withdrawal strategy, education-vs-personalized-advice, fiduciary-vs-Reg-BI standard) +
  a dated 2026 reference map (`[verify-at-build]`).
- **8 best-practices**, **3 commands** (`build-financial-plan`, `draft-ips`, `client-review`),
  **2 templates** (Investment Policy Statement, client-review & suitability checklist), **1 advisory hook**
  (`check-wealth-management-ria-anti-patterns.sh`; `RIA_STRICT=1` to make it blocking), and a
  **scenarios bank** (2 field notes).
- Seams: corporate FP&A → `finance`; deep securities-law → `regulatory-compliance`; advisory-fee billing →
  `fintech-payments-engineering`; client PII/data security → `ravenclaude-core/security-reviewer`.
  Requires `ravenclaude-core@>=0.7.0`.
