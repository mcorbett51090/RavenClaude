# Changelog — travel-agency-tour-operations

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-07-02

Initial release.

### Added

- **3 agents** — `travel-agency-operations-lead` (agency P&L, revenue model, supplier mix, host-agency splits, booking systems, E&O / seller-of-travel risk), `itinerary-and-booking-specialist` (itinerary design, multi-supplier booking, pricing/quoting, FIT vs group, changes/cancellations, disruption service-recovery, documentation), `supplier-and-commission-manager` (supplier relationships, commission tracking & recovery, net vs commissionable, BSP/ARC settlement, preferred-supplier/consortia).
- **4 skills** — `itinerary-design-and-quoting`, `supplier-and-commission-management`, `group-vs-fit-trip-operations`, `service-recovery-and-disruption`.
- **Knowledge bank** — `travel-agency-decision-trees.md` (4 Mermaid trees: revenue model commission-vs-fee-vs-markup, group vs FIT structuring, disruption/service-recovery, commission-recovery chase) and `travel-agency-reference-2026.md` (dated reference: revenue models, commission norms by supplier type `[ESTIMATE]`, BSP/ARC basics, cancellation-policy & group patterns, regulatory/risk touchpoints — each with source placeholder + retrieval date + verify-at-use).
- **5 best-practices** — charge a fee when the commission won't cover the work, chase every commission it is your margin, document the itinerary and every change, build the group block before you sell it, service recovery is the repeat booking.
- **2 templates** — itinerary-and-quote, supplier-commission-tracker.
- **2 commands** — `/build-itinerary-quote`, `/reconcile-commissions`.

### Scope & verify-at-use

- **Advisory domain operations knowledge, not legal, tax, or financial advice.** The agents store no traveler PII — they work in trip structure, cohorts, placeholders, and internal booking IDs.
- All supplier fare rules, commission rates, cancellation penalties, BSP/ARC settlement mechanics, consortia benefits, and seller-of-travel / E&O requirements in `travel-agency-reference-2026.md` are volatile and supplier-/jurisdiction-specific — each carries a retrieval date + `[verify-at-use]`; re-confirm against the live supplier agreement, settlement statement, or the jurisdiction before quoting or acting.
- Seams to `ravenclaude-core` for domain-neutral protocols and security/privacy verdicts; binding legal/tax questions escalate to counsel or the agency's financial authority.
