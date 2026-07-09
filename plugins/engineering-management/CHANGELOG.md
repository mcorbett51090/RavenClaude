# Changelog — engineering-management

All notable changes to this plugin are documented here. Versioning is semver; bump on every user-visible change (AGENTS.md).

## [0.1.1] — 2026-07-09

### Fixed

- **Advisory anti-pattern hook now fires under Claude Code.** `hooks/flag-engineering-management-antipatterns.sh` read the target path only from `$CLAUDE_TOOL_FILE_PATH` (`$1`) — not a real Claude Code hook variable — so under Claude Code it received an empty path and silently no-op'd. Added the canonical stdin-JSON `.tool_input.file_path` fallback so the hook inspects the written file as intended. Advisory-only (no gate/behavior change beyond the hook actually running now). From the 2026-07-09 autonomous repo review (Decision 1).

## [0.1.0] — 2026-06-09

Initial release.

- **4 agents** — `engineering-manager-lead`, `people-and-growth-manager`, `delivery-and-execution-manager`, `technical-health-manager`, each carrying the full scenario-authoring schema.
- **5 skills + 5 commands** — `run-one-on-one`, `write-performance-review`, `design-hiring-loop`, `improve-team-flow`, `decide-tech-debt`.
- **4-file knowledge bank** — KPI glossary (DORA/flow/people/quality), economics, 2025–2026 frameworks context, and Mermaid decision trees.
- **`scripts/engineering_management_calc.py`** — stdlib calculator: `oncall-load`, `attrition-cost`, `tech-debt`. Decision-support only.
- **4 templates · 8 best-practice rules · scenarios bank · 1 advisory hook**.
