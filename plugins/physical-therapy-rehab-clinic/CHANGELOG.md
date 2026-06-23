# Changelog — physical-therapy-rehab-clinic

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-06-22

Initial release.

### Added

- **3 agents** — `clinic-operations-lead` (scheduling & capacity, POC visit cadence, patient flow, no-show management, productivity), `clinical-documentation-compliance` (defensible POC documentation, certification/recertification timing, medical necessity, skilled care, therapy-threshold + KX concept, signatures), `billing-and-revenue` (CPT timed codes & the 8-minute rule, units, GP/KX/59 modifiers, denial prevention & appeals, payor mix).
- **5 skills** — `schedule-and-capacity-planning`, `defensible-documentation`, `therapy-billing-and-units`, `denial-prevention-and-appeals`, `plan-of-care-management`.
- **Knowledge bank** — `pt-clinic-decision-trees.md` (4 Mermaid trees: 8-minute-rule unit calculation, documentation defensibility / medical necessity, plan certification vs recertification timing, denial triage) and `pt-clinic-reference-2026.md` (dated reference: timed-vs-untimed CPT, therapy-threshold + KX concept, common payor rules — every figure carries a source placeholder + retrieval date + verify-at-use; advisory numbers marked [ESTIMATE]).
- **8 best-practices** — document medical necessity every visit, the 8-minute rule governs timed units, certify the plan of care before it lapses, skilled care must be skilled in the note, match the modifier to the discipline, track no-shows as a revenue leak, defensible notes beat appeals, verify payor rules before you bill.
- **3 templates** — plan-of-care, daily-note-skeleton, denial-appeal-letter.
- **3 commands** — `/calc-therapy-units`, `/review-documentation`, `/plan-clinic-capacity`.
- **1 advisory hook** — `check-pt-documentation-smells.sh` (3 checks: timed minutes with no unit count, "tolerated well" boilerplate with no skilled-care justification, a plan of care with no certification/recert date; `PTCLINIC_STRICT=1` to block). Does not read or store PII.

### Advisory & verify-at-use

- **Advisory domain knowledge only — not medical, legal, or billing/coding advice.** Every regulatory/payor specific (the 8-minute-rule variant, CPT status, the Medicare therapy threshold, KX/modifier rules, certification windows, signature rules, denial codes, cancellation rules) carries a retrieval date + `verify-at-use`, or is marked `[unverified — training knowledge]` / `[ESTIMATE]`. No patient PII anywhere.

### Seams

- Generic medical revenue-cycle → `medical-revenue-cycle`; mental-health / behavioral clinics → `behavioral-health-practice` (cross-linked, not duplicated).
