---
description: "Plan an open-enrollment cycle and map the compliance calendar: backward-planned timeline, eligibility, QLE/special enrollment, carrier/EDI coordination, and COBRA/HIPAA/ACA-1095/ERISA-5500 obligations — educational, not legal advice."
argument-hint: "[effective date + group size + ALE status + lines of coverage + carriers]"
---

You are running `/insurance-life-health-benefits:plan-open-enrollment`. Use `enrollment-and-compliance-lead` + the `enrollment-and-compliance` skill.

## Steps
1. Backward-plan the timeline from the effective date: system build/test, communications, the decision window, processing, and the carrier/EDI cutover — each with its lead time.
2. Write the eligibility rules: classes, waiting periods, hours/ACA measurement, dependent rules, and the QLE/special-enrollment windows. Ambiguity here becomes a claim dispute.
3. Map the compliance calendar with triggers, owners, and current-year deadlines (`[verify-at-build]`): COBRA notices, HIPAA special enrollment, ACA 1095-C/1094-C, ERISA Form 5500 + SAR, SPD/SBC distribution, recurring notices.
4. Build the carrier-coordination checklist: EDI/834 feeds, eligibility reconciliation cadence, and the carrier confirmation step. Reconcile every cycle, not at audit.
5. Route: plan-design problems surfaced during enrollment → benefits-advisor; the renewal/rate story → underwriting-and-actuarial-analyst; ongoing HR administration → people-ops-hr.
6. Emit the enrollment plan + compliance calendar + the Structured Output block (with `Not advice:` and `Coverage gaps flagged:`). Name the carrier/ERISA-counsel confirmation step.
