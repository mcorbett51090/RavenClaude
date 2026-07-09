# Changelog — restaurant-operations

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.3.2] — 2026-07-09

### Fixed

- **Advisory anti-pattern hook now fires under Claude Code.** `hooks/flag-restaurant-operations-antipatterns.sh` read the target path only from `$CLAUDE_TOOL_FILE_PATH` (`$1`) — not a real Claude Code hook variable — so under Claude Code it received an empty path and silently no-op'd. Added the canonical stdin-JSON `.tool_input.file_path` fallback so the hook inspects the written file as intended. Advisory-only (no gate/behavior change beyond the hook actually running now). From the 2026-07-09 autonomous repo review (Decision 1).

## [0.3.1] — 2026-06-12

Version bump previously unlogged here (rolls up `0.2.0` → `0.3.1`); the change that set `0.3.1`:

- fix: repo-review fixes — gate tool-absence guard + broken antipattern regex (#422)

## [0.2.0] — 2026-06-05

Value-add build-out mirroring the `veterinary-practice` non-code-vertical recipe. Adds the scenarios bank, two Mermaid decision-tree knowledge files, a runnable four-wall calculator, and cited KPI benchmarks; honestly dispositions the code-runtime tier as N-A.

- **Scenarios bank** (`scenarios/`) — **4** dated, scope-tagged engagement scenarios (mirrors the marketplace 9-field schema, `product_version: "n/a"` for a non-code vertical): prime-cost blowout (food-control gap, not pricing), menu re-priced on percentage instead of contribution-margin dollars, labor flat against demand (mis-allocated across dayparts), inventory/waste shrink on a multi-unit laggard. Each carries an "Action for the next consultant" lesson and cited public benchmarks. (The `scenarios/README.md` was pre-staged in v0.1.x; this release fills in the four narratives it indexes.)
- **2 new Mermaid decision-tree knowledge files** (the plugin previously had zero Mermaid trees — the existing `restaurant-decision-trees.md` is a prose router):
  - `restaurant-menu-action-decision-tree.md` — raise price vs. re-engineer the mix vs. cut the item, matrix-first and resist-the-price-cut, with the contribution-margin and 70%×(1/N) Kasavana-Smith popularity arithmetic. Toast/meez/Apicbase-cited.
  - `restaurant-make-vs-buy-decision-tree.md` — make from scratch vs. buy prepped as a fully-loaded cost + capacity + consistency + brand trade (usually hybrid), with the prep-labor breakeven term most operators omit. Modern Restaurant Management/RestaurantOwner/McDonald Paper-cited.
- **Runnable calculator** `scripts/restaurant_calc.py` (stdlib only, Python 3.8+) — four modes: `prime-cost` (food/labor/prime % vs segment bands + which-half read), `menu-item` (engineering-matrix quadrant from CM dollars + popularity threshold), `make-vs-buy` (fully-loaded scratch cost incl. the prep-labor term vs prepped price, per-unit + monthly verdict), `price-change` (contribution-dollar breakeven for a price move). Decision-support, not advice.
- **KPI glossary enriched** (`knowledge/restaurant-kpi-glossary.md`) — rewritten with cited, dated benchmark bands (prime/food/labor by QSR vs full-service), throughput formulas (SPLH, table turns, RevPASH with a worked example), the menu-mix popularity threshold, and contribution-margin profit metrics. All 7shifts/Toast/VantaInsights/TouchBistro/Apicbase-cited with retrieval dates.

### Honestly N-A for a non-code vertical (documented, not forced)
The code-runtime tier (code-aware MCP server, LSP, `bin/`, monitors, output-styles, themes, `settings.json`) is genuinely not applicable to a restaurant-operations advisory vertical. Each is dispositioned with a one-line reason in `CLAUDE.md` § "9. Value-add completeness (build-out 2026-06-05)". The one runtime item with real non-code value — a runnable calculator — **was** built (`scripts/restaurant_calc.py`).

### Shared-file changes required (orchestrator-owned, NOT done here)
- `.repo-layout.json` `allowed_globs` must cover `plugins/*/scenarios/**` and `plugins/*/scripts/**` (both already exist for other plugins; confirm coverage).
- `.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json` `version` bump `0.1.0` → `0.2.0`.

## [0.1.0] — initial release

4 agents (`restaurant-engagement-lead`, `menu-cost-engineer`, `foh-boh-operations-specialist`, `restaurant-finance-analyst`), 5 skills, 3 templates, 5 commands, 1 advisory hook, an 8-rule best-practices set, and a 4-file research-grounded knowledge bank. An operations-and-unit-economics team for an independent or multi-unit restaurant operator.
