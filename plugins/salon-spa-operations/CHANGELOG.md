# Changelog — salon-spa-operations

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-06-25

Initial release.

### Added

- **3 agents** — `salon-spa-operations-lead` (front desk/client experience, the commission-vs-booth-rental decision, stylist staffing/retention, routing), `booking-and-retention-analyst` (calendar utilization, online booking, double-booking + color processing-time overlap, gap-filling, the no-show/deposit policy, rebooking rate, retention), `service-menu-and-pricing-strategist` (service-menu design, pricing + price increases, retail attachment, service-mix margin).
- **5 skills** — `design-service-menu-and-pricing`, `set-no-show-and-deposit-policy`, `choose-commission-vs-booth-rental`, `improve-rebooking-rate`, `plan-retail-attachment`.
- **Knowledge bank** — `salon-spa-operations-decision-trees.md` (4 Mermaid trees: compensation model commission/booth-rental/hybrid, empty-chair diagnosis demand-vs-scheduling, price increase, deposit policy) and `salon-spa-operations-reference-2026.md` (dated benchmark map; re-verify before quoting).
- **7 best-practices** — rebooking rate is the core KPI, name the classification before the comp split, no-show policy needs a deposit behind it, measure chair utilization not bookings, book the color processing gap don't double-book it, retail attachment is the margin lifeline, raise prices on a schedule and communicate them.
- **3 templates** — service-menu-and-pricing, no-show-deposit-policy, compensation-model-comparison.
- **3 commands** — `/design-service-menu`, `/set-no-show-policy`, `/compare-comp-models`.
- **1 advisory hook** — `check-salon-anti-patterns.sh` (3 checks on `.md`; `SALON_STRICT=1` to block).

### Verify-at-use

- All benchmark numbers in `salon-spa-operations-reference-2026.md` (rebooking %, retail-attachment %, commission splits, no-show rates, booth-rent ranges) — volatile; re-confirm against your own POS/booking actuals and local market before quoting.
- All worker-classification and tax statements — jurisdiction-dependent; escalate to `people-operations-hr` (classification) and `accounting-bookkeeping` (tax) before relying on them.
