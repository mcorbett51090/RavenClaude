# Changelog — construction-field-management

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

## 0.1.0 — 2026-06-08

Initial release. The field side of construction project delivery — executing a building job on the
jobsite after design is done — alongside the design / PM / trade cluster.

- **3 agents** — `project-engineer` (RFIs, submittals + the submittal log, daily logs, document control,
  schedule coordination, meeting minutes), `cost-and-change-controls-lead` (schedule of values, AIA G702/G703
  pay applications, change orders PCO→CO, cost codes, budget-vs-actual / cost-to-complete, retainage),
  `field-and-safety-coordinator` (punch lists, QA/QC + inspection-and-test plans, safety/JHA + toolbox talks +
  OSHA, inspections, closeout). Each carries the full scenario-authoring frontmatter.
- **3 skills** — `rfi-and-submittal-workflow`, `change-order-and-pay-application`, `field-qaqc-and-safety`.
- **Knowledge bank** — `construction-field-management-decision-trees.md`: Mermaid trees (RFI-vs-change triage,
  submittal sequencing vs. install date, is-this-field-event-a-change-order, QA hold-point selection) + a dated
  2026 standards/forms map (AIA G702/G703, EJCDC, OSHA, ITP/CPM conventions) (`[verify-at-build]`).
- **8 best-practices**, **3 commands** (`draft-rfi`, `assemble-pay-app`, `run-punch-list`),
  **2 templates** (RFI, change-order log), **1 advisory hook**
  (`check-construction-field-management-anti-patterns.sh`; `CONSTRUCTION_STRICT=1` to make it blocking),
  and a **scenarios bank** (2 field notes).
- Seams: drawings / BIM / design intent → `architecture-aec`; master schedule / risk / RAID → `project-management`;
  trade means-and-methods → `skilled-trades-contracting`. Requires `ravenclaude-core@>=0.7.0`.
