# Changelog — commercial-real-estate

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.2.0] — 2026-06-05

Value-add build-out — extends the non-code-vertical recipe (the `veterinary-practice` pilot) to CRE. Adds the scenarios bank, two new Mermaid decision-tree knowledge files complementing the consolidated #315 trees, and a runnable underwriting calculator; honestly dispositions the code-runtime tier as N-A.

- **Scenarios bank** (`scenarios/`) — the README index (added in #315) is now backed by **4** dated, scope-tagged engagement scenarios (mirrors the marketplace 9-field schema, `product_version: "n/a"` for a non-code vertical): DSCR breach on a refinance rate-reset, NOI erosion from opex/recovery-ratio vs vacancy, hold-vs-sell at a cap-rate shift, and lease-renewal vs re-tenant on a net-effective/TI/downtime basis. Each carries an "Action for the next analyst" lesson and cited, `[verify-at-use]`-dated public references.
- **2 new Mermaid decision-tree knowledge files** (complement the consolidated trees added in #315 — lease rollover, acquisition retrade/walk, asset-plan prioritization):
  - `cre-hold-sell-refi-decision-tree.md` — sell vs refinance-and-hold vs hold-unlevered at a capital event, with the exit-cap-sensitivity gate node and the refi-clearing (binding-constraint) test made explicit. Cap-rate/Treasury figures cited + `[verify-at-use]`.
  - `cre-lease-structure-nnn-vs-gross-decision-tree.md` — NNN vs gross vs modified-gross expense-recovery structure (who bears opex growth), with the recovery-ratio recheck loop. Holland & Knight / NAIOP-cited.
- **Runnable calculator** `scripts/cre_calc.py` (stdlib only, Python 3.8+) — four modes: `noi-cap` (NOI build-up + going-in cap + price-at-target-cap + cap-rate-vs-Treasury spread), `debt-size` (loan sized by the *binding* of max-LTV / min-DSCR / min-debt-yield, with the resulting ratios + cash-after-debt), `cash-on-cash` (levered first-year return on equity), `hold-vs-sell` (net sale proceeds + equity multiple + rough one-year held return at an exit-cap shift). Decision-support, not investment/legal/tax advice. `ruff check` clean.

### Honestly N-A for a non-code vertical (documented, not forced)
The code-runtime tier (code-aware/bundled MCP server, LSP, `bin/`, monitors, output-styles, themes, `settings.json`) is genuinely not applicable to a CRE investment/asset-management advisory vertical. Each is dispositioned with a one-line reason in `CLAUDE.md` § "Value-add completeness (build-out 2026-06-05)". The one runtime item with real non-code value — a runnable underwriting calculator — **was** built (`scripts/cre_calc.py`).

### Shared-file changes required (orchestrator-owned, NOT done here)
- `.repo-layout.json` `allowed_globs` already covers `plugins/*/scenarios/**`, `plugins/*/scripts/**`, `plugins/*/knowledge/**`, and `plugins/*/CHANGELOG.md` — no new globs needed.
- `.claude-plugin/marketplace.json` `version` bump `0.1.2` → `0.2.0` (the `plugin.json` mirror was bumped here; the catalog mirror must match — CI fails on drift).

## [0.1.0] — initial release

4 agents (`cre-engagement-lead`, `acquisitions-underwriter`, `asset-property-manager`, `cre-market-analyst`), 5 skills, 4 templates, 5 commands, 1 advisory hook, an 8-rule best-practices set, and a 4-file research-grounded knowledge bank. An acquisitions-and-asset-management team for a CRE owner, operator, or advisor.
