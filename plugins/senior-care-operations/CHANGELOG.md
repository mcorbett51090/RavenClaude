# Changelog — senior-care-operations

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.2.0] — 2026-06-05

Value-add build-out — extends the non-code-vertical recipe (proven by `veterinary-practice`) to senior-care operations. Adds the scenarios bank, a complementary Mermaid staffing decision-tree, a runnable operations calculator, and cited KPI benchmarks; honestly dispositions the code-runtime tier as N-A. Builds **on top of** PR #315 (which added the consolidated `senior-care-decision-trees.md`, best-practices/, and templates) — does not duplicate it.

- **Scenarios bank** (`scenarios/`) — new directory + README + **4** dated, scope-tagged engagement scenarios (mirrors the marketplace 9-field schema, `product_version: "n/a"` for a non-code vertical): occupancy-slide segment recovery, staffing-PPD-to-acuity alignment, move-in-funnel conversion leak, payer-mix margin rebalance. Each carries an "Action for the next consultant" lesson and cited, dated public benchmarks.
- **1 new complementary Mermaid decision-tree knowledge file** `senior-care-acuity-staffing-ppd-decision-tree.md` — staff to acuity-based PPD vs. a fixed ratio (reallocate-before-hire, agency-as-bridge-only), with the regulatory frame that the federal nursing-home minimum-staffing rule (3.48 HPRD) is **rescinded** (PL 119-21 §71111 bars enforcement through 2034; interim final rule effective 2026-02-02) and that AL is state-regulated (e.g. Oregon's Acuity-Based Staffing Tool). Complements — does not duplicate — #315's occupancy/survey/admit trees. CMS/AHA/Federal-Register/Oregon-DHS/zumBrunnen-cited.
- **Runnable calculator** `scripts/senior_calc.py` (stdlib only, Python 3.8+) — four modes: `ppd-staffing` (acuity-weighted hours-per-resident-day → required care-hours/FTEs + gap), `occupancy-rev` (occupancy as a flow → end census + revenue gap to target), `move-in-funnel` (two-stage conversion → leaking stage vs benchmark + implied spend), `payer-mix` (per-payer revenue/margin + mix-shift margin delta). Decision-support, not advice. ruff-clean, py_compile-clean, executable.
- **KPI glossary enriched** (`knowledge/senior-care-kpi-glossary.md`) — added cited, dated benchmark tables (occupancy ~89.1% / AL LOS ~22mo / inquiry-to-tour ~29% / tour-to-move-in ~29–34% / overall ~12–15%; CPL ~$431 / owned-channel CPMI ~$1.2–2.8k; labor ~41% of revenue / ~15% operating profit / AL turnover ~41%; avg AL cost ~$5,676/mo / SNF FY2025 +4.2% / payer-mix barbell) plus a regulatory-status note. All NIC/Aline/USR-Engage/zumBrunnen/CMS/trade-cited with retrieval dates.

### Honestly N-A for a non-code vertical (documented, not forced)
The code-runtime tier (code-aware MCP server, LSP, `bin/`, monitors, output-styles, themes, `settings.json`) is genuinely not applicable to an operations-advisory vertical. Each is dispositioned with a one-line reason in `CLAUDE.md` § "Value-add completeness (build-out 2026-06-05)". The one runtime item with real non-code value — a runnable calculator — **was** built (`scripts/senior_calc.py`).

### Shared-file changes required (orchestrator-owned, NOT done here)
- `.repo-layout.json` `allowed_globs` already covers `plugins/*/scenarios/**` and `plugins/*/scripts/**` — confirmed; no new glob needed.
- `.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json` `version` bump `0.1.2` → `0.2.0` (recommended; not done here per task constraint).

## [0.1.2] — prior

Consolidated `senior-care-decision-trees.md` (occupancy decline / survey deficiency / high-acuity admit Mermaid trees), `best-practices/` rule set, and additional templates (PR #315), on top of the v0.1.0 initial release (4 agents, 5 skills, 5 commands, 1 advisory hook, research-grounded knowledge bank, 8 best-practice rules).
