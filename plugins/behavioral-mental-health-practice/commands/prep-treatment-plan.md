---
description: "Prepare a compliant outpatient behavioral health treatment plan structure — including medical-necessity framing, measurable goals, intervention listing, and MBC instrument cadence — for a specified presenting problem and payer type."
argument-hint: "[context, e.g. 'MDD patient, commercial payer, 12-session auth, PHQ-9 at 16, no current MBC workflow']"
---

You are running `/behavioral-mental-health-practice:prep-treatment-plan`. Use the
`clinical-documentation-advisor` discipline and the `clinical-documentation-and-treatment-planning`
skill.

## Steps

1. Gather or confirm context: the presenting diagnosis or problem area (framed at the practice
   operations level, not as clinical advice), the payer type (commercial, Medicaid, Medicare, self-
   pay), and any prior authorization requirements or known payer-specific treatment-plan standards.

2. Lay out the required treatment plan components per the skill playbook: presenting problem →
   diagnosis linkage → functional impairment → measurable SMART goals → intervention modalities
   (listed, not clinically endorsed) → frequency and duration → signature fields.

3. Draft the medical-necessity statement pattern for this service type, linking the diagnosis →
   functional impairment → treatment rationale in language that survives a utilization review.

4. Recommend an MBC instrument from the publicly available set (PHQ-9, GAD-7, PCL-5, etc.) based
   on the presenting problem. Specify the recommended cadence (every session or every 2–4 weeks)
   and the EHR workflow to capture and trend scores.

5. Specify the treatment-plan update cadence: authorization renewal trigger, 90-day maximum
   between updates, and any payer-specific requirements.

6. Output a filled treatment-plan template using `templates/treatment-plan.md` as the base, with
   the medical-necessity statement, one sample SMART goal per presenting domain, the MBC plan,
   and the update cadence.

7. Emit the Structured Output block with handoffs: `behavioral-billing-compliance-advisor` for
   authorization-request documentation; `telehealth-operations-lead` if the plan is for a telehealth
   patient.
