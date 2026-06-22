# Route the claim to medical or vision deliberately

**Status:** Absolute rule
**Domain:** Billing / payor routing
**Applies to:** `optometry-eyecare-practice`

> Advisory operations rule, not billing advice. Payor rules and codes are `[verify-at-use]`. No PII/PHI.

---

## Why this exists

The defining feature of eye-care billing is that the **same patient** can be a medical insurance claim or a vision plan claim depending on **why they came in**. Routing it wrong is the most common recurring way an eye-care practice loses money — to a denial, an under-payment, or a patient surprised by a bill.

## How to apply

- Decide on the **chief complaint and what the visit actually addressed**, never on which payor is convenient or pays more.
- Routine refraction / well-vision → typically the vision plan. A medical complaint or diagnosis (dry eye, diabetic eye exam, glaucoma, foreign body, sudden change) → typically medical.
- A visit with both components → split per the specific payor's rules (`[verify-at-use]`); if a split isn't allowed, route to the dominant reason for the visit.
- Make the decision at the **front desk / at scheduling**, not retroactively at billing.

**Do:** traverse the routing decision tree; document the basis for the route.
**Don't:** route to chase the richer benefit; reverse-engineer the route from the desired payment.

## Edge cases / when the rule does NOT apply

The clinical diagnosis is the doctor's; routing follows the documented encounter. This rule governs the *operations* decision of which payor, not the clinical call.

## See also

- [`./code-to-the-chief-complaint.md`](./code-to-the-chief-complaint.md), [`./document-medical-necessity-for-medical-claims.md`](./document-medical-necessity-for-medical-claims.md)
- [`../skills/medical-vs-vision-billing/SKILL.md`](../skills/medical-vs-vision-billing/SKILL.md)

## Provenance

Codifies `front-office-billing` house opinion (#1) and the medical-vs-vision routing decision tree. Payor-specific rules: [`../knowledge/eyecare-practice-reference-2026.md`](../knowledge/eyecare-practice-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-06-22 by `claude`_
