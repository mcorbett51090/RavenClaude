# Changelog — childcare-early-education

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-07-02

Initial release.

### Added

- **3 agents** — `childcare-center-lead` (enrollment/waitlist, capacity vs licensed ratios, tuition model, staffing to ratio, family retention, P&L), `enrollment-and-family-manager` (tour-to-enroll conversion, waitlist, enrollment paperwork, family communication, tuition & CCDF/state subsidy billing), `classroom-ratio-compliance-advisor` (ratio & group-size by age, licensing readiness, staff qualifications, health & safety, incident documentation).
- **4 skills** — `enrollment-and-waitlist-management`, `ratios-and-licensing-compliance`, `tuition-and-subsidy-billing`, `staffing-to-ratio-scheduling`.
- **Knowledge bank** — `childcare-decision-trees.md` (4 Mermaid trees: staff a room to ratio, enrollment/waitlist decision, tuition vs subsidy billing route, licensing-readiness triage) and `childcare-reference-2026.md` (dated reference: ratio/group-size norms by age `[ESTIMATE]`, CCDF/subsidy basics, licensing domains — each with source placeholder + retrieval date + verify-at-use, state-specific).
- **5 best-practices** — ratios are a floor not a target, staff-to-ratio is the cost model, enroll the waitlist before you discount, licensing compliance is continuous not an inspection day, family communication is the retention engine.
- **2 templates** — enrollment-funnel-tracker, ratio-staffing-plan.
- **2 commands** — `/plan-staffing-to-ratio`, `/model-enrollment`.

### Scope & verify-at-use

- **Advisory domain operations knowledge, not legal, licensing, or financial advice.** The agents make no licensing determinations and store **no child or family PII**.
- All child:staff ratios, group-size caps, staff-qualification rules, subsidy program rules (CCDF and state variants), and licensing requirements in `childcare-reference-2026.md` are **state-specific and volatile** — each carries a retrieval date + `[verify-at-use, state-specific]`; re-confirm against the current state licensing regulation and funding agency before it drives a staffing plan, an enrollment cap, or a bill.
- Seam to the adjacent (distinct) `edtech-partner-success` plugin for broader early-education partner/programmatic relationships (cross-linked, not duplicated).
