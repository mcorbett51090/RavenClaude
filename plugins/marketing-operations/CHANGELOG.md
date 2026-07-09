# Changelog — marketing-operations

All notable changes to this plugin are documented here. Versioning is semver; bump on every user-visible change (AGENTS.md).

## [0.2.1] — 2026-07-09

### Fixed

- **Advisory anti-pattern hook now fires under Claude Code.** `hooks/flag-marketing-operations-antipatterns.sh` read the target path only from `$CLAUDE_TOOL_FILE_PATH` (`$1`) — not a real Claude Code hook variable — so under Claude Code it received an empty path and silently no-op'd. Added the canonical stdin-JSON `.tool_input.file_path` fallback so the hook inspects the written file as intended. Advisory-only (no gate/behavior change beyond the hook actually running now). From the 2026-07-09 autonomous repo review (Decision 1).

## [0.2.0] — 2026-06-22

Execution value-add: content-marketing engine. No agents added; all existing files unchanged.

- **+1 skill** — `content-engine` (intent briefs, topic clusters/pillar pages, distribution, leading-vs-lagging measurement). Now **6 skills**.
- **+1 knowledge doc** — `knowledge/content-marketing-engine.md` (1 Mermaid decision tree). Now a **5-file knowledge bank**.
- **+2 best-practice rules** — `brief-every-piece-against-a-search-intent`, `build-topic-clusters-not-orphan-posts`. Now **10 rules**.

## [0.1.0] — 2026-06-08

Initial release.

- **4 agents** — `marketing-ops-lead`, `demand-gen-funnel-analyst`, `attribution-analytics-specialist`, `martech-campaign-architect`, each carrying the full scenario-authoring schema.
- **5 skills + 5 commands** — `diagnose-funnel`, `size-demand`, `read-cac-ltv`, `evaluate-channel-mix`, `audit-attribution-data`.
- **4-file knowledge bank** — KPI glossary, unit economics, 2025–2026 context, and Mermaid decision trees.
- **`scripts/marketingops_calc.py`** — stdlib calculator: `funnel`, `cac-ltv`, `channel-roi`. Decision-support only.
- **4 templates · 8 best-practice rules · scenarios bank · 1 advisory hook**.
