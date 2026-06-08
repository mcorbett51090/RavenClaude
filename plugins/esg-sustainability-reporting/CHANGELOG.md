# Changelog — esg-sustainability-reporting

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

## 0.2.0 — 2026-06-08

Depth build-out to the v0.2.0 standard. No agent/skill/command count change; deeper enforcement
surface, a runnable calculator, and a fuller scenarios bank.

- **Runnable calculator** — `scripts/ghg_calc.py` (stdlib only, Python 3.8+; ruff-clean F,E9,B,C4,I,UP).
  Three subcommands: `scope2` (dual location-based vs market-based Scope 2 from kWh × user-supplied
  factors, with repeatable market instruments and a residual-grid fallback — neither figure silently
  dropped), `inventory` (sum activity × factor across scopes from a CSV, with a Scope-3 category
  breakdown, per-scope shares, and a data-quality-tier mix), and `intensity` (emissions per
  revenue/output, flagged as a ratio not a reduction). **Every emission factor is a user-supplied
  input** — the tool ships no factor library, no benchmarks, no grid intensities.
- **12 best-practices** (the description previously undercounted these as 8) — the always-on priors
  the agents cite by filename; `best-practices/README.md` indexes all twelve.
- **Knowledge bank** — 5 Mermaid decision trees (which-framework, which-materiality-test,
  Scope-3-relevance, location-vs-market Scope 2, target-assurance-level) plus the dated 2026
  framework/standard map (`[verify-at-build]`).
- **Scenarios bank → 5 dated field notes** (9-field schema, `reviewed: false`): added
  `base-year-drift-broke-the-trend` and `assurance-bar-set-too-late`, and indexed the previously
  un-indexed `scope-3-cherry-picked-categories`; `scenarios/README.md` now lists all five.
- Seams, scope, and hand-offs unchanged. NOT a legal or financial-audit opinion.
  Requires `ravenclaude-core@>=0.7.0`.

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
