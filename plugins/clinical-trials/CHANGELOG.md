# Changelog — clinical-trials

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.2.0] — 2026-06-05

Value-add build-out — extends the recipe (proven on the `veterinary-practice` pilot) to a **regulated non-code vertical**. Adds the scenarios bank, two Mermaid decision-tree knowledge files, a runnable clinical-operations calculator, and cited KPI benchmarks; honestly dispositions the code-runtime tier as N-A.

- **Scenarios bank** (`scenarios/`) — new directory + README + **4** dated, scope-tagged engagement scenarios (mirrors the marketplace 9-field schema, `product_version: "n/a"` for a non-code vertical): enrollment-shortfall recovery, protocol-deviation/CAPA, risk-based monitoring plan, IRB/IND submission gaps. Each carries an "Action for the next consultant" lesson and cited public sources, with no sponsor/CRO identity and no patient PHI.
- **2 new Mermaid decision-tree knowledge files** (the plugin previously had zero Mermaid trees — its `trials-decision-trees.md` is a prose skill/specialist router):
  - `trials-enrollment-shortfall-recovery-decision-tree.md` — diagnose the funnel leak (eligibility vs referral vs activation vs retention) and exhaust cheap upstream levers before a site expansion, with the sites × rate × months feasibility arithmetic. WCG/ACT/Sofpromed-cited.
  - `trials-monitoring-intensity-decision-tree.md` — risk-based monitoring intensity under **ICH E6(R3)** (adopted 2025-01-06, in force 2025-07-23; FDA final guidance Sept 2025): risk-assessment-first, centralized backbone, targeted on-site SDV by data criticality, with the cost read vs flat 100% SDV. ICH/FDA/ACRP/Applied-Clinical-Trials-cited.
- **Runnable calculator** `scripts/trials_calc.py` (stdlib only, Python 3.8+) — three modes: `enrollment-feasibility` (sites × rate × months vs target + breakeven rate/added-sites), `recruitment-funnel` (screens needed + spend + screen-to-enroll ratio), `retention-roi` (replace-vs-retain breakeven dropout-reduction). Decision-support, not advice; explicitly **NOT** a sample-size/power tool.
- **KPI glossary rewritten** (`knowledge/trials-kpi-glossary.md`) — from a thin 4-section stub into cited, dated benchmark tables across enrollment, retention & cost, schedule, quality & monitoring, and submission-readiness (site under-enrollment %, per-patient cost, dropout/replacement cost, delay rate, SDV-vs-cost figures, IND 30-day window). All ICH/FDA/WCG/Applied-Clinical-Trials/Sofpromed/mdgroup-cited with retrieval dates.

### Honestly N-A for a non-code vertical (documented, not forced)
The code-runtime tier (code-aware MCP server, LSP, `bin/`, monitors, output-styles, themes, `settings.json`) is genuinely not applicable to a clinical-operations advisory vertical. Each is dispositioned with a one-line reason in `CLAUDE.md` § "Value-add completeness (build-out 2026-06-05)". The one runtime item with real non-code value — a runnable calculator — **was** built (`scripts/trials_calc.py`). A ClinicalTrials.gov read-only API is noted as a possible *future recommend-don't-bundle* MCP candidate, not built this round.

### Shared-file changes required (orchestrator-owned, NOT done here)
- `.repo-layout.json` `allowed_globs` already covers `plugins/*/scenarios/**` and `plugins/*/scripts/**` — no new glob needed.
- `.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json` `version` bump `0.1.0` → `0.2.0`.

## [0.1.0] — initial release

4 agents (`trials-engagement-lead`, `protocol-design-specialist`, `clinical-operations-manager`, `regulatory-submissions-specialist`), 5 skills, 3 templates, 5 commands, 1 advisory hook, an 8-rule best-practices set, and a 4-file research-grounded knowledge bank. A clinical-operations team for a trial sponsor, CRO, or site network.
