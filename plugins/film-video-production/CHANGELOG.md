# Changelog — film-video-production

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.2.0] — 2026-06-05

Value-add build-out for the non-code production-management vertical. Adds the scenarios bank, a net-new Mermaid decision-tree knowledge file (complementing the three trees PR #315 added), and a runnable production-economics calculator; honestly dispositions the code-runtime tier as N-A.

- **Scenarios bank** (`scenarios/`) — new directory + README + **4** dated, scope-tagged engagement scenarios (mirrors the marketplace 9-field schema, `product_version: "n/a"` for a non-code vertical): shoot-day overtime spiral, fixed-bid scope-vs-budget, post-pipeline delivery slip, contingency burn before wrap. Each carries an "Action for the next producer/analyst" lesson and cited rate/convention framing.
- **1 net-new Mermaid decision-tree knowledge file** complementing the three trees in PR #315 (budget-overage classify; pre-lock post parallelization; delivery-problem triage):
  - `production-in-house-vs-vendor-decision-tree.md` — in-house staff / owned gear vs. rent / freelance vs. buy as a utilization + cash + risk trade (usually rent-per-project or hybrid), with the breakeven arithmetic for both gear (rent-vs-buy) and crew (staff-vs-freelance). Saturation.io / First Draft Filmworks / Filmmaker's Production Bible-cited.
- **Runnable calculator** `scripts/production_calc.py` (stdlib only, Python 3.8+) — three modes: `shoot-day-cost` (loaded day = straight-time + overtime 1.5x/2x + fringe load + flat per-day costs), `contingency` (top-sheet reserve at a % of the BTL+post base + a drawn/burn-rate projection that flags exhaustion-before-wrap), `overtime-burden` (the true marginal cost of one held hour at ST / 1.5x / 2x, fringe-loaded). Decision-support, not union/legal/financial advice; ruff-clean.

### Honestly N-A for a non-code vertical (documented, not forced)
The code-runtime tier (code-aware/bundled MCP server, LSP, `bin/`, monitors, output-styles, themes, `settings.json`) is genuinely not applicable to a production-management advisory vertical. Each is dispositioned with a one-line reason in `CLAUDE.md` section "Value-add completeness (build-out 2026-06-05)". The one runtime item with real non-code value — a runnable calculator — **was** built (`scripts/production_calc.py`).

### Shared-file changes required (orchestrator-owned, NOT done here)
- `.repo-layout.json` `allowed_globs` must cover `plugins/*/scenarios/**` and `plugins/*/scripts/**` (both already exist for other plugins; confirm coverage).
- `.claude-plugin/marketplace.json` catalog `version` for `film-video-production` must bump `0.1.2` → `0.2.0` to match `.claude-plugin/plugin.json` (CI fails on drift).

## [0.1.x] — initial release

4 agents (`production-lead`, `line-producer`, `post-production-supervisor`, `production-finance-analyst`), 5 skills, 5 templates, 5 commands, 1 advisory hook, an 8-rule best-practices set, and a research-grounded knowledge bank (incl. the three Mermaid decision trees from PR #315). A production-management team for a producer, production company, or post house.
