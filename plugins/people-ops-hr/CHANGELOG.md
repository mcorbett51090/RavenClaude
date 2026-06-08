# Changelog — people-ops-hr

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

## 0.1.0 — 2026-06-08

Initial release. The People Operations / HR layer for SMBs — the human side of running a company
(lifecycle, hiring, total rewards), distinct from `staffing-operations` (the staffing-agency business).
**Not legal advice — employment-compliance basics are flagged for counsel, never opined on.**

- **3 agents** — `people-ops-generalist` (employee lifecycle, handbook & policy authoring, HRIS data hygiene,
  leave/PTO, employee-relations basics), `talent-acquisition-lead` (structured hiring, job ladders, interview kits
  & scorecards, hiring-funnel metrics, candidate experience, offers), `total-rewards-analyst` (compensation bands
  & ranges, leveling/job architecture, benefits-design overview, pay equity, merit/promotion cycles). Each carries
  the full scenario-authoring frontmatter.
- **3 skills** — `structured-hiring`, `comp-band-and-leveling`, `handbook-and-policy`.
- **Knowledge bank** — `people-ops-hr-decision-trees.md`: 2 Mermaid trees (is-this-hire-structured-and-fair,
  is-this-comp-decision-defensible) + a dated 2026 reference map (HRIS / ATS / comp-data / pay-equity / review-cycle
  practice; `[verify-at-build]`, never legal advice).
- **8 best-practices**, **3 commands** (`build-interview-kit`, `build-comp-bands`, `draft-handbook-policy`),
  **2 templates** (interview kit, comp-band & leveling sheet), **1 advisory hook**
  (`check-people-ops-hr-anti-patterns.sh`; `HR_STRICT=1` to make it blocking), and a **scenarios bank** (2 field notes).
- Seams: staffing-**agency** operations → `staffing-operations`; payroll/GL & comp budgeting → `finance`;
  benefits insurance/underwriting → `insurance-life-health-benefits`. Requires `ravenclaude-core@>=0.7.0`.
