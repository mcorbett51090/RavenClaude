# Changelog — corporate-development-ma

All notable changes to this plugin are documented here. Versioning is semver, bumped
on every user-visible change (mirrored in `.claude-plugin/plugin.json` and the
marketplace catalog entry).

## 0.1.0 — 2026-07-18

Initial release. The buy-side deal team.

- 3 agents: `corpdev-lead`, `ma-diligence-lead`, `integration-pmi-strategist`.
- 4 skills + 4 mirrored commands: `frame-a-deal-thesis`, `triangulate-a-valuation`,
  `run-a-diligence-plan`, `plan-post-merger-integration`.
- 3-file knowledge bank: M&A KPI glossary, valuation & deal economics, and a Mermaid
  decision-tree file (skill/agent router, buy-vs-build/partner, valuation-method
  weighting, go/no-go gate).
- 7 best-practice rules + a best-practices README.
- 2 templates: deal-thesis / IC memo, 100-day integration plan.
- 1 advisory `PostToolUse` hook (`CORPORATE_DEVELOPMENT_MA_STRICT=1` makes it blocking).
- 8 house opinions anchored on thesis-before-model, valuation triangulation, owner/date
  synergies, and pricing integration risk pre-signing.
