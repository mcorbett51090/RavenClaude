# Changelog — auto-repair-shop-operations

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-07-02

Initial release.

### Added

- **3 agents** — `auto-repair-shop-lead` (shop P&L, effective labor rate, bay/tech productivity, labor + parts gross profit, comeback rate, car count/scheduling), `service-advisor-estimator` (write-up, digital vehicle inspection, inspection-to-estimate, approval workflow, declined-work follow-up, ethical upsell), `technician-workflow-manager` (dispatch, flat-rate vs actual hours, WIP/RO aging, parts staging, quality/comeback control).
- **4 skills** — `effective-labor-rate-and-gross-profit`, `estimate-and-dvi-workflow`, `technician-productivity-and-efficiency`, `ro-lifecycle-and-comeback-control`.
- **Knowledge bank** — `auto-repair-shop-decision-trees.md` (4 Mermaid trees: price a job / labor + parts matrix, comeback root-cause triage, declined-work follow-up, tech pay flat-rate vs hourly) and `auto-repair-shop-reference-2026.md` (dated reference: labor economics, productivity/efficiency/proficiency benchmarks `[ESTIMATE]`, the parts-GP matrix, and state authorization/disclosure specifics — each with source placeholder + retrieval date + verify-at-use).
- **5 best-practices** — sell the inspection not the part, the effective labor rate is the real price, a comeback costs you twice, schedule the bay not the day, set the parts matrix once then manage it.
- **2 templates** — repair-order-workflow, shop-kpi-dashboard.
- **2 commands** — `/build-estimate`, `/diagnose-comebacks`.

### Scope & verify-at-use

- **Operations and financial decision-support, not legal, tax, or OEM-warranty advice.** The agents store no customer PII.
- All labor-rate norms, labor-guide times, parts-margin figures, productivity/efficiency/proficiency benchmarks (`[ESTIMATE]`), and state estimate-authorization/disclosure rules in `auto-repair-shop-reference-2026.md` are volatile and market-/shop-/jurisdiction-specific — each carries a retrieval date + `[verify-at-use]`; re-confirm against the shop's own numbers, the current labor guide, or the local statute before quoting or acting.
- Distinct model from `automotive-dealership`, `fleet-logistics`, and `skilled-trades-contracting` (cross-linked, not duplicated).
