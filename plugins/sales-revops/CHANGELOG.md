# Changelog — sales-revops

All notable changes to this plugin are documented here. Versioning is semver; bump on every user-visible change (AGENTS.md).

## [0.1.1] — 2026-07-09

### Fixed

- **Advisory anti-pattern hook now fires under Claude Code.** `hooks/flag-sales-revops-antipatterns.sh` read the target path only from `$CLAUDE_TOOL_FILE_PATH` (`$1`) — not a real Claude Code hook variable — so under Claude Code it received an empty path and silently no-op'd. Added the canonical stdin-JSON `.tool_input.file_path` fallback so the hook inspects the written file as intended. Advisory-only (no gate/behavior change beyond the hook actually running now). From the 2026-07-09 autonomous repo review (Decision 1).

## [0.1.0] — 2026-06-08

Initial release.

- **4 agents** — `revops-lead`, `pipeline-forecast-analyst`, `funnel-conversion-strategist`, `quota-territory-architect`, each carrying the full scenario-authoring schema.
- **5 skills + 5 commands** — `build-forecast`, `read-pipeline-coverage`, `diagnose-funnel`, `model-velocity`, `design-quota`.
- **4-file knowledge bank** — KPI glossary, unit economics, 2025–2026 context, and Mermaid decision trees.
- **`scripts/revops_calc.py`** — stdlib calculator: `coverage`, `forecast`, `funnel`, `velocity`, `quota-capacity`. Decision-support only.
- **4 templates · 8 best-practice rules · scenarios bank · 1 advisory hook**.
