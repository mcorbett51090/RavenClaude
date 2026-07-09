# Changelog — finops-cloud-cost

All notable changes to this plugin are documented here. Versioning is semver; bump on every user-visible change (AGENTS.md).

## [0.1.1] — 2026-07-09

- **Knowledge bank** — added a **FOCUS standard** section to `knowledge/finops-cloud-cost-context.md`: what the FinOps Open Cost & Usage Specification is (vendor-neutral normalized cost/usage schema across clouds), that it is the industry-standard data model, and current version **v1.4** (ratified 2026-06-04) with headline additions — invoice-to-usage reconciliation (Invoice Detail + Billing Period datasets), the expanded Contract Commitment dataset, and `CommitmentProgramEligibilityDetails`. Notes Validator 1.4 conformance expected Q3 2026. Dated, sourced.

## [0.1.0] — 2026-06-08

Initial release.

- **4 agents** — `finops-lead`, `cost-allocation-analyst`, `commitment-planning-specialist`, `unit-economics-strategist`, each carrying the full scenario-authoring schema.
- **5 skills + 5 commands** — `measure-allocation`, `read-unit-economics`, `harvest-waste`, `plan-commitments`, `forecast-and-alert`.
- **4-file knowledge bank** — KPI glossary, unit economics, 2025–2026 context, and Mermaid decision trees.
- **`scripts/finops_cloud_cost_calc.py`** — stdlib calculator: `commitment`, `unit-cost`, `rightsizing`. Decision-support only.
- **4 templates · 8 best-practice rules · scenarios bank · 1 advisory hook**.
