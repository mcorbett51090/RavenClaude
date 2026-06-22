# Changelog — optometry-eyecare-practice

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-06-22

Initial release.

### Added

- **3 agents** — `practice-operations-lead` (scheduling, pretesting workflow, exam-room/lane flow, recall/recare cadence, capacity), `optical-dispensary-manager` (frames & lens inventory, optical capture rate & sales, lab orders, managed-vision-care formularies), `front-office-billing` (medical-vs-vision billing split, eligibility, CPT/coding, payor mix, claims/denials).
- **5 skills** — `schedule-and-recall-management`, `exam-flow-and-pretesting`, `optical-capture-and-dispensary`, `medical-vs-vision-billing`, `eligibility-and-claims`.
- **Knowledge bank** — `eyecare-practice-decision-trees.md` (4 Mermaid trees: medical-vs-vision routing, recall cadence by exam type, optical capture improvement, claim denial triage) and `eyecare-practice-reference-2026.md` (dated reference: vision-plan vs medical-insurance concepts, capture-rate benchmarks `[ESTIMATE]`, recall intervals — each with source placeholder + retrieval date + verify-at-use).
- **8 best-practices** — route the claim to medical or vision deliberately, verify eligibility before the visit, code to the chief complaint, document medical necessity for medical claims, capture rate is the optical profit lever, dispense from managed-care formularies knowingly, track frames inventory turns, recall drives the schedule.
- **3 templates** — practice-kpi-dashboard, recall-campaign-plan, billing-route-decision.
- **3 commands** — `/route-claim`, `/plan-recall`, `/review-optical-capture`.
- **1 advisory hook** — `check-eyecare-billing-smells.sh` (3 checks on .md/.txt; `EYECARE_STRICT=1` to block).

### Scope & verify-at-use

- **Advisory domain operations knowledge, not medical, legal, coding, or billing advice.** The agents store no PII/PHI.
- All payor rules, CPT/coding specifics, vision-plan benefit structures, medical-necessity criteria, capture-rate benchmarks (`[ESTIMATE]`), and clinical recall intervals in `eyecare-practice-reference-2026.md` are volatile and payor-/protocol-specific — each carries a retrieval date + `[verify-at-use]`; re-confirm against the payor, clearinghouse, or clinical protocol before quoting or acting.
- Distinct practice model from `dental-practice` and `veterinary-practice` (cross-linked, not duplicated); shares the revenue-cycle seam with `medical-revenue-cycle`.
