---
description: "Design an outpatient behavioral-health intake-to-first-session flow with no-show, telehealth, caseload, and referral handling — self-service-first, PHI-aware, clinical steps routed to a clinician."
argument-hint: "[current intake/scheduling pain + setting (in-person/telehealth) + payer mix]"
---

You are running `/behavioral-health-practice:design-intake-flow`. Use `practice-operations-lead` + the `intake-and-scheduling` skill.

## Steps
1. Map the current intake-to-first-session path; name where friction or drop-off lives (no-shows, cold referrals, telehealth fails).
2. Design the flow: first contact → screening (clinical step → route to clinician) → eligibility hand-off (→ billing-and-authorization-lead) → scheduling → telehealth-readiness check → first session. Mark each step self-service vs human-required.
3. If no-shows are the pain: add a reminder cadence + a fair cancellation policy + waitlist backfill, and name the tracked metric.
4. If telehealth: add the readiness check (tech/consent/location) and flag cross-state-licensure to clinician/compliance.
5. Keep all PHI in the EHR — examples use placeholders (`[Client]`, `[DOB]`). Route any clinical-appropriateness/risk call to a licensed clinician.
6. Emit the flow + the Structured Output block (with `Not clinical advice:` and `PHI posture:` lines).
