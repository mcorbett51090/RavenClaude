# Changelog — skilled-trades-contracting

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.2.2] — 2026-07-09

### Fixed

- **Advisory anti-pattern hook now fires under Claude Code.** `hooks/flag-skilled-trades-contracting-antipatterns.sh` read the target path only from `$CLAUDE_TOOL_FILE_PATH` (`$1`) — not a real Claude Code hook variable — so under Claude Code it received an empty path and silently no-op'd. Added the canonical stdin-JSON `.tool_input.file_path` fallback so the hook inspects the written file as intended. Advisory-only (no gate/behavior change beyond the hook actually running now). From the 2026-07-09 autonomous repo review (Decision 1).

## [Unreleased] — value-add build-out — 2026-06-05

Non-code-vertical value-add build-out — applies the `veterinary-practice` pilot recipe to skilled-trades contracting. Adds the scenarios bank, two **new, complementary** Mermaid decision-tree knowledge files, a runnable contracting-economics calculator, and cited KPI benchmarks; honestly dispositions the code-runtime tier as N-A. Recommended version bump: **0.1.2 → 0.2.0** (new user-visible surface — scenarios + script + decision trees).

- **Scenarios bank** (`scenarios/`) — new directory + README + **4** dated, scope-tagged engagement scenarios (mirrors the marketplace 9-field schema, `product_version: "n/a"` for a non-code vertical): job-margin erosion via uncaptured change orders, markup-vs-margin pricing correction, dispatch/utilization improvement, overhead-recovery pricing gap. Each carries an "Action for the next consultant" lesson and cited public benchmarks.
- **2 new Mermaid decision-tree knowledge files** that **complement** PR #315's `trades-decision-trees.md` (no duplication — #315 holds the skill/specialist router + post-completion / hiring / price-objection trees):
  - `trades-bid-no-bid-decision-tree.md` — the go/no-go gate before spending estimating hours (capability → client solvency → capacity → win probability → scope), with bid-hit-ratio targets. ConstructConnect/Sunflower-Bank/DowntoBid-cited.
  - `trades-markup-vs-margin-decision-tree.md` — the markup≠margin trap, overhead-before-profit, and `price = cost ÷ (1 − margin)`, with trade gross-margin ranges. Procore/Buildern/Siana/FieldEdge-cited.
- **Runnable calculator** `scripts/trades_calc.py` (stdlib only, Python 3.8+) — four modes: `job-margin` (actual-vs-estimated gross margin + uncaptured-change-order leak), `markup` (target-margin ⇄ applied-markup conversion), `loaded-rate` (wage + burden + overhead ÷ sellable hours with billable-hour efficiency), `overhead-rate` (overhead recovery markup + revenue ratio). Decision-support, not advice. `ruff check` clean; `py_compile` clean; executable.
- **KPI glossary enriched** (`knowledge/trades-kpi-glossary.md`) — added cited, dated benchmark tables (margin/profitability by trade & scope, pricing mechanics incl. the 10-and-10 baseline and markup≠margin, change-orders & bid-hit ratios) plus per-metric formulas and misreads. All trade-association / reputable-contractor-business-cited with retrieval dates and `[verify-at-use]` markers.

### Honestly N-A for a non-code vertical (documented, not forced)
The code-runtime tier (code-aware MCP server, LSP, `bin/`, monitors, output-styles, themes, `settings.json`) is genuinely not applicable to an estimating/field-ops advisory vertical. Each is dispositioned with a one-line reason in `CLAUDE.md` §9 "Value-add completeness (build-out 2026-06-05)". The one runtime item with real non-code value — a runnable calculator — **was** built (`scripts/trades_calc.py`).

### Shared-file changes required (orchestrator-owned, NOT done in this build-out)
- `.repo-layout.json` `allowed_globs` already covers `plugins/*/scenarios/**` and `plugins/*/scripts/**` — confirmed present; no new glob needed.
- `.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json` `version` bump `0.1.2` → `0.2.0`.

## [0.1.x] — PR #315

Consolidated `knowledge/trades-decision-trees.md` (Mermaid trees), the `best-practices/` rule set, and `templates/`.

## [0.2.1] — 2026-06-12

Version bump previously unlogged here (rolls up `0.1.0` → `0.2.1`); the change that set `0.2.1`:

- fix: repo-review fixes — gate tool-absence guard + broken antipattern regex (#422)

## [0.1.0] — initial release

4 agents (`trades-engagement-lead`, `estimating-specialist`, `field-operations-specialist`, `trade-business-analyst`), 5 skills, 3 templates, 5 commands, 1 advisory hook, an 8-rule best-practices set, and a 4-file research-grounded knowledge bank. An estimating-and-field-operations team for an HVAC, electrical, or plumbing contractor.
