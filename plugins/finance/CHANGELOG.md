# Changelog — finance

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.14.1] — 2026-06-20

Bug fix — the credit-card PAN check in the advisory anti-pattern hook never fired.

- **`hooks/flag-finance-anti-patterns.sh`** — the `[plaintext-pii-card]` credit-card regex used PCRE non-capturing groups `(?:…)` inside `grep -E` (POSIX ERE), which GNU grep rejects with `warning: ? at start of expression` and then never matches a real card number. Replaced the two `(?:…)` groups with plain capturing groups `(…)`; verified the pattern now matches all four major brands (Visa/MC/Amex/Discover) and does not false-positive on SSNs or ordinary digit strings. No behavior change other than the check now actually firing.

## [0.14.0] — 2026-06-05

Non-code-vertical value-add build-out — adds the scenarios bank, two new Mermaid decision-tree knowledge files, and a runnable corporate-finance / FP&A calculator. Net-new against PR #315 (which added the consolidated decision-trees, best-practices, and templates); honestly dispositions the code-runtime tier as N-A.

- **Scenarios bank** (`scenarios/`) — new directory + README + **4** dated, scope-tagged engagement scenarios (mirrors the marketplace 9-field schema, `product_version: "n/a"` for a non-code vertical): budget-vs-actual variance investigation, 13-week cash crunch, driver-based forecast rebuild, unit-economics / contribution-margin teardown. Each carries an "Action for the next analyst" lesson and cited public benchmarks. §8b TODO retired; inline **scenario-retrieval priors** added to `fpa-analyst`, `treasury-analyst`, and `financial-modeler`.
- **2 new Mermaid decision-tree knowledge files** (complementing #315's `finance-decision-trees.md`, not duplicating it — forecast-method and capex/build-vs-buy-NPV trees already existed there):
  - `scenario-vs-sensitivity-vs-simulation-decision-tree.md` — how to model uncertainty on a base case: sensitivity/tornado (find the levers) → scenario analysis (one switch, base/upside/downside) → Monte-Carlo (only on data-sourced distributions, else fall back to scenarios + state the gap).
  - `reforecast-vs-hold-the-budget-decision-tree.md` — whether to revise the plan when actuals diverge: reconcile/triage first → hold (one-time) / update rolling forecast only (late-year) / reforecast-budget-held / formal re-plan with governance. Keeps the budget as the yardstick.
- **Runnable calculator** `scripts/finance_calc.py` (stdlib only, Python 3.8+, ruff-clean) — four modes: `npv-irr` (DCF NPV + bisection-solved IRR for capex / build-vs-buy / lease-vs-buy), `variance-bridge` (price/volume/mix decomposition that sums exactly to the total), `runway` (direct-method weekly cash trough + run-out + min-buffer/covenant breach), `unit-economics` (gross-margin LTV + CAC payback + LTV:CAC on defensible definitions). Decision-support, not accounting/audit/tax/investment advice.

### Honestly N-A for a non-code vertical (documented, not forced)
The code-runtime tier (bundled code-aware MCP server, LSP / `.lsp.json`, `bin/`, monitors, output-styles, themes, `settings.json`) is genuinely not applicable to a corporate-finance / FP&A advisory vertical. Each is dispositioned with a one-line reason in `CLAUDE.md` § "Value-add completeness (build-out 2026-06-05)". The one runtime item with real non-code value — a runnable calculator — **was** built (`scripts/finance_calc.py`).

### Shared-file changes required (orchestrator-owned, NOT done here)
- `.repo-layout.json` `allowed_globs` already covers the new paths — `plugins/*/scenarios/**`, `plugins/*/scripts/**`, `plugins/*/knowledge/**`, and `plugins/*/CHANGELOG.md` all exist; no new glob needed.
- `.claude-plugin/marketplace.json` `version` bump to `0.14.0` to mirror `.claude-plugin/plugin.json` (CI fails on drift).

## [0.13.x] and earlier — pre-build-out

7 specialist agents (`fpa-analyst`, `financial-modeler`, `controller`, `treasury-analyst`, `valuation-analyst`, `audit-prep-specialist`, `board-pack-composer`), 9 skills, 8 templates, 5 commands, an advisory anti-pattern hook, a cited best-practices set, and a research-grounded knowledge bank (variance triage, consolidated decision-trees, ASC 805 / 718 / 740, accrual & cutoff, cost accounting, WACC sourcing, FP&A operating model + unit economics). PR #315 added the consolidated decision-trees, the `best-practices/` set, and `templates/`.
