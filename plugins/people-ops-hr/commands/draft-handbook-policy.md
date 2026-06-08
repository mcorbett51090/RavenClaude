---
description: "Draft a handbook policy or lifecycle checklist: plain-language statement, scope, rule, process, and edge cases — consistent with the handbook, with employment-law mechanics flagged for counsel."
argument-hint: "[policy or lifecycle stage + any existing handbook context]"
---

You are running `/people-ops-hr:draft-handbook-policy`. Use `people-ops-generalist` + the `handbook-and-policy` skill.

## Steps
1. Clarify scope: is this a policy (PTO, remote work, code of conduct, etc.) or a lifecycle artifact (onboarding/offboarding checklist)?
2. For a policy, draft it in the standard shape: plain-language statement -> scope -> rule -> process -> edge cases. Check it doesn't contradict adjacent handbook policies.
3. For a lifecycle artifact, build the checklist with an owner per step (onboarding: pre-day-one/day-one/30-60-90; offboarding: access, final pay, equipment, knowledge transfer, HRIS updates).
4. Note the HRIS fields the policy/lifecycle touches and any input controls needed to keep the record canonical; route payroll-affecting items to `finance`.
5. Flag every entitlement/accrual mechanic, FLSA classification, leave, final-pay timing, and termination point for counsel — do not state jurisdiction-specific law as settled fact.
6. Emit the drafted policy/checklist + the Structured Output block (with `People impact:` and `Compliance flags (for counsel, not advice):`).
