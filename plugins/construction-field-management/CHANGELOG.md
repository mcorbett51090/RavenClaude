# Changelog — construction-field-management

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

## 0.2.0 — 2026-06-08

Depth pass — same 3 agents / 3 skills / 3 commands / 2 templates / 1 hook, deepened to the v0.2.0 standard.

- **Best-practices → 12** — added `route-design-intent-to-an-rfi-not-the-field` and
  `an-sov-is-the-billing-contract-not-a-front-load` to the original eight (RFI-to-a-dated-response,
  ball-in-court, nothing-built-unpriced/uninspected, schedule-submittals-backward, one-current-set,
  cost-to-complete, safety-per-task, punch-to-zero, closeout-releases-retainage, contemporaneous-records).
  `best-practices/README.md` indexes all twelve.
- **Knowledge bank → 5 Mermaid decision trees** — is-this-a-change-order, submittal/inspection
  sequencing vs. the install, how-to-bill-a-change (PCO/COR/CCD), is-the-cost-report-honest (CTC),
  and substantial-completion/closeout-readiness — plus the dated 2026 standards/forms map, now with
  earned-value and field-records rows and a pointer to the runnable calculator.
- **Scenarios → 5 dated field notes** — added `under-budget-until-the-ctc-landed` (cost-to-complete),
  `generic-toolbox-talk-on-a-confined-space-day` (task-specific JHA/OSHA), and
  `substantial-completion-held-the-retainage` (closeout package) to the original two.
- **Runnable calculator** — `scripts/construction_calc.py` (stdlib-only, argparse): `payapp`
  (SOV %-complete → work completed, retainage, current payment due, AIA G702/G703 style), `changeorder`
  (running adjusted contract sum after executed COs), and `earned-value` (CV/SV/CPI/SPI from BCWP/ACWP/BCWS,
  optional EAC/VAC). Ruff-clean (F, E9, B, C4, I, UP).

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
