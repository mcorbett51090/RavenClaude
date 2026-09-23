# Changelog — platform-engineering-idp

All notable changes to this plugin are documented here. Versioning is semver; bump on every user-visible change (AGENTS.md).

## [0.1.3] — 2026-09-23

Research-sweep **correction** (weekly deep-research sweep, issue #1229), independently re-verified this session via WebSearch before shipping:

- **DORA framework updated.** DORA now publishes **5 metrics** (added deployment rework rate), renamed "MTTR" to **failed deployment recovery time** (regrouped as a throughput metric, not stability), and its **2025 report dropped the elite/high/medium/low tiers** in favor of seven team archetypes. Updated `knowledge/platform-engineering-idp-kpi-glossary.md` (5-metric table), `knowledge/platform-engineering-idp-economics.md` §4 (annotated `classify()` as this team's own house convention, not DORA's current construct), `knowledge/platform-engineering-idp-context.md` (renamed the MTTR directional-frame row, added a dated correction note), and `knowledge/platform-engineering-idp-decision-trees.md` Tree 1 ("four DORA keys" → "the 5 DORA metrics"). **Not done this pass** (explicitly out of `knowledge/` scope per the sweep's own recommendation): `scripts/platform_engineering_idp_calc.py`'s `dora` subcommand, the `classify-dora` skill/command, `templates/scorecard.md`, `best-practices/measure-devex-with-dora-and-lead-time-not-opinions.md`, the two agents that reference bands, and `CLAUDE.md` §3 #3's "four DORA keys" house opinion — these all share the same four-key/four-tier model and need a coordinated `developer-experience-analyst` owner pass, not a knowledge-only patch.

## [0.1.2] — 2026-08-14

### Changed

- Dropped hand-maintained artifact-count literals from the plugin description (D1). The roster enumerates itself; Gate 206 forbids the digit.

## [0.1.1] — 2026-07-09

### Fixed

- **Advisory anti-pattern hook now fires under Claude Code.** `hooks/flag-platform-engineering-idp-antipatterns.sh` read the target path only from `$CLAUDE_TOOL_FILE_PATH` (`$1`) — not a real Claude Code hook variable — so under Claude Code it received an empty path and silently no-op'd. Added the canonical stdin-JSON `.tool_input.file_path` fallback so the hook inspects the written file as intended. Advisory-only (no gate/behavior change beyond the hook actually running now). From the 2026-07-09 autonomous repo review (Decision 1).

## [0.1.0] — 2026-06-08

Initial release.

- **4 agents** — `platform-eng-lead`, `golden-path-architect`, `developer-experience-analyst`, `platform-reliability-specialist`, each carrying the full scenario-authoring schema.
- **5 skills + 5 commands** — `classify-dora`, `measure-adoption`, `design-golden-path`, `quantify-toil`, `set-platform-slos`.
- **4-file knowledge bank** — KPI glossary, unit economics, 2025–2026 context, and Mermaid decision trees.
- **`scripts/platform_engineering_idp_calc.py`** — stdlib calculator: `dora`, `adoption`, `toil`. Decision-support only.
- **4 templates · 8 best-practice rules · scenarios bank · 1 advisory hook**.
