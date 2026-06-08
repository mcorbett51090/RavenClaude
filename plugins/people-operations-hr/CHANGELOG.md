# Changelog — people-operations-hr

All notable changes to this plugin are documented here. Versioning is semver; bump on every user-visible change (AGENTS.md).

## [0.1.0] — 2026-06-08

Initial release.

- **4 agents** — `people-ops-lead` (orchestrator), `talent-acquisition-strategist`, `total-rewards-comp-analyst`, `people-analytics-engagement-specialist`, each carrying the full scenario-authoring schema.
- **5 skills + 5 commands** — `diagnose-attrition`, `model-hiring-plan`, `design-comp-bands`, `run-pay-equity-review`, `read-engagement-signals`.
- **4-file knowledge bank** — KPI glossary, unit economics, 2025–2026 benchmark/regulatory context, and a Mermaid decision-tree file (rising attrition · open req won't close · pay-equity gap surfaced).
- **`scripts/people_calc.py`** — stdlib-only calculator with four modes: `attrition`, `hiring-plan`, `comp-band`, `pay-equity`. Decision-support only.
- **4 templates** — scorecard, exec readout, engagement brief, hiring-plan tracker.
- **8 best-practice rules** — one per house opinion (§3).
- **Scenarios bank** — README + 3 dated, unverified engagement narratives.
- **1 advisory hook** — flags People-Ops anti-patterns (unbaselined metric, unsourced benchmark, employee PII); set `PEOPLE_OPERATIONS_HR_STRICT=1` to make it blocking.
