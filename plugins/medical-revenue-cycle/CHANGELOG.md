# Changelog — medical-revenue-cycle

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.2.2] — 2026-07-09

### Fixed

- **Advisory anti-pattern hook now fires under Claude Code.** `hooks/flag-medical-revenue-cycle-antipatterns.sh` read the target path only from `$CLAUDE_TOOL_FILE_PATH` (`$1`) — not a real Claude Code hook variable — so under Claude Code it received an empty path and silently no-op'd. Added the canonical stdin-JSON `.tool_input.file_path` fallback so the hook inspects the written file as intended. Advisory-only (no gate/behavior change beyond the hook actually running now). From the 2026-07-09 autonomous repo review (Decision 1).

## [0.2.1] — 2026-06-12

Version bump previously unlogged here; the change that set `0.2.1`:

- fix: repo-review fixes — gate tool-absence guard + broken antipattern regex (#422)

## [0.2.0] — 2026-06-05

Value-add build-out — adds the scenarios bank, a runnable RCM calculator, two complementary Mermaid decision-tree knowledge files, and cited KPI/benchmark enrichment; honestly dispositions the code-runtime tier as N-A. Net-new on top of PR #315's consolidated decision-trees + best-practices + templates.

- **Scenarios bank** (`scenarios/`) — new directory + README + **4** dated, scope-tagged engagement scenarios (mirrors the marketplace 9-field schema, `product_version: "n/a"` for a non-code vertical, **no PHI**): denial-rate root-cause/CAPA, A/R-days reduction, clean-claim-rate improvement, payer-contract underpayment. Each carries an "Action for the next consultant" lesson and cited public benchmarks.
- **2 new complementary Mermaid decision-tree knowledge files** (complement, don't duplicate, #315's consolidated `rcm-decision-trees.md`):
  - `rcm-write-off-vs-appeal-decision-tree.md` — per-claim disposition once a denial is picked up: write off / appeal / corrected-claim / rebill / patient-balance / underpayment-escalation, routed by CARC (CO-16/CO-11/CO-22/CO-27/CO-29/CO-45/CO-50/CO-197, PR-1/2/3). CARC-X12/HFMA/overturn-rate-cited.
  - `rcm-front-end-denial-prevention-decision-tree.md` — where to *prevent* a denial upstream (eligibility / prior-auth / scrubber / credentialing / submission pipeline), embodying §3 #6. CARC/HFMA/CMS-cited.
- **Runnable calculator** `scripts/rcm_calc.py` (stdlib only, Python 3.8+) — four modes: `ar-days` (days-in-A/R + over-90 bucket flag), `net-collection` (NCR vs allowed, with the gross-collection gap exposed), `clean-claim` (rework cost of each point below the first-pass target), `denial-recovery` (recoverable cash in an unworked queue). Decision-support, not coding/billing/legal advice. Ruff-clean, py_compile-clean, executable.
- **KPI glossary rewritten + benchmarks enriched** — `knowledge/rcm-kpi-glossary.md` now carries cited, dated benchmark tables (clean-claim, denial, cost-to-collect, NCR, days-in-A/R, A/R>90, appeal overturn / recovery decay) plus a CARC/RARC quick-reference table routed to the decision trees. `knowledge/rcm-benchmarks-2026.md` gained a recovery-economics section. All HFMA/MGMA/MD-Clarity/X12-cited with retrieval dates; the unverified "30%→41% denials" vendor figure is flagged `[unverified]`.

### Honestly N-A for a non-code vertical (documented, not forced)
The code-runtime tier (code-aware MCP server, LSP, `bin/`, monitors, output-styles, themes, `settings.json`) is genuinely not applicable to an RCM advisory vertical. Each is dispositioned with a one-line reason in `CLAUDE.md` §9 "Value-add completeness (build-out 2026-06-05)". A clearinghouse/PM-EHR MCP would be PHI-bearing and per-tenant — *recommend, evaluate-first*, never bundled, and write/PHI access gates through `security-reviewer`. The one runtime item with real non-code value — a runnable calculator — **was** built (`scripts/rcm_calc.py`).

### Shared-file changes required (orchestrator-owned, NOT done here)
- `.repo-layout.json` `allowed_globs` already covers `plugins/*/scenarios/**` and `plugins/*/scripts/**` (and `plugins/*/knowledge/**`, `plugins/*/CHANGELOG.md`) — no new globs needed; confirm coverage.
- `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` `version` bump `0.1.2` → `0.2.0` (both mirrors).

## [0.1.2] — prior

4 agents (`rcm-engagement-lead`, `medical-coding-specialist`, `denials-management-specialist`, `rcm-analytics-analyst`), 5 skills, templates, 5 commands, 1 advisory hook, an 8-rule best-practices set, and a research-grounded knowledge bank (incl. the consolidated `rcm-decision-trees.md` from PR #315). A revenue-cycle team for a healthcare provider or RCM operator.
