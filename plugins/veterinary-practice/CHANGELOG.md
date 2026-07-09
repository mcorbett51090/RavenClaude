# Changelog — veterinary-practice

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.2.3] — 2026-07-09

### Fixed

- **Advisory anti-pattern hook now fires under Claude Code.** `hooks/flag-veterinary-practice-antipatterns.sh` read the target path only from `$CLAUDE_TOOL_FILE_PATH` (`$1`) — not a real Claude Code hook variable — so under Claude Code it received an empty path and silently no-op'd. Added the canonical stdin-JSON `.tool_input.file_path` fallback so the hook inspects the written file as intended. Advisory-only (no gate/behavior change beyond the hook actually running now). From the 2026-07-09 autonomous repo review (Decision 1).

## [0.2.2] — 2026-06-12

Version bump previously unlogged here (rolls up `0.2.0` → `0.2.2`); the change that set `0.2.2`:

- fix: repo-review fixes — gate tool-absence guard + broken antipattern regex (#422)

## [0.2.0] — 2026-06-05

Value-add build-out — the pilot proving the marketplace recipe generalizes to a **pure non-code vertical**. Adds the scenarios bank, two Mermaid decision-tree knowledge files, a runnable practice-economics calculator, and cited KPI benchmarks; honestly dispositions the code-runtime tier as N-A.

- **Scenarios bank** (`scenarios/`) — new directory + README + **4** dated, scope-tagged engagement scenarios (mirrors the marketplace 9-field schema, `product_version: "n/a"` for a non-code vertical): exam-room throughput bottleneck, controlled-substance log gap, inventory shrink reduction, associate-DVM ROI model. Each carries an "Action for the next consultant" lesson and cited public benchmarks.
- **2 new Mermaid decision-tree knowledge files** (the plugin previously had zero):
  - `vet-add-associate-vs-extend-capacity-decision-tree.md` — add an associate DVM vs. extend hours vs. fix the template, cheap-levers-first, with the production-threshold gate table and the ROI J-curve. AAHA/AVMA/dvm360-cited.
  - `vet-in-house-vs-send-out-lab-decision-tree.md` — in-house analyzer vs. reference lab as a volume + turnaround + clinical-value trade (usually hybrid), with the breakeven arithmetic. Vet-Advantage/Safepath/VPN-cited.
- **Runnable calculator** `scripts/vet_calc.py` (stdlib only, Python 3.8+) — three modes: `associate-roi` (hiring J-curve: monthly trough + breakeven month), `lab-breakeven` (in-house vs send-out volume breakeven + verdict), `wellness-margin` (plan-tier monthly margin + underwater redemption rate). Decision-support, not advice.
- **KPI glossary enriched** (`knowledge/vet-kpi-glossary.md`) — added cited, dated benchmark tables (revenue/FTE, invoice & new-client thresholds, staffing ratio, credentialed-tech revenue lift, net-margin range, inventory turns) plus a PIMS-landscape context section (Cornerstone, Avimark/ImproMed, ezyVet, Pulse, …). All AAHA/AVMA/trade-cited with retrieval dates.

### Honestly N-A for a non-code vertical (documented, not forced)
The code-runtime tier (code-aware MCP server, LSP, `bin/`, monitors, output-styles, themes, `settings.json`) is genuinely not applicable to a practice-operations advisory vertical. Each is dispositioned with a one-line reason in `CLAUDE.md` § "Value-add completeness (pilot build-out 2026-06-05)". The one runtime item with real non-code value — a runnable calculator — **was** built (`scripts/vet_calc.py`).

### Shared-file changes required (orchestrator-owned, NOT done here)
- `.repo-layout.json` `allowed_globs` must add `plugins/*/scenarios/**` and `plugins/*/scripts/**` (both already exist for other plugins; confirm coverage).
- `.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json` `version` bump `0.1.0` → `0.2.0`.

## [0.1.0] — initial release

4 agents (`vet-practice-lead`, `clinical-protocol-specialist`, `practice-operations-manager`, `vet-finance-analyst`), 5 skills, 3 templates, 5 commands, 1 advisory hook, an 8-rule best-practices set, and a 4-file research-grounded knowledge bank. A clinical-and-practice-management team for a veterinary hospital owner or medical director.
