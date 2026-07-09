# Changelog — precision-agriculture

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.2.3] — 2026-07-09

### Fixed

- **Advisory anti-pattern hook now fires under Claude Code.** `hooks/flag-precision-agriculture-antipatterns.sh` read the target path only from `$CLAUDE_TOOL_FILE_PATH` (`$1`) — not a real Claude Code hook variable — so under Claude Code it received an empty path and silently no-op'd. Added the canonical stdin-JSON `.tool_input.file_path` fallback so the hook inspects the written file as intended. Advisory-only (no gate/behavior change beyond the hook actually running now). From the 2026-07-09 autonomous repo review (Decision 1).

## [0.2.2] — 2026-06-12

Version bump previously unlogged here (rolls up `0.2.0` → `0.2.2`); the change that set `0.2.2`:

- fix: repo-review fixes — gate tool-absence guard + broken antipattern regex (#422)

## [0.2.0] — 2026-06-05

Value-add build-out for a **pure non-code vertical** (precision ag / farm operations & agronomy analytics). Completes the scenarios bank, adds two standalone Mermaid decision-tree knowledge files and a runnable farm-economics calculator, and honestly dispositions the code-runtime tier as N-A. Builds on PR #315 (which added the consolidated knowledge decision-trees, `best-practices/`, `templates/`, and the scenarios `README.md`).

- **Scenarios bank completed** (`scenarios/`) — PR #315's `README.md` + first scenario (breakeven-vs-input-cost-spike) is now backed by **4 new** dated, scope-tagged engagement scenarios (mirrors the marketplace 9-field schema, `product_version: "n/a"` for a non-code vertical): VRT/seeding-rate ROI, nutrient-budget overspend, irrigation water cost (segment-specific — irrigated growers), imagery/scouting false alarm. Each carries an "Action for the next consultant" lesson and cited public benchmarks (extension / ERS / farmdoc). The README's "What's in this bank" table now matches the files on disk.
- **2 new standalone Mermaid decision-tree knowledge files** (complementing #315's 3 in-file trees — input-rate, yield-shortfall, market-now-vs-store):
  - `ag-adopt-precision-tech-roi-decision-tree.md` — adopt a precision-tech tool vs. defer: prove-the-problem-and-cheap-levers-first, validate variability, the per-acre ROI gate at *this operation's* costs, and measure-don't-assume (check strip / control / ground-truth). ERS/extension-cited.
  - `ag-vrt-vs-uniform-seeding-decision-tree.md` — variable-rate vs. uniform seeding rate as a field-variability + return-to-seed trade, with the RTS arithmetic and a mandatory uniform check strip. OSU/Illinois/Iowa-State-cited.
- **Runnable calculator** `scripts/ag_calc.py` (stdlib only, Python 3.8+, ruff-clean) — three modes: `breakeven` (per-field breakeven price + breakeven yield + margin + underwater flag), `vrt-roi` (VR-vs-uniform return-to-seed delta net of prescription cost + breakeven yield lift), `input-cost` (per-acre input-cost stack with shares + economic-optimum check on the last input unit). Decision-support, not advice; sets no application rates (§2). Supplies the `scripts/ag_calc.py` the #315 breakeven + VRT scenarios already referenced.
- **CLAUDE.md** — added §8 (scenarios bank & runnable tooling), §9 (Value-add completeness build-out table), the two new knowledge-bank rows in §5, and a §10 v0.2.0 milestone.

### Honestly N-A for a non-code vertical (documented, not forced)
The code-runtime tier (code-aware MCP server, LSP, `bin/`, monitors, output-styles, themes, `settings.json`) is genuinely not applicable to a farm-operations advisory vertical. Each is dispositioned with a one-line reason in `CLAUDE.md` § "Value-add completeness (build-out 2026-06-05)". FMS/telematics MCP (John Deere Ops Center, Climate FieldView, agX) are per-tenant/authenticated/billed → *recommend / evaluate-first*, never bundled (per `docs/best-practices/bundled-mcp-servers.md`); none fabricated. The one runtime item with real non-code value — a runnable calculator — **was** built (`scripts/ag_calc.py`).

### Shared-file changes required (orchestrator-owned, NOT done here)
- `.claude-plugin/marketplace.json` `version` bump `0.1.2` → `0.2.0` (mirror of `.claude-plugin/plugin.json`).
- `.repo-layout.json` `allowed_globs` already cover `plugins/*/scenarios/**`, `plugins/*/scripts/**`, and `plugins/*/CHANGELOG.md` — no glob change needed (confirmed 2026-06-05).

## [0.1.0] — initial release

4 agents (`agronomy-engagement-lead`, `crop-agronomist`, `farm-operations-analyst`, `ag-market-analyst`), 5 skills, 3 templates, 5 commands, 1 advisory hook, an 8-rule best-practices set, and a 4-file research-grounded knowledge bank. An agronomy-and-farm-operations team for a grower, farm manager, or ag retailer.
