---
name: prior-auth-and-claims
description: "Run the behavioral-health billing front-end: verify eligibility, assemble and track prior authorizations, select the correct behavioral CPT code, triage claim denials, and keep payer disclosures consent-correct under 42 CFR Part 2 + HIPAA — never upcoding, PHI placeholdered, codes verified against current policy."
---

# Prior Auth & Claims

## Eligibility before scheduling
Verify the active coverage and behavioral benefit first: covered benefit, copay/coinsurance/deductible, session limits, in/out-of-network, and the auth-required flag. No scheduling against unconfirmed coverage. **Not clinical advice** — clinical level-of-care questions route to a clinician.

## Prior authorization
Confirm whether the plan requires auth for the service/CPT (unknown → treat as required). Assemble the request packet: codes, units, diagnosis, medical-necessity attachment (from the note). An auth is confirmed *in writing* — capture the auth number and unit count — before sessions are scheduled against it. An assumed auth is a denied claim. Re-auth before units run out.

## Behavioral CPT-code selection
The code reflects the service rendered — never the reimbursement wanted. Time and modality and who's present determine the code (e.g. eval vs 30/45/60-min individual vs family with/without client vs group + telehealth modifier/POS). Never upcode. Quote every code as `[verify-at-build]` against the current CPT set and the specific payer's policy before treating it as final.

## Claims basics & denial triage
Clean-claim elements, then triage denials by *cause* — eligibility/auth, code/diagnosis mismatch, medical-necessity documentation, timely filing — because the cause picks the fix. Route documentation-driven denials to `clinical-documentation-specialist`; route denials analytics and payer-contract modeling to `medical-revenue-cycle`.

## 42 CFR Part 2 + HIPAA in billing
Disclosing SUD information to a payer can need specific Part 2 consent a general authorization doesn't cover — assume Part 2 applies when unsure, and gate the disclosure on consent. PHI (member ID, name, DOB) stays in the billing system; checklists use placeholders.

## Output
An eligibility + prior-auth checklist, a CPT-selection rationale (`[verify-at-build]`), or a denial-cause triage — never upcoded, PHI placeholdered, Part 2 disclosures consent-gated, deep RCM routed to `medical-revenue-cycle`.
