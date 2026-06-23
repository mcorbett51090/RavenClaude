# Changelog — nonprofit-fundraising

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.3.0] — 2026-06-22

Post-award / grant-management value-add — **complements** (does not duplicate) the existing pre-award / development side. Adds the post-award compliance lane as a skill + knowledge doc + template + 3 best-practice rules; **no new agent** (team-growth-as-knowledge house rule — `grant-writer` and `nonprofit-finance-analyst` reach the new surface).

- **New knowledge doc** `knowledge/grant-management-post-award.md` — dated, with **2 Mermaid decision trees**: (a) allowable-cost determination (allowable/allocable/reasonable + direct vs indirect, Uniform Guidance 2 CFR 200) and (b) reporting-cadence & compliance triage (financial + programmatic reports, deadlines, the Single Audit threshold). Plus budget-vs-actual tracking, drawdown/reimbursement, modifications/no-cost extensions, the document/audit trail (records retention), and subrecipient monitoring. **Every regulatory specific carries a retrieval date + `[verify-at-use]`; advisory only, not legal/accounting/audit advice (§2).**
- **New skill** `skills/grant-postaward-compliance/SKILL.md` — the post-award lifecycle: set up → spend within allowable costs → track budget-vs-actual monthly → report on cadence → modify before needed → close out audit-ready.
- **New template** `templates/grant-budget-vs-actual-tracker.md` — fill-in budget-vs-actual ledger by category + drawdown log + report calendar (financial + programmatic) + modifications + subrecipient monitoring + audit-readiness checklist.
- **3 new best-practice rules** (indexed in `best-practices/README.md`, now 23 rules): `spend-only-on-allowable-allocable-reasonable-costs.md`, `track-budget-vs-actual-every-month-not-at-report-time.md`, `keep-an-audit-ready-document-trail.md`.
- **`CLAUDE.md`** — added the new skill, knowledge doc, and template to their tables (§5) plus a one-line post-award-coverage note.
- **`plugin.json`** — version `0.2.1` → `0.3.0` (minor); description counts updated (6 skills, 4 templates, 23 best-practice rules, 5-file knowledge bank; "covering both pre-award development and post-award grant compliance").

### Shared-file changes (orchestrator-owned, NOT done here)
- `.claude-plugin/marketplace.json` `version` must be bumped `0.2.1` → `0.3.0` to match this catalog entry (per task constraint, marketplace.json was not edited here).

## [0.2.0] — 2026-06-05

Value-add build-out — generalizing the marketplace non-code-vertical recipe (proven on `veterinary-practice`) to development/fundraising. Adds the scenarios bank, two complementary Mermaid decision-tree knowledge files, a runnable fundraising-economics calculator, and cited KPI benchmarks; honestly dispositions the code-runtime tier as N-A.

- **Scenarios bank** (`scenarios/`) — rounded to **4** dated, scope-tagged engagement scenarios (mirrors the marketplace 9-field schema, `product_version: "n/a"` for a non-code vertical). The donor-retention-turnaround scenario shipped in #315; this round adds **major-gift pipeline build** (a list is not a pipeline — qualify before cultivate, cap the portfolio, stage every prospect), **annual-fund renewal lift** (run the LYBUNT/SYBUNT report before buying acquisition; segment-then-sequence + percent-increase upgrade), and **campaign feasibility / gift pyramid** (the donor pyramid sets the goal, not the project budget). Each carries an "Action for the next consultant" lesson and cited public benchmarks.
- **2 new Mermaid decision-tree knowledge files** that **complement** #315's consolidated `fundraising-decision-trees.md` (do not duplicate it):
  - `nonprofit-campaign-readiness-decision-tree.md` — go-public vs stay-silent vs not-yet for a capital/comprehensive campaign: gift range chart → rated prospect pool → case for support → lead gift (~10-25% of goal) → silent-phase threshold (~50-70%+). CapitalCampaignPro / DonorSearch / NonProfit PRO-cited.
  - `nonprofit-channel-investment-decision-tree.md` — where the next fundraising dollar goes: split CRD by channel first → fix retention first → judge acquisition on multi-year LTV, not first-year CRD. RallyUp / Bonterra / Kindsight-cited.
- **Runnable calculator** `scripts/fundraising_calc.py` (stdlib only, Python 3.8+) — three modes: `gift-pyramid` (tiered gift range chart: gifts-needed + prospects-needed + cumulative coverage vs goal), `cost-per-dollar` (per-channel CRD/ROI + blended + subsidy flag, never blended-only — §3 #4), `donor-ltv` (avg gift × frequency × lifespan, lifespan derivable from retention as 1/(1−r), + retain-vs-acquire payback — §3 #1). Decision-support, not advice. Ruff-clean, `py_compile`-clean, executable.
- **KPI glossary enriched** (`knowledge/fundraising-kpi-glossary.md`) — rewritten from a thin stub into cited, dated benchmark tables: retention (overall ~43-45%, first-time vs repeat), LYBUNT/SYBUNT definitions, donor LTV formula, cost-to-raise-a-dollar by channel, gift pyramid (lead gift 10-25%, 80/20), officer portfolio size, plus a CRM-landscape context section. All AFP/Bloomerang/Neon One/Kindsight/RallyUp/Bonterra/CapitalCampaignPro/DonorSearch-cited with retrieval dates.

### Honestly N-A for a non-code vertical (documented, not forced)
The code-runtime tier (code-aware MCP server, LSP, `bin/`, monitors, output-styles, themes, `settings.json`) is genuinely not applicable to a fundraising advisory vertical. Each is dispositioned with a one-line reason in `CLAUDE.md` § "Value-add completeness (build-out 2026-06-05)". The one runtime item with real non-code value — a runnable calculator — **was** built (`scripts/fundraising_calc.py`).

### Shared-file changes required (orchestrator-owned, NOT done here)
- `.repo-layout.json` `allowed_globs` must cover `plugins/*/scenarios/**` and `plugins/*/scripts/**` (both already exist for other plugins; confirm coverage — no edit made here per task constraint).
- `.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json` `version` bump `0.1.2` → `0.2.0` (orchestrator-owned; not done here).

## [0.1.x] — PR #315
Consolidated `fundraising-decision-trees.md` (Mermaid major-gift go/cultivate, retention-diagnosis, grant-pipeline trees), the best-practices/ rule set, templates/, and the first scenario (donor-retention-turnaround).

## [0.1.0] — initial release
4 agents (`development-lead`, `grant-writer`, `major-gifts-strategist`, `nonprofit-finance-analyst`), 5 skills, 3 templates, 5 commands, 1 advisory hook, an 8-rule best-practices set, and a 4-file research-grounded knowledge bank. A development team for a nonprofit fundraiser or executive director.
