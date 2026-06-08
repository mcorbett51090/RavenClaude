---
description: "Assemble an eligibility + prior-authorization request checklist for a behavioral-health service — codes, units, medical necessity, Part 2 consent — never upcoded, PHI placeholdered, codes [verify-at-build]."
argument-hint: "[service/CPT + payer + new-or-continuing + any prior denial]"
---

You are running `/behavioral-health-practice:prep-prior-auth`. Use `billing-and-authorization-lead` + the `prior-auth-and-claims` skill.

## Steps
1. Eligibility first: confirm active coverage + behavioral benefit, copay/coinsurance/deductible, session limits, in/out-of-network, and the auth-required flag (unknown → treat as required).
2. Select the candidate behavioral CPT code(s) by the service rendered (time/modality/participants); never upcode; mark every code `[verify-at-build]` against the current CPT set + payer policy.
3. Assemble the prior-auth request packet: codes, units, diagnosis, medical-necessity attachment (route documentation gaps to clinical-documentation-specialist).
4. Add the verify-auth-before-scheduling gate (capture auth number + unit count in writing); note re-auth before units run out.
5. Part 2 check: if SUD content is disclosed to the payer, require specific consent — a general HIPAA authorization is not enough.
6. Keep PHI (member ID, name, DOB) out — use placeholders. Route deep denials analytics / payer-contract modeling to medical-revenue-cycle; clinical questions to a clinician.
7. Emit the checklist + the Structured Output block (with `Not clinical advice:` and `PHI posture:` lines).
