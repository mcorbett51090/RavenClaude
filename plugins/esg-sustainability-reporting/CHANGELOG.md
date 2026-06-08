# Changelog — esg-sustainability-reporting

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

## 0.1.0 — 2026-06-08

Initial release. The corporate ESG & sustainability-disclosure layer above the audited ledger, the data
pipeline, and the regulatory filing route.

- **3 agents** — `esg-reporting-architect` (framework selection & scoping: CSRD/ESRS, ISSB IFRS S1/S2, GRI,
  the SEC climate rule, double vs financial materiality, the reporting boundary & governance, the disclosure
  roadmap), `ghg-accounting-analyst` (GHG Protocol Scopes 1/2/3 + the 15 Scope-3 categories, activity data &
  emission factors, location-based vs market-based Scope 2, base year & recalculation, data quality),
  `disclosure-and-assurance-lead` (disclosure drafting, data controls & evidence trail, limited vs reasonable
  assurance readiness, gap assessment, auditor liaison). Each carries the full scenario-authoring frontmatter.
- **3 skills** — `framework-selection-and-materiality`, `ghg-inventory`, `disclosure-and-assurance-readiness`.
- **Knowledge bank** — `esg-sustainability-reporting-decision-trees.md`: Mermaid trees (which-framework-applies,
  which-materiality-test, Scope-3-relevance, location-vs-market Scope 2, target-assurance-level) + a dated 2026
  framework/standard map (ESRS / IFRS S1·S2 / GRI / SEC climate rule / GHG Protocol) (`[verify-at-build]`).
- **8 best-practices**, **3 commands** (`scope-esg-report`, `build-ghg-inventory`, `assess-assurance-readiness`),
  **2 templates** (materiality assessment, GHG inventory report), **1 advisory hook**
  (`check-esg-sustainability-reporting-anti-patterns.sh`; `ESG_STRICT=1` to make it blocking), and a
  **scenarios bank** (2 field notes).
- Seams: financial-statement reporting → `finance`; data lineage/controls → `data-governance-privacy`;
  financial-regulator filing → `regulatory-compliance`. NOT a legal or financial-audit opinion.
  Requires `ravenclaude-core@>=0.7.0`.
