# Changelog — residential-real-estate-brokerage

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-07-02

Initial release.

### Added

- **3 agents** — `residential-brokerage-lead` (brokerage/team P&L, lead-to-close pipeline, commission splits/caps, recruiting & retention, agency/fair-housing compliance, brand/lead-gen), `listing-and-transaction-coordinator` (CMA/pricing, listing prep + MLS + marketing launch, contract-to-close timeline, contingencies, deadlines, docs), `buyer-agent-advisor` (buyer needs analysis, showings, offer & negotiation strategy, financing coordination, closing).
- **4 skills** — `cma-and-pricing-strategy`, `listing-launch-and-marketing`, `transaction-timeline-management`, `commission-split-and-cap-economics`.
- **Knowledge bank** — `residential-brokerage-decision-trees.md` (4 Mermaid trees: price a listing/CMA, represent buyer vs seller / dual-agency conflict, offer & counter strategy, commission split-vs-cap model) and `residential-brokerage-reference-2026.md` (dated reference: fair-housing protected classes, commission/comp-model norms `[ESTIMATE]`, typical contract-to-close milestones & contingency periods, pipeline/pricing benchmarks — each with source placeholder + retrieval date + verify-at-use).
- **5 best-practices** — price to the comps not the seller's ego, fair housing is non-negotiable, contract-to-close is a deadline checklist, disclose agency before you represent, recruit and retain on economics and support.
- **2 templates** — listing-launch-plan, transaction-timeline-checklist.
- **2 commands** — `/build-cma`, `/manage-transaction-timeline`.

### Scope & verify-at-use

- **Advisory domain operations knowledge, not legal, financial, real-estate-license, or lending advice.** This domain is fair-housing sensitive; the agents never steer and store no client PII.
- All commission rates, contingency periods, agency rules, and protected-class lists in `residential-brokerage-reference-2026.md` are volatile and jurisdiction-/agreement-specific — each carries a retrieval date + `[verify-at-use]`; re-confirm against current law, the specific contract, and the brokerage's own agreements before quoting or acting.
- Seams to `mortgage-lending` (buyer financing) and the `title-escrow-settlement` team (closing); cross-links (not duplication) to `property-management` and `commercial-real-estate` (distinct models).
