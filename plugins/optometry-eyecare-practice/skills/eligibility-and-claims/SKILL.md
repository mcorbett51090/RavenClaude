---
name: eligibility-and-claims
description: "Run the eye-care claims loop: verify both medical and vision eligibility before the visit, manage payor mix, and triage denials by cause (eligibility, coding/medical-necessity, wrong-payor-routed, timely-filing). Payor specifics are verify-at-use."
---

# Eligibility & Claims

Close the loop from benefit check to clean claim to resolved denial.

> **Advisory, not billing advice.** Payor rules, timely-filing windows, and eligibility response formats vary by payor and change — `[verify-at-use]`. No PII/PHI; work in patterns and policy.

## Verify eligibility before the visit

The single highest-yield fix for collection failures is knowing the benefit **before the patient arrives**, not at check-in. Check **both** medical and vision benefits at scheduling because the visit may route either way (see [`../medical-vs-vision-billing/SKILL.md`](../medical-vs-vision-billing/SKILL.md)).

| Step | When | Catches |
|---|---|---|
| Medical + vision benefit check | At scheduling | No-benefit surprises, exhausted allowances, wrong plan on file |
| Re-confirm at check-in | Day of | Plan changes since scheduling |

## Read the payor mix

Know the share of visits/revenue by payor and the effective reimbursement by plan. The mix is a strategy lens, not a line you discover in adjustments.

## Triage denials by cause

Group denials, then fix the **process** that produced the group:

| Denial cause | Fix the process |
|---|---|
| Eligibility / no benefit | Pre-visit eligibility step (above) |
| Coding / medical necessity | Code to the encounter; document necessity |
| Wrong payor routed (medical vs vision) | The routing decision (separate skill) |
| Timely filing | Submission cadence + worklist |

## Anti-patterns

- Discovering eligibility at checkout instead of at scheduling.
- Working denials one-by-one instead of by cause cluster.
- Treating payor mix as an accident rather than a managed lens.

## See also

- [`../medical-vs-vision-billing/SKILL.md`](../medical-vs-vision-billing/SKILL.md); traverse the **claim denial triage** tree in [`../../knowledge/eyecare-practice-decision-trees.md`](../../knowledge/eyecare-practice-decision-trees.md).
- Best practices: [`../../best-practices/verify-eligibility-before-the-visit.md`](../../best-practices/verify-eligibility-before-the-visit.md).
- Shared revenue-cycle mechanics: [`../../../medical-revenue-cycle/CLAUDE.md`](../../../medical-revenue-cycle/CLAUDE.md).
