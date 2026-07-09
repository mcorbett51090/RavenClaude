# Changelog — accessibility-engineering

All notable changes to this plugin are documented here. Versioning is semver; bump on every user-visible change (AGENTS.md).

## [0.1.2] — 2026-07-09

### Fixed

- **Advisory anti-pattern hook now fires under Claude Code.** `hooks/flag-accessibility-engineering-antipatterns.sh` read the target path only from `$CLAUDE_TOOL_FILE_PATH` (`$1`) — not a real Claude Code hook variable — so under Claude Code it received an empty path and silently no-op'd. Added the canonical stdin-JSON `.tool_input.file_path` fallback so the hook inspects the written file as intended. Advisory-only (no gate/behavior change beyond the hook actually running now). From the 2026-07-09 autonomous repo review (Decision 1).

## [0.1.1] — 2026-06-24

### Added

- **European Accessibility Act (EAA) as a named, dated regulatory driver.** The EAA (Directive (EU) 2019/882) has applied since **28 June 2025**, making accessibility a hard EU-market gate for in-scope consumer products/services, with **EN 301 549 (v3.2.1) → WCAG 2.1 AA** as the presumptive standard and a transition tail to 2030 for some existing services. Added a "Regulatory drivers (dated)" subsection to `knowledge/accessibility-engineering-context.md` (marked `[unverified — training knowledge]` per the file's convention) and a brief pointer in `CLAUDE.md` house opinion #6, so "is this in EU-market scope?" becomes a standard intake question. Liability/scope determinations still route to qualified counsel (§2, §3 #6). Dates verified 2026-06-24.

## [0.1.0] — 2026-06-08

Initial release.

- **4 agents** — `accessibility-lead`, `wcag-audit-analyst`, `assistive-tech-testing-specialist`, `inclusive-design-strategist`, each carrying the full scenario-authoring schema.
- **5 skills + 5 commands** — `run-wcag-audit`, `prioritize-remediation`, `test-assistive-tech`, `verify-contrast`, `design-accessible-pattern`.
- **4-file knowledge bank** — KPI glossary, unit economics, 2025–2026 context, and Mermaid decision trees.
- **`scripts/accessibility_calc.py`** — stdlib calculator: `conformance`, `remediation`, `contrast`. Decision-support only.
- **4 templates · 8 best-practice rules · scenarios bank · 1 advisory hook**.
