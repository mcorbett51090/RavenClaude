# Changelog — customer-success-analytics

All notable changes to this plugin. Versions are semver; bump on every user-visible change.

## 0.2.0 — 2026-06-05

Value-add build-out on top of PR #315's consolidated decision-trees + best-practices.

### Added

- **Scenarios bank** (`scenarios/`) — README + 5 dated, scope-tagged, unverified engagement field notes: health-score-not-predicting-churn (lagging-signal audit), nrr-masking-logo-churn (GRR floor), renewal-forecast-miss-single-thread, false-positive-risk-tier-segment (segment override), and usage-data-identity-gap (the `data-platform` identity-resolution seam). Wired into the marketplace scenario-retrieval pattern (unverified-scenario preamble required).
- **Knowledge — retention metrics** (`knowledge/cs-retention-metrics.md`) — NRR/GRR/CAC-payback definitions + 2025 SaaS benchmarks (cited, dated, `[verify-at-use]`-marked), plus **2 new Mermaid decision trees**: retention-metric-choice (NRR vs GRR vs both) and renewal-forecast-confidence.
- **Knowledge — risk-tier escalation tree** (`knowledge/cs-risk-tier-escalation-decision-tree.md`) — a Mermaid tree for *which save motion fires* when an account is Red or a fast-trigger fires (the action complement to #315's classification trees), enforcing freshness-before-alarm and DM-confirmation gates.
- **Runnable calculator** (`scripts/cs_calc.py`) — stdlib-only, ruff-clean: `retention` (NRR/GRR + the expansion-gap masking check), `health-score` (transparent weighted composite + per-signal contribution + lagging-share flag + tier), `renewal-risk` (proximity × engagement). Calculator, not a data source.
- **Template** (`templates/health-tier-design-worksheet.md`) — the fillable output of the `health-tier-design` skill: signal selection (5–7, leading/lagging), the tier rule expression, the weighting/contribution check (drives `cs_calc.py`), the explainability contract, validation gates, and the data-platform handoff table.

### Notes

- Bundled MCP/LSP, `bin/`, monitors, output-styles, settings/themes dispositioned **N-A** with reasons in CLAUDE.md §"Value-add completeness (build-out 2026-06-05)" — CS platforms are per-tenant credentialed (recommend-not-bundle), and there is no code-runtime surface to instrument.
- No new agent (team-growth-as-knowledge house rule); the calculator + trees + template extend reach without a fifth agent.

## 0.1.x

- Initial release + PR #315: 2 agents, 5 skills, 20 best-practice rules, consolidated `customer-success-decision-trees.md`, 2-doc knowledge bank, 4 templates.
