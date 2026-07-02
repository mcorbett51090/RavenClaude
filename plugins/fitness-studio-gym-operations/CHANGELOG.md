# Changelog — fitness-studio-gym-operations

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-07-02

Initial release.

### Added

- **3 agents** — `fitness-studio-operations-lead` (membership P&L, growth vs churn, member LTV, class/floor utilization, ancillary revenue, pricing strategy), `membership-retention-manager` (onboarding, attendance/engagement triggers, churn prediction & saves, win-back, referral, tier design), `class-schedule-coach-ops` (class scheduling, instructor utilization & pay, capacity/fill, waitlist, no-show policy, sub coverage).
- **4 skills** — `membership-growth-and-churn`, `member-onboarding-and-retention`, `class-schedule-and-instructor-utilization`, `ancillary-revenue-mix`.
- **Knowledge bank** — `fitness-studio-decision-trees.md` (4 Mermaid trees: churn-save triage, membership pricing/tier model, schedule the class grid on fill, instructor pay model) and `fitness-studio-reference-2026.md` (dated reference: membership-economics identities, churn/fill/no-show/ancillary benchmarks `[ESTIMATE]`, instructor pay models, pricing tiers — each with source placeholder + retrieval date + verify-at-use).
- **5 best-practices** — retention beats acquisition on unit economics, the first 30 days decide the member, schedule the grid on demand not habit, ancillary revenue is the margin, price the membership on value and commitment.
- **2 templates** — studio-kpi-dashboard, retention-playbook.
- **2 commands** — `/build-retention-plan`, `/optimize-class-grid`.

### Scope & verify-at-use

- **Advisory domain operations knowledge, not legal, financial, or medical/exercise-prescription advice.** The agents store no member PII.
- All churn/LTV benchmarks, class-fill targets, instructor-pay norms, and pricing figures in `fitness-studio-reference-2026.md` are volatile and model-/market-specific — each carries a retrieval date + `[verify-at-use]`; re-confirm against the studio's own books and current market data before quoting or acting.
- Seams to `retail-store-operations` (retail attach) and `restaurant-operations` (café) for ancillary mechanics, and `people-operations-hr` for instructor staffing/pay and employment classification.
