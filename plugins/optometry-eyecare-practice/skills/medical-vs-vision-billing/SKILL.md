---
name: medical-vs-vision-billing
description: "Route an eye-care visit to medical insurance vs the vision plan deliberately, on the chief complaint and what the visit addressed. Code to the encounter, document medical necessity for medical claims, and flag every payor/coding specific verify-at-use."
---

# Medical vs Vision-Plan Billing

The routing decision that makes optometry billing distinct: the **same patient** can be a medical insurance claim or a vision plan claim depending on **why they came in**.

> **Advisory, not billing advice.** CPT codes, payor rules, and medical-necessity criteria are volatile and payor-specific. Every specific here is `[verify-at-use]` — confirm against the payor/clearinghouse before it drives a claim. No PII/PHI.

## The split

| Concept | Vision plan | Medical insurance |
|---|---|---|
| Typical trigger | Routine refraction, "new glasses", well-vision exam | Medical chief complaint or diagnosis (dry eye, diabetic eye exam, glaucoma, foreign body, sudden change) |
| What it covers | Refraction, materials allowance (frames/lenses), routine exam | The medical evaluation/management of an eye condition |
| Decided on | The reason for the visit and what was addressed | The reason for the visit and what was addressed |

**The rule:** route on the **chief complaint and what the visit actually addressed**, not on which payor is convenient or which has a richer benefit. A visit can have both a routine and a medical component — split per payor rules (`[verify-at-use]`).

## Code to the chief complaint

The exam code + diagnosis follow the documented reason for the visit. Coding around coverage instead of around the encounter is how denials and audits begin.

## Document medical necessity

Every medical claim needs the complaint, findings, and plan in the record to survive a denial or audit. No documentation, no medical claim.

## Anti-patterns

- Routing to whichever payor pays more, regardless of the chief complaint.
- Coding to fit coverage rather than the encounter.
- A medical claim with no medical-necessity documentation.

## See also

- Traverse the **medical-vs-vision-plan billing routing** tree in [`../../knowledge/eyecare-practice-decision-trees.md`](../../knowledge/eyecare-practice-decision-trees.md).
- [`../eligibility-and-claims/SKILL.md`](../eligibility-and-claims/SKILL.md), [`../../templates/billing-route-decision.md`](../../templates/billing-route-decision.md).
- Best practices: [`../../best-practices/route-the-claim-to-medical-or-vision-deliberately.md`](../../best-practices/route-the-claim-to-medical-or-vision-deliberately.md), [`../../best-practices/code-to-the-chief-complaint.md`](../../best-practices/code-to-the-chief-complaint.md), [`../../best-practices/document-medical-necessity-for-medical-claims.md`](../../best-practices/document-medical-necessity-for-medical-claims.md).
- The shared medical revenue-cycle rails: [`../../../medical-revenue-cycle/CLAUDE.md`](../../../medical-revenue-cycle/CLAUDE.md).
