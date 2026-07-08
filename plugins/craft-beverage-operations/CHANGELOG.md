# Changelog — craft-beverage-operations

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-07-04

Initial release.

### Added

- **3 agents** — `craft-beverage-operations-lead` (batch/yield planning, COGS per unit, tank/barrel/time capacity, packaging, DTC-vs-wholesale channel margin mix), `tasting-room-and-club-manager` (tasting-room throughput & conversion, club/membership revenue & churn, DTC e-commerce, events), `beverage-distribution-compliance-advisor` (three-tier vs self-distribution economics, distributor relationships & depletion, TTB / state licensing & excise concepts — flags to a professional).
- **4 skills** — `production-planning-and-cogs`, `tasting-room-throughput-and-conversion`, `club-membership-and-dtc-revenue`, `three-tier-and-self-distribution-economics`.
- **Knowledge bank** — `craft-beverage-decision-trees.md` (4 Mermaid trees: channel mix DTC-vs-wholesale, add production capacity, design the club, self-distribute vs distributor) and `craft-beverage-reference-2026.md` (dated reference: production/yield/capacity, COGS & packaging, channel margin / tasting-room / club, and distribution & compliance concepts — each with source placeholder + retrieval date + verify-at-use).
- **5 best-practices** — COGS per unit is the number that hides, capacity is tanks/barrels/time, DTC margin beats wholesale but doesn't scale like it, the club is the recurring-revenue engine, three-tier and licensing are a professional call.
- **2 templates** — craft-beverage-kpi-dashboard, channel-margin-and-cogs-worksheet.
- **2 commands** — `/model-channel-mix`, `/design-club-tier`.

### Scope & verify-at-use

- **Operations and financial decision-support, not legal, tax, or regulatory advice.** The agents make no licensing, franchise-law, or excise determinations and store no PII.
- All benchmarks in `craft-beverage-reference-2026.md` (yields, COGS, channel margins, tasting-room conversion, club churn) are volatile and market-/producer-specific — each carries a retrieval date + `[verify-at-use]`; re-confirm against a current source and the producer's own baseline before quoting or acting.
- The three-tier system, distributor franchise law, TTB and state licensing, direct-ship permits, excise tax, worker classification, wage/tax, and lease law are flagged for a licensed attorney/accountant and the regulator; the agents model the economics and map the structure and do not render the legal/tax call.
