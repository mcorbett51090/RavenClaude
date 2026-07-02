# Changelog — salon-spa-operations

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-07-02

Initial release.

### Added

- **3 agents** — `salon-spa-operations-lead` (chair/room utilization, service mix, retail attach, membership/package revenue, the staffing model), `front-desk-booking-manager` (online booking, no-show / late-cancel policy & deposits, rebooking at checkout, waitlist, reminders), `stylist-chair-economics-advisor` (commission tiers, booth rent, product cost, prebooking, clientele building, retention).
- **4 skills** — `booking-and-no-show-control`, `chair-and-room-utilization`, `retail-attach-and-service-mix`, `compensation-models-commission-vs-booth-rent`.
- **Knowledge bank** — `salon-spa-decision-trees.md` (4 Mermaid trees: compensation model commission-vs-booth-rent, no-show policy & deposit, rebook at checkout, price the service menu) and `salon-spa-reference-2026.md` (dated reference: utilization & capacity, retail-attach & service mix, no-show/cancel/rebooking, and compensation-model concepts — each with source placeholder + retrieval date + verify-at-use).
- **5 best-practices** — rebook before they leave the chair, a no-show is inventory you can't resell, retail is margin the service can't match, price the menu on time and demand, choose the comp model deliberately.
- **2 templates** — salon-kpi-dashboard, service-menu-and-pricing.
- **2 commands** — `/set-noshow-policy`, `/model-compensation`.

### Scope & verify-at-use

- **Operations and financial decision-support, not legal, tax, or employment-classification advice.** The agents store no client PII.
- All benchmarks in `salon-spa-reference-2026.md` (utilization, retail-attach, no-show rates, commission splits, booth rent) are volatile and market-/model-specific — each carries a retrieval date + `[verify-at-use]`; re-confirm against a current source and the shop's own baseline before quoting or acting.
- Worker classification (employee vs 1099 booth-renter), wage/tax, lease law, and deposit/payment-processor / consumer-protection rules are flagged for a licensed professional; the agents model the economics and do not render the legal call.
