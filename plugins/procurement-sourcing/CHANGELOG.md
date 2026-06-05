# Changelog — procurement-sourcing

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.2.0] — 2026-06-05

Value-add build-out — mirrors the merged `veterinary-practice` recipe for a **pure non-code vertical**. Adds the scenarios bank, two complementary Mermaid decision-tree knowledge files, and a runnable strategic-sourcing calculator; honestly dispositions the code-runtime tier as N-A. Net-new on top of PR #315 (which added the consolidated knowledge decision-trees + best-practices/ + templates/).

- **Scenarios bank** (`scenarios/`) — new directory + README + **4** dated, scope-tagged engagement scenarios (mirrors the marketplace 9-field schema, `product_version: "n/a"` for a non-code vertical): negotiated-vs-realized savings leakage, single-source supply-risk / dual-source, maverick-spend / non-compliance, should-cost / TCO teardown. Each carries an "Action for the next consultant" lesson and cited public benchmarks.
- **2 new Mermaid decision-tree knowledge files** (complementing the #315 trees, which placed/played/validated; these sit one level *up*):
  - `procurement-kraljic-positioning-decision-tree.md` — how to **place** a category on the supply-risk × profit-impact matrix (the precondition the #315 "which sourcing play" tree assumes). CIPS / Art of Procurement / Planergy-cited; hands off to the existing play tree.
  - `procurement-make-vs-buy-decision-tree.md` — the make-in-house vs buy-from-market fork *before* a sourcing event (core-competency → control → market → full-cost/TCO, with a hybrid base/swing outcome). CFI / supply-chain make-vs-buy-cited.
- **Runnable calculator** `scripts/sourcing_calc.py` (stdlib only, Python 3.8+, `ruff`-clean) — three modes: `tco` (compare bids on total cost of ownership, flags the unit-price trap), `savings` (negotiated → realized → incremental, with the leakage gap + realization rate), `terms` (payment-terms working-capital NPV + early-pay-discount implied-rate test). Decision-support, not advice.

### Honestly N-A for a non-code vertical (documented, not forced)
The code-runtime tier (code-aware MCP server, LSP, `bin/`, monitors, output-styles, themes, `settings.json`) is genuinely not applicable to a strategic-sourcing advisory vertical. Each is dispositioned with a one-line reason in `CLAUDE.md` § "Value-add completeness (build-out 2026-06-05)". The one runtime item with real non-code value — a runnable calculator — **was** built (`scripts/sourcing_calc.py`). P2P/ERP MCP servers are per-tenant / authenticated / PII-bearing, so bundling is out of scope and the plugin stays P2P/ERP-neutral (§2).

### Shared-file changes required (orchestrator-owned, NOT done here)
- `.repo-layout.json` `allowed_globs` already covers `plugins/*/scenarios/**` and `plugins/*/scripts/**` (both pre-exist for other plugins) — no new globs required; confirm coverage.
- `.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json` `version` bump `0.1.2` → `0.2.0`.

## [0.1.x] — initial release + PR #315 knowledge consolidation

4 agents (`sourcing-lead`, `category-strategist`, `supplier-risk-specialist`, `spend-analytics-analyst`), 5 skills, 4 templates, 5 commands, 1 advisory hook, an 8-rule best-practices set, and a research-grounded knowledge bank (KPI glossary, sourcing economics, benchmarks, and the consolidated decision-trees added in #315). A strategic-sourcing team for a procurement / category lead.
