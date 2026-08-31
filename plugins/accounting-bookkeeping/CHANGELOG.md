# Changelog — accounting-bookkeeping

All notable changes to this plugin are documented here. Versioning is semver; bump on every user-visible change (AGENTS.md).

## [0.2.2] — 2026-08-14

### Changed

- Dropped hand-maintained artifact-count literals from the plugin description (D1). The roster enumerates itself; Gate 206 forbids the digit.

## [0.2.1] — 2026-07-09

### Fixed

- **Advisory anti-pattern hook now fires under Claude Code.** `hooks/flag-accounting-bookkeeping-antipatterns.sh` read the target path only from `$CLAUDE_TOOL_FILE_PATH` (`$1`) — not a real Claude Code hook variable — so under Claude Code it received an empty path and silently no-op'd. Added the canonical stdin-JSON `.tool_input.file_path` fallback so the hook inspects the written file as intended. Advisory-only (no gate/behavior change beyond the hook actually running now). From the 2026-07-09 autonomous repo review (Decision 1).

## [0.2.0] — 2026-07-06

Scope clarification (docs-only; no agent/skill behavior change) — adds a **§0 scope-boundary** section to `CLAUDE.md` disambiguating this plugin from the `finance` plugin's controller-autopilot, ending the close/reconciliation/segregation-of-duties double-routing overlap. `accounting-bookkeeping` is now explicitly the **SMB multi-client practice-operations** lane (advisory diagnosis + readouts across a client portfolio); the **governed, audit-grade close-to-report cycle** — GAAP statement production, the enforced review→approve→lock workflow, GL↔subledger auto-match, finance-shaped ELT, and multi-entity consolidation — routes to the `finance` controller-autopilot (v0.16.0). Decoupled follow-on from the FORGE `financial-controller-autopilot` plan.

## [0.1.0] — 2026-06-08

Initial release.

- **4 agents** — `accounting-practice-lead`, `close-cycle-analyst`, `ap-ar-cashflow-specialist`, `reconciliation-controls-specialist`, each carrying the full scenario-authoring schema.
- **5 skills + 5 commands** — `run-close`, `reconcile-accounts`, `read-working-capital`, `estimate-bad-debt`, `audit-controls`.
- **4-file knowledge bank** — KPI glossary, unit economics, 2025–2026 context, and Mermaid decision trees.
- **`scripts/acctgops_calc.py`** — stdlib calculator: `working-capital`, `aging`, `close-cycle`. Decision-support only.
- **4 templates · 8 best-practice rules · scenarios bank · 1 advisory hook**.
