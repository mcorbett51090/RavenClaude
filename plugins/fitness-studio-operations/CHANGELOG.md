# Changelog — fitness-studio-operations

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-06-25

Initial release.

### Added

- **3 agents** — `fitness-studio-operations-lead` (membership models + pricing, unit economics, front-desk & member experience, retail/ancillary revenue), `member-retention-analyst` (churn math, at-risk detection, win-back, the retention economic engine, cohort analysis), `class-and-instructor-ops-lead` (schedule & capacity/utilization, instructor mix, pay models, the 1099-vs-W2 flag, no-show policy).
- **5 skills** — `design-membership-model`, `compute-studio-unit-economics`, `analyze-retention-and-churn`, `optimize-class-schedule`, `design-instructor-pay-model`.
- **Knowledge bank** — `fitness-studio-operations-decision-trees.md` (5 Mermaid trees: pricing-model, retention-intervention, capacity, pay-model, no-show) and `fitness-studio-operations-reference-2026.md` (dated tooling/benchmark map; re-verify before quoting).
- **7 best-practices** — retention is the economic engine, know your real churn rate, compute LTV before CAC, price the membership model not just the number, manage capacity by utilization not headcount, pick the instructor pay model on purpose, enforce a no-show policy or expect ghost capacity.
- **3 templates** — membership-model-and-pricing, retention-dashboard, class-schedule-and-pay-plan.
- **3 commands** — `/design-membership`, `/retention-review`, `/schedule-audit`.
- **1 advisory hook** — `check-studio-anti-patterns.sh` (3 checks on `.md`; `STUDIO_STRICT=1` to block).

### Verify-at-use

- All platform names, processor fees, and benchmark numbers in `fitness-studio-operations-reference-2026.md` (booking/billing platforms, churn and utilization rules of thumb, payback windows) — volatile; re-confirm against the vendor and your own historical actuals before quoting.
- The 1099-vs-W2 guidance is a practical operator flag, **not** a legal determination — the binding classification call belongs to `people-operations-hr` and the studio's counsel.
