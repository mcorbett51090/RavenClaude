# Membership smooths cash but breakage is a liability

**Status:** Pattern
**Domain:** Operations / recurring revenue
**Applies to:** `med-spa-aesthetics`

> Operations rule. No patient PHI/PII. Membership norms are `[verify-at-use]`.

---

## Why this exists

Memberships and packages pre-fill the calendar and smooth cash flow, which is real value. But the included value is a **redemption liability** — services owed at a locked price against future scarce capacity. A practice that books membership sales as banked revenue without modeling redemption is counting a liability as a windfall.

## How to apply

- Price the membership on **redemption plus margin**, not on gross sale.
- Model redemption honestly; breakage reduces the liability but should never be the plan.
- Steer included-value redemption **away from peak** injector/room hours, or cap it.
- Enroll at the moments of trust (consult, post-first-treatment); track redemption rate and churn.
- Hand the economics to `med-spa-operations-lead`; hand enrollment mechanics to `patient-coordinator-lead`.

**Do:** model redemption before counting revenue; protect peak capacity.
**Don't:** treat breakage as the business model; let redemption swamp peak hours.

## Edge cases / when the rule does NOT apply

A pure prepaid package with a short, defined redemption window and no recurring commitment carries less liability than an open-ended membership — but still model redemption before pricing.

## See also

- [`../skills/service-mix-injectables-devices-memberships/SKILL.md`](../skills/service-mix-injectables-devices-memberships/SKILL.md)
- Command: [`/design-membership`](../commands/design-membership.md)

## Provenance

Codifies the `med-spa-operations-lead` house opinions and the design-the-membership decision tree. Benchmarks: [`../knowledge/med-spa-reference-2026.md`](../knowledge/med-spa-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-04 by `claude`_
