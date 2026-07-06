# Changelog — higher-education-administration

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-07-02

Initial release.

### Added

- **3 agents** — `higher-ed-administration-lead` (enrollment strategy, budget / net-tuition-revenue model, retention/completion, cross-functional coordination across admissions/registrar/aid/student-success, accreditation), `enrollment-management-strategist` (the inquiry->apply->admit->yield->melt funnel, yield & discount-rate modeling, financial-aid leveraging, recruitment), `student-success-advisor` (retention/persistence, early-alert, advising, at-risk intervention, completion, DFW-course analysis).
- **4 skills** — `enrollment-funnel-and-yield`, `financial-aid-and-discount-rate`, `retention-and-student-success`, `registrar-and-academic-operations`.
- **Knowledge bank** — `higher-ed-decision-trees.md` (4 Mermaid trees: yield/melt intervention, discount-rate / aid-leverage decision, at-risk student triage, enrollment-vs-retention lever choice) and `higher-ed-reference-2026.md` (dated reference: funnel benchmarks `[ESTIMATE]`, discount-rate norms, retention/persistence/completion metric definitions — each with source placeholder + retrieval date + verify-at-use).
- **5 best-practices** — yield is cheaper to defend than to replace, the discount rate is a strategy not an accident, retention is an early-alert problem, model the funnel not the headcount, aid leverages enrollment spend it deliberately.
- **2 templates** — enrollment-funnel-model, retention-intervention-plan.
- **2 commands** — `/model-enrollment-funnel`, `/build-retention-plan`.

### Scope & verify-at-use

- **Advisory domain operations knowledge, not legal, financial-aid-compliance, or academic-policy advice.** FERPA-aware — the agents store no student PII and work in cohorts, funnels, and policy, never individual student records.
- All funnel benchmarks (`[ESTIMATE]`), discount-rate norms, yield/melt rates, and retention/persistence/completion metric definitions in `higher-ed-reference-2026.md` are volatile and institution-/system-/accreditor-specific — each carries a retrieval date + `[verify-at-use]`; re-confirm against the institution's own IR definitions, the aid office, and the accreditor before quoting or acting. A metric is meaningless without its definition and source.
