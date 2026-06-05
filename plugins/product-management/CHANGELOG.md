# Changelog — product-management

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.3.0] — 2026-06-05

Non-code-vertical value-add build-out — extends the plugin against the full value-add menu without forking a new agent (team-growth-as-knowledge house rule). Completes the scenarios bank, adds two complementary Mermaid decision trees, and ships a runnable prioritization calculator; honestly dispositions the code-runtime tier as N-A.

- **Scenarios bank completed** (`scenarios/`) — the README already indexed four scenarios but only one existed; added the **3** missing dated, scope-tagged engagement scenarios (mirrors the marketplace 9-field schema, `product_version: "n/a"`): feature-shipped-without-success-metric, discovery-skipped → low-adoption, build-vs-buy-vs-partner-capability. Each carries an "Action for the next PM" lesson and cited public sources. (Also added `reviewed: false` to the pre-existing roadmap-thrash scenario for schema consistency.)
- **2 new standalone Mermaid decision-tree knowledge files** complementing the consolidated #315 trees (both were already cross-referenced but did not exist):
  - `prioritization-method-selection-decision-tree.md` — RICE vs. WSJF vs. Kano vs. argue-the-bet, with the split-mixed-types rule, a method comparison table (best-when / formula / failure-prevented / failure-invited), and the published formulas/scales. Intercom/SAFe/ProductPlan/Product-School-cited.
  - `build-vs-buy-vs-partner-decision-tree.md` — own vs. rent vs. share a capability via the differentiation test + core/context/commodity filter, with the pre-PMF carve-out and opportunity-cost sizing. ideaplan/ClearFunction/Engenia-cited; the core-vs-context attribution to Geoffrey Moore is marked `[unverified — training-knowledge attribution]`.
- **Runnable calculator** `scripts/pm_calc.py` (stdlib only, Python 3.8+, ruff-clean) — three modes: `rice` (Reach × Impact × Confidence / Effort; single item or a ranked-table compare; Intercom impact/confidence scales), `wsjf` (SAFe Cost-of-Delay ÷ Job Size with the three CoD inputs, Fibonacci convention), `opportunity` (bottoms-up size + an honest +/-(1-confidence) band, explicitly not a statistical interval). Decision-support, not a data source — the score's value is making the inputs explicit and arguable, not the decimal.
- **CLAUDE.md** gained §5 Knowledge bank (with the two new trees), §6 Scenarios bank & runnable tooling, §7 Value-add completeness table, §8 Milestones.

### Honestly N-A for a non-code vertical (documented, not forced)
The code-runtime tier (bundled/code-aware MCP server, LSP, `bin/`, monitors, output-styles, themes, `settings.json`) is genuinely not applicable to a product-strategy/discovery advisory vertical. PM tooling (Jira/Productboard/Amplitude/Linear) is per-tenant/authenticated/billed → recommend-not-bundle at most, never bundled. Each item is dispositioned with a one-line reason in `CLAUDE.md` §7. The one runtime item with real non-code value — a runnable prioritization calculator — **was** built (`scripts/pm_calc.py`).

### Shared-file changes (orchestrator-owned, NOT done here)
- `.repo-layout.json` `allowed_globs` already cover `plugins/*/scenarios/**`, `plugins/*/knowledge/**`, and `plugins/*/scripts/**` — no new globs needed.
- `.claude-plugin/marketplace.json` catalog `version` mirror bumped `0.2.2` → `0.3.0` alongside `plugin.json` (also corrected the skills count in both descriptions: 3/7 → 5).

## [0.2.2] — prior

3 specialist agents (`product-strategist`, `product-discovery-lead`, `product-metrics-analyst`), 5 skills, 4 templates, 4 commands, 1 advisory hook, a 12-rule best-practices set, and a consolidated decision-tree knowledge bank (#315). The product craft of deciding what to build and why — continuous discovery, evidence-based prioritization, crisp PRDs, and outcome metrics — distinct from project-management's delivery lane.
