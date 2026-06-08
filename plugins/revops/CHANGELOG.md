# Changelog — revops

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

## 0.1.0 — 2026-06-08

Initial release. The lead-to-cash revenue-operations (RevOps) layer above the CRM and warehouse systems.

- **3 agents** — `revops-architect` (the lead-to-cash funnel + bowtie, the RevOps data model, the GTM tech stack,
  marketing↔sales↔CS SLAs), `pipeline-and-forecast-analyst` (stage hygiene, forecast methodology — weighted vs commit/category
  vs AI, coverage derived from win-rate, sales velocity, deal inspection), `gtm-systems-engineer` (CRM hygiene & automation,
  lead routing & scoring, territory/quota/comp ops, attribution modeling, data quality). Each carries the full
  scenario-authoring frontmatter.
- **3 skills** — `funnel-and-revops-data-model`, `forecast-methodology`, `pipeline-hygiene-and-routing`.
- **Knowledge bank** — `revops-decision-trees.md`: Mermaid trees (forecast-method selection, coverage derivation,
  attribution-model choice, funnel-stage definition) + a dated 2026 reference map (funnel glossary, forecast methods,
  attribution models, comp/quota mechanics) (`[verify-at-build]`).
- **8 best-practices**, **3 commands** (`define-funnel`, `build-forecast`, `audit-pipeline-hygiene`),
  **2 templates** (funnel-and-data-model brief, forecast-and-pipeline spec), **1 advisory hook**
  (`check-revops-anti-patterns.sh`; `REVOPS_STRICT=1` to make it blocking), and a **scenarios bank** (2 field notes).
- Seams: post-sale health → `customer-success-analytics`; CRM build → `salesforce`; warehouse/BI → `data-platform` /
  `tableau`; experiments → `experimentation-growth-engineering`; significance → `applied-statistics`. Requires
  `ravenclaude-core@>=0.7.0`.
