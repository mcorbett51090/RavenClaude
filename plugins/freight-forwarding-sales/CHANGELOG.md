# Changelog — freight-forwarding-sales

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.2.0] — 2026-06-05

Value-add build-out against the full marketplace menu, mirroring the merged `veterinary-practice` non-code-vertical recipe (scenarios + decision trees + the "## Value-add completeness" disposition table + CHANGELOG). The plugin already shipped a rich surface (6 agents, 6 skills, 6 commands, 22 best-practices, a 2-doc knowledge bank, and `scripts/freight_calc.py`); this round fills the two genuine net-new gaps and dispositions every menu item honestly.

- **Scenarios bank materialized** (`scenarios/`) — the README index existed but the 4 scenario files did not. Added all **4** dated, scope-tagged, web-researched engagement narratives (marketplace 9-field schema, `product_version: "n/a"` for a non-code vertical): quote-margin erosion under surcharge volatility, RFQ/tender qualify-or-decline + win-rate, mode-shift air-vs-ocean against a deadline, key-account QBR/retention. Each carries an "Action for the next consultant" lesson and cited, dated public sources; volatile figures marked `[verify-at-use]` / `[example — confirm against your live rates]`.
- **2 new Mermaid decision trees** appended to `knowledge/freight-sales-decision-trees.md` (previously 8 trees; now 10), both **complementing** the existing urgency-first Mode-selection tree rather than duplicating it:
  - **LCL vs FCL** — the ocean-only volume/cost crossover (~13–15 CBM breakeven band) the Mode-selection tree only points at, with a fragile/hazardous-cargo protection branch and a `freight_calc.py ocean` breakeven gate.
  - **Deadline mode-shift** — air / sea-air / air-bridge-split keyed to the **stock-out cost vs air premium** total-landed-cost trade (not air-vs-ocean-rate), with a `freight_calc.py air` chargeable-weight gate.
- **CLAUDE.md** — added § "Value-add completeness (build-out 2026-06-05)" dispositioning every menu item, plus a milestones entry, and wired the scenarios bank into the routing/knowledge sections.

### Honestly N-A for a non-code vertical (documented, not forced)
The code-runtime tier (code-aware MCP server, LSP, `bin/`, monitors, output-styles, themes, `settings.json`/permissions) is genuinely not applicable to a freight-sales advisory vertical and is dispositioned with a one-line reason each in CLAUDE.md § "Value-add completeness". A second calculator was assessed as **N-A** — `scripts/freight_calc.py` (air / ocean / quote) already covers the recurring arithmetic, and the two new trees reuse it rather than needing new code.

### Shared-file changes required (orchestrator-owned, NOT done here)
- `.repo-layout.json` `allowed_globs` already covers `plugins/*/scenarios/**`, `plugins/*/knowledge/**`, and `plugins/*/CHANGELOG.md` — no new glob required (all four added paths fall under existing globs).
- `.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json` `version` bumped `0.1.2` → `0.2.0` (both mirrors).

## [0.1.2] — prior release

6 agents (`freight-rate-quoter`, `rfq-tender-strategist`, `key-account-manager`, `pipeline-forecast-coach`, `prospecting-outreach-strategist`, `trade-lane-compliance-advisor`), 6 skills, 6 slash commands, 22 best-practices, a 2-doc knowledge bank (glossary + 8 Mermaid decision trees), templates, and a runnable chargeable-weight / quote-margin calculator (`scripts/freight_calc.py`). Carrier-neutral, public industry-standard practice. Built per PR #315 (consolidated knowledge decision-trees, best-practices, templates).
