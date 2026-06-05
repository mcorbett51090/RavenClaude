# Changelog — project-management

All notable changes to the `project-management` plugin. Versions are semver; the authoritative version is `.claude-plugin/plugin.json` (mirrored in the root `marketplace.json`).

## 0.4.0 — 2026-06-05

Value-add build-out: scenarios bank enabled, two net-new decision trees, and a runnable EVM/PERT/forecast calculator.

### Added

- **Scenarios bank** (`scenarios/`) — enabled (replaces the prior `## 7a` TODO placeholder in `CLAUDE.md`). README + 4 dated, scope-tagged, unverified engagement narratives:
  - `2026-06-05-watermelon-status-green-on-red` — a green RAG hiding an amber-band SPI; instrument earned value, lead status with narrative.
  - `2026-06-05-scope-creep-no-change-control` — silent scope absorption blamed as "delay"; reconcile delivered-vs-baselined scope, make the change path lower-friction than the back channel.
  - `2026-06-05-evm-cpi-recovery-decision` — CPI ~0.83 at 30% complete; EAC/TCPI prove recovery-to-budget is implausible, package as a steering decision.
  - `2026-06-05-predictive-agile-method-mismatch` — approach chosen by org habit, not the work; traverse the delivery-approach tree against observable inputs.
  - Scenario-retrieval priors wired into `CLAUDE.md` §7a for all four specialists.
- **Two NEW Mermaid decision trees** (`knowledge/`), complementing — not duplicating — the 7 trees consolidated in `pm-decision-trees.md` (PR #315):
  - `pm-estimate-confidence-decision-tree.md` — cone-of-uncertainty / three-point (PERT) / contingency-sized-from-the-spread. Sits one level earlier than the change-request tree.
  - `pm-recover-vs-escalate-slip-decision-tree.md` — a measured schedule/cost slip: absorb-into-float / recover-at-team / draw-contingency / escalate. The watermelon-prevention companion that *feeds* the existing Status-RAG and Escalation-threshold trees.
- **Runnable calculator** `scripts/evm_calc.py` (stdlib only, Python 3.8+; `ruff check` clean):
  - `evm` — CV/SV, CPI/SPI, the four standard EAC variants, ETC, VAC, TCPI, and a RAG read keyed to the Status-RAG tree thresholds.
  - `pert` — three-point mean `(O+4M+P)/6`, SD `(P−O)/6`, ±1σ/±2σ confidence bands for contingency sizing.
  - `forecast` — agile completion range from a throughput sample (mean ±1σ → optimistic/expected/conservative sprint counts).
- **CLAUDE.md** — new `## 7d` calculator section, `## Value-add completeness (build-out 2026-06-05)` disposition table; §7 knowledge-bank table extended with the two new trees.
- **CHANGELOG.md** — this file.

### Notes

- EVM and PERT formulas are standard PMBOK/PERT framings (web-verified 2026-06-05); the RAG and contingency *threshold numbers* are this plugin's conventions and carry inline `[verify-at-use]` markers — calibrate to the engagement, not the tool.
- **Migration:** none — additive only. Nothing in a consumer's installed plugin breaks on `/plugin marketplace update`; the scenarios bank, new trees, and calculator are net-new files.

## 0.3.3 and earlier

Initial release + PR #315 consolidation: 4 specialist agents (delivery-lead, scrum-master, risk-and-raid-analyst, stakeholder-comms-lead), 4 skills, 5 templates, a consolidated 7-tree `pm-decision-trees.md`, and a best-practices library. See git history for the per-version detail (this CHANGELOG begins at 0.4.0).
