# Changelog — power-platform

All notable changes to the `power-platform` plugin. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions in `.claude-plugin/plugin.json`.

## [Unreleased]

_(Currently aligns with the version pinned in `plugin.json`. Add entries here as PRs land.)_

## [0.6.0] — Pending merge (PR #10)

### Added
- `agents/power-platform-tester.md` — PP-specific tester that spawns AFTER a specialist's change but BEFORE `solution-alm-engineer` packages a release. Covers Test Studio + Monitor (canvas), Manual Test + run-history assertions (flows), plug-in execution order + FLS/RLS + cascade (Dataverse), form/business-rule/command-bar (model-driven), DAX measure-tests + VertiPaq + DAX Studio server-timings (Power BI), `pac solution check` as a gate.
- `hooks/check-house-opinions.sh` — three new mechanically-detectable checks:
  - `premium-connector-no-licensing-note` — premium-connector references without a licensing annotation (§3 #8).
  - `powerfx-var-prefix` / `powerfx-col-prefix` — `Set` / `Collect` / `ClearCollect` whose first arg doesn't follow the `var*` / `col*` convention (§3 #6).
  - `secret-in-env-var` — plaintext-secret-looking defaults in env-variable XML/JSON instead of `@Microsoft.KeyVault(...)` (§4 anti-pattern).

## [0.5.4] — 2026-05-18

### Changed
- External-review polish; CLAUDE.md tightening; minor hook fixes.

## [0.5.0] — 2026-05-08

### Added
- `agents/power-bi-engineer.md` — semantic models, DAX, PBIP git + Azure DevOps integration.
- `skills/power-bi/` — DAX patterns, PBIP structure + git resources.
- `skills/power-automate/` — expressions, solution-aware flows + connection refs, error handling + child flows.
- Bundled community `pbix-mcp` server (d0nk3yhm/pbix-mcp, MIT) for `.pbix`/`.pbit` read/write/DAX-eval without Power BI Desktop.

### Changed
- `solution-alm-engineer` expanded for Azure DevOps git pain points and flows-in-source-control.
- Roster updated to 10 agents; cross-cutting list expanded; grounding checklist + skill mapping updated.
- Added anti-pattern for committing raw `.pbix`.

## [0.1.0] — 2026-04-15

### Added
- Initial release: 9 Power Platform specialist agents (canvas/Power Fx, Power Automate, Dataverse, model-driven apps, pac CLI + ALM, tenant governance/DLP, PCF, Copilot Studio + AI Builder, Power Pages).
- House-opinion checks hook with five initial checks.
- Imported veteran skills.
