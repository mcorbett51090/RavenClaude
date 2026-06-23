# Changelog — dental-practice

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.3.1] — 2026-06-12

Version bump previously unlogged here (rolls up `0.2.0` → `0.3.1`); the change that set `0.3.1`:

- fix: repo-review fixes — gate tool-absence guard + broken antipattern regex (#422)

## [0.2.0] — 2026-06-05

Value-add build-out — mirrors the `veterinary-practice` v0.2.0 recipe for a **pure non-code vertical** (practice ops, scheduling/production, insurance/PPO, hygiene recall, case acceptance, DSO economics). Adds the scenarios bank, two Mermaid decision-tree knowledge files, a runnable practice-economics calculator, and cited KPI benchmarks; honestly dispositions the code-runtime tier as N-A.

- **Scenarios bank** (`scenarios/`) — README plus **4** dated, scope-tagged engagement scenarios (mirrors the marketplace 9-field schema, `product_version: "n/a"` for a non-code vertical): hygiene-recall reactivation, case-acceptance presentation fix, PPO-vs-FFS payer mix, production-per-hour schedule read. Each carries an "Action for the next consultant" lesson and cited public benchmarks. (The README already enumerated all four; this release adds the three missing scenario files.)
- **2 new Mermaid decision-tree knowledge files** (the plugin previously had zero):
  - `dental-ppo-vs-ffs-decision-tree.md` — keep / re-negotiate / drop a PPO plan and the FFS question, measured per-plan on effective fee × volume × strategic value, with the write-off arithmetic. ADA HPI / Veritas / BoomCloud-cited.
  - `dental-hygiene-capacity-decision-tree.md` — fill and re-mix the hours you already own (reappointment, overdue recall, per-hour yield) before expansion/marketing. Dental Economics / Dentx / Dental Intelligence-cited.
- **Runnable calculator** `scripts/dental_calc.py` (stdlib only, Python 3.8+) — three modes: `ppo-mix` (effective fee + write-off dollars + negotiation-lift recovery), `hygiene-capacity` (recoverable fill from reappointment gap + overdue pool + per-hour yield gap), `collection-lift` (dollars banked by raising the collection ratio). Decision-support, not advice.
- **KPI glossary enriched** (`knowledge/dental-kpi-glossary.md`) — replaced the thin stub with cited, dated benchmark tables (collection ratio, doctor/hygiene production per hour, hygiene share + reappointment, case acceptance, overhead/staff-cost/net-margin, PPO write-off, DSO margin, practice-scale revenue) plus a PMS-landscape context section (Dentrix, Eaglesoft, Open Dental, Curve, Denticon, Dental Intel, Jarvis). All ADA/dental-economics/trade-cited with retrieval dates.

### Honestly N-A for a non-code vertical (documented, not forced)
The code-runtime tier (code-aware MCP server, LSP, `bin/`, monitors, output-styles, themes, `settings.json`) is genuinely not applicable to a practice-operations advisory vertical. Each is dispositioned with a one-line reason in `CLAUDE.md` § "Value-add completeness (build-out 2026-06-05)". The one runtime item with real non-code value — a runnable calculator — **was** built (`scripts/dental_calc.py`).

### Shared-file changes required (orchestrator-owned, NOT done here)
- `.repo-layout.json` `allowed_globs` already covers `plugins/*/scenarios/**` and `plugins/*/scripts/**` — no new globs needed.
- `.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json` `version` bump `0.1.0` → `0.2.0`.

## [0.1.0] — initial release

4 agents (`dental-practice-lead`, `clinical-treatment-planner`, `dental-rcm-specialist`, `dental-operations-analyst`), 5 skills, 3 templates, 5 commands, 1 advisory hook, an 8-rule best-practices set, and a 4-file research-grounded knowledge bank. A treatment-planning-and-revenue-cycle team for a dental practice owner or office manager.
