# Changelog — accessibility-engineering

All notable changes to this plugin are documented here. Versioning is semver; bump on every user-visible change (AGENTS.md).

## [0.1.5] — 2026-11-05

### Added

- **Settings and choice controls contract.** `knowledge/settings-controls-markup-and-keyboard-2026-11.md`: per-control markup, keys, name and state for switch, segmented control / radio tiles, slider, tooltip, toggletip, sheet, usage meter and save status; WCAG 2.5.7 (AA), 1.4.13 (AA) and 2.5.8 as they land on these controls; an audit-result table; a keyboard-then-screen-reader test script. Rows are tagged `[docs-verified 2026-11-05]` (APG, WCAG 2.2 Understanding, MDN, GOV.UK, Inclusive Components), `[inference]` or `[unverified]`. Native checkbox `switch` is experimental; the Understanding page for 2.5.7 is silent on native ranges; APG's tooltip page is work in progress. Separate from the 2026-11-04 capture and re-grades nothing in it. Also covers the Connect apps flow (scope tiles, removable pills, Advanced disclosure, static "Required" tile, multi-step authorize sheet, per-connector account list). Wired through `CLAUDE.md` §3c and `design-accessible-pattern` Step 7. No assistive-technology session produced it.

## [0.1.4] — 2026-11-04

### Added

- **Portal chrome and coding-agent accessibility standing bar.** `knowledge/portal-and-agent-accessibility-2026-11.md` records the 2026-11-04 capture as rules agents follow. Solid: persistent labeled left rail, current location (without an "exactly one `aria-current`" requirement), disclosure buttons with `aria-expanded` and `aria-controls` rather than `role="menu"`, quieter local nav. Provisional: WCAG 2.3.3 is AAA, and the coding-agent practice list (semantic names, stable hooks, URL state, confirm-before-destructive, page content untrusted). Unverified and not implemented from this note: WebMCP / `navigator.modelContext`, hosted MCP on Cloudflare, `llms.txt` as a gate, Cursor `.mdc` claims, Storybook MCP coverage of Astro. Evidence grades and the discarded claims live in `ux-research`'s `ui-pattern-standing-bar-2026-11.md`. `design-accessible-pattern`, `test-assistive-tech`, and `run-wcag-audit` now point at the file. The 109-claim extract is not in this repo and is not reconstructed.

## [0.1.3] — 2026-08-14

### Changed

- Dropped hand-maintained artifact-count literals from the plugin description (D1). The roster enumerates itself; Gate 206 forbids the digit.

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
