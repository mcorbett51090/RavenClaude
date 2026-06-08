# Changelog — revops

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

## 0.2.0 — 2026-06-08

Depth pass. No new agents or skills (the roster and the three skills are unchanged); this release
deepens the surrounding craft material and adds a runnable calculator.

- **Runnable calculator** — `scripts/revops_calc.py` (stdlib-only, Python 3.8+, `argparse`, ruff-clean
  on `F,E9,B,C4,I,UP`): `forecast` (weighted-by-stage roll-up vs the commit roll-up with the gap named,
  plus a win-rate-derived coverage target vs the coverage the pipeline actually provides), `funnel`
  (stage-to-stage + cumulative conversion, win-rate, and the sales-velocity equation), `quota-capacity`
  (bottoms-up capacity = (ramped + ramping × ramp-fraction) × productivity, reconciled against the board
  target). A **calculator, not a data source** — the user supplies every input; outputs are
  decision-support and a stage rate is a hypothesis until back-tested.
- **12 best-practices** (was 8) — added `funnel-is-a-bowtie`, `stage-is-exit-criteria-not-vibes`,
  `quota-is-bottoms-up-from-capacity`, `the-build-belongs-to-the-system-layer`; index reconciled.
- **Knowledge bank → 5 Mermaid trees** — forecast-method selection, coverage derivation,
  attribution-model choice, funnel-stage definition, and quota-reconciles-to-capacity, plus the dated
  2026 reference map (last reviewed 2026-06-08).
- **Scenarios bank → 5 field notes** (was 2) — added last-touch-defunds-demand (attribution),
  quota-from-the-board-number (capacity/comp behavior), crm-garbage-corrupts-routing
  (data-quality/routing). All `reviewed: false`, 9-field schema; index updated.
- No migration impact — additive only. Requires `ravenclaude-core@>=0.7.0`.

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
