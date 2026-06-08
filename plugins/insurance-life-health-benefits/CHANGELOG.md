# Changelog — insurance-life-health-benefits

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

## 0.2.0 — 2026-06-08

Deepening pass. No breaking changes — purely additive; a consumer running `/plugin marketplace update`
gets four more best-practices, three more field notes, and a runnable calculator with no migration needed.

- **Best-practices 8 → 12** — added `credibility-is-the-hinge-of-rating`, `network-adequacy-before-plan-elegance`,
  `stop-loss-is-the-real-self-funded-decision`, and `verify-dated-figures-at-build`, rounding out the rating,
  plan-design, funding, and accuracy-discipline house opinions.
- **Scenarios bank 2 → 5** (all `reviewed: false`) — added `loss-ratio-mistaken-for-mlr-rebate`,
  `missed-cobra-notice-window`, and `thin-contribution-starved-the-pool`, corroborating the loss-ratio≠MLR,
  compliance-calendar, and contribution-strategy best-practices.
- **Runnable calculator** — `scripts/benefits_calc.py`, stdlib-only (argparse), three subcommands:
  `loss-ratio` (underwriting loss ratio AND a separate ACA MLR rebate flag vs the 80%/85% threshold — never
  conflated), `contribution` (employer/employee premium split + all-in annual cost across enrollees), and
  `renewal` (projected premium decomposed into trend × experience × demographic). Educational scaffolding;
  every ACA/MLR figure is `[verify-at-build]`. ruff-clean (F,E9,B,C4,I,UP).
- **5 decision trees** in the knowledge bank; CLAUDE.md milestone + counts reconciled.

## 0.1.0 — 2026-06-08

Initial release. The group life / health / employee-benefits side of insurance, distinct from property &
casualty (`insurance-pc`).

- **3 agents** — `benefits-advisor` (group plan design across medical/dental/vision/life/disability, funding
  strategy fully-insured vs self-funded vs level-funded, contribution structure, ACA/ERISA basics),
  `underwriting-and-actuarial-analyst` (rating factors, manual vs experience rating, loss ratios + ACA MLR,
  renewal-projection decomposition), `enrollment-and-compliance-lead` (open-enrollment operations, eligibility,
  COBRA/HIPAA, ACA 1095-C/1094-C, ERISA 5500 + SPD/SBC, carrier coordination). Each carries the full
  scenario-authoring frontmatter.
- **3 skills** — `benefits-plan-design`, `underwriting-and-rating`, `enrollment-and-compliance`.
- **Knowledge bank** — `insurance-life-health-benefits-decision-trees.md`: Mermaid trees (funding-model selection,
  rating-method/renewal read) + a dated 2026 reference map (ACA/COBRA/ERISA/MLR figures, plan types, funding
  models) — every figure `[verify-at-build]`.
- **8 best-practices**, **3 commands** (`design-benefits-program`, `review-renewal`, `plan-open-enrollment`),
  **2 templates** (benefits-program brief, renewal-and-rate review), **1 advisory hook**
  (`check-insurance-life-health-benefits-anti-patterns.sh`; `BENEFITS_STRICT=1` to make it blocking), and a
  **scenarios bank** (2 field notes).
- **Educational scaffolding only — not legal, tax, or actuarial advice.** Seams: P&C lines → `insurance-pc`;
  HR benefits administration → `people-ops-hr`; provider-side medical billing → `medical-revenue-cycle`.
  Requires `ravenclaude-core@>=0.7.0`.
