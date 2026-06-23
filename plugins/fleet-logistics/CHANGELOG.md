# Changelog — fleet-logistics

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.2.1] — 2026-06-12

Version bump previously unlogged here; the change that set `0.2.1`:

- fix: repo-review fixes — gate tool-absence guard + broken antipattern regex (#422)

## [0.2.0] — 2026-06-05

Value-add build-out — applies the marketplace's non-code-vertical recipe (proven by the `veterinary-practice` pilot) to fleet & logistics. Adds the scenarios bank, two new Mermaid decision-tree knowledge files, and a runnable fleet-economics calculator; honestly dispositions the code-runtime tier as N-A. Builds **on top of** PR #315's consolidated knowledge (the three in-file Mermaid trees, best-practices/, templates/) — net-new, no duplication.

- **Scenarios bank** (`scenarios/`) — new directory + README + **4** dated, scope-tagged engagement scenarios (mirrors the marketplace 9-field schema, `product_version: "n/a"` for a non-code vertical): cost-per-mile creep + deadhead leak, PM-deferral breakdown spiral, driver-turnover bleed, HOS/ELD compliance gap. Each carries an "Action for the next consultant" lesson and cited public benchmarks (ATRI 2025, FMCSA, driver-turnover snapshots, PM-vs-reactive cost studies).
- **2 new Mermaid decision-tree knowledge files** (complement the three trees PR #315 added inside `fleet-decision-trees.md` — lane-thin, replacement-timing, spot-vs-contract):
  - `fleet-lease-vs-buy-vs-rent-decision-tree.md` — how the next unit comes in (utilization + capital + duration + maintenance-appetite trade; TCO-not-monthly-payment arithmetic). KPMG/Ryder + Penske + ATRI-cited.
  - `fleet-in-house-vs-3pl-decision-tree.md` — make-vs-buy for transportation capacity: private fleet vs. dedicated vs. 3PL/for-hire (volume + lane-stability + service + capital-bandwidth trade; fixed-vs-variable cost test). RXO/Jones/Transforce/Trinity-cited.
- **Runnable calculator** `scripts/fleet_calc.py` (stdlib only, Python 3.8+, ruff-clean) — four modes: `cost-per-mile` (build all-in CPM bottom-up + margin vs. a rate), `deadhead` (empty-mile leak + backhaul prize), `replace-repair` (keep-vs-replace per-mile crossover incl. downtime), `turnover` (annual driver-turnover cost + retention prize). Decision-support, not advice; the user supplies every input.

### Honestly N-A for a non-code vertical (documented, not forced)
The code-runtime tier (code-aware MCP server, LSP, `bin/`, monitors, output-styles, themes, `settings.json`) is genuinely not applicable to a fleet-operations advisory vertical. Each is dispositioned with a one-line reason in `CLAUDE.md` § "Value-add completeness (build-out 2026-06-05)". Telematics/ELD/TMS systems are per-tenant, authenticated, and PII/safety-bearing — bundling an MCP is out of scope and the plugin is deliberately TMS/ELD-neutral (§2). The one runtime item with real non-code value — a runnable calculator — **was** built (`scripts/fleet_calc.py`).

### Shared-file changes (orchestrator-owned, NOT done here)
- `.repo-layout.json` `allowed_globs` already cover `plugins/*/scenarios/**`, `plugins/*/scripts/**`, `plugins/*/knowledge/**`, and `plugins/*/CHANGELOG.md` — confirmed; no new globs required.
- `.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json` `version` bump `0.1.2` → `0.2.0` (plugin.json bumped here; marketplace.json mirror is orchestrator-owned).

## [0.1.0] — initial release

4 agents (`fleet-engagement-lead`, `dispatch-routing-specialist`, `fleet-maintenance-specialist`, `logistics-cost-analyst`), 5 skills, 3 templates, 5 commands, 1 advisory hook, an 8-rule best-practices set, and a 4-file research-grounded knowledge bank. A fleet-operations team for a carrier, private fleet, or last-mile operator anchored on cost-per-mile and the operating ratio.
