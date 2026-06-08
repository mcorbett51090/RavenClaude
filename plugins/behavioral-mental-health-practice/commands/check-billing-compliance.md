---
description: "Run a billing compliance review for an outpatient behavioral health practice — covering 42 CFR Part 2 vs HIPAA disclosure handling, prior authorization status and burn rate, CPT code and units use, and denial pattern triage."
argument-hint: "[context, e.g. 'SUD program, 3 open authorizations expiring in 30 days, 15% denial rate on 90837, no Part 2 consent workflow']"
---

You are running `/behavioral-mental-health-practice:check-billing-compliance`. Use the
`behavioral-billing-compliance-advisor` discipline and the `behavioral-billing-and-authorization`
skill.

## Steps

1. Gather or confirm context: whether the practice treats SUD patients (Part 2 applicability),
   the current authorization tracking method, the top CPT codes billed, and the current denial
   rate and top denial categories (if known).

2. **Part 2 check:** if the practice treats SUD patients, traverse the Part-2-vs-HIPAA tree in
   `knowledge/bh-practice-decision-trees.md`. Confirm: (a) a Part 2-compliant consent-to-disclose
   form is in the intake packet, (b) the disclosure workflow distinguishes Part 2 records from HIPAA-
   only records, (c) staff are aware that TPO does not apply to Part 2 records.

3. **Authorization audit:** for each open authorization in context, calculate units remaining and
   coverage-weeks remaining using `scripts/bh_calc.py auth-burn`. Flag any authorizations within
   10–14 business days of expiration without a submitted renewal.

4. **CPT and units review:** check the billed CPT codes against the documented session times in
   context. Flag any mismatch (e.g., 90837 billed for a session documented at under 53 minutes).
   Confirm telehealth billing modifiers (95/GT, POS 02/10) are used correctly if telehealth services
   are billed.

5. **Denial triage:** categorize denials by type (medical necessity, authorization, eligibility,
   coding error, timely filing). For medical-necessity denials, escalate to
   `clinical-documentation-advisor` for note structure remediation. For auth denials, confirm the
   peer-to-peer request path.

6. Output a compliance checklist with pass/fail status per category, priority remediation actions,
   and a Part 2 consent workflow if it is missing.

7. Emit the Structured Output block with handoffs: `clinical-documentation-advisor` for
   medical-necessity documentation; `telehealth-operations-lead` for telehealth billing modifiers.
