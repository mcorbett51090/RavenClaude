---
description: "Design a med-spa membership / package priced on redemption plus margin, not gross sale — included value modeled against redemption, redemption steered away from peak scarce capacity, enrollment wired into the consult and post-treatment moments, with breakage treated as a liability not a windfall (verify-at-use on norms)."
argument-hint: "[goal (cash-smoothing / pre-fill / drive a service) + proposed included value + price + peak-capacity picture]"
---

You are running `/med-spa-aesthetics:design-membership`. Use `med-spa-operations-lead` (economics) + `patient-coordinator-lead` (enrollment) and the `service-mix-injectables-devices-memberships` skill.

> Operations decision-support, not legal, tax, or medical advice. Membership terms can carry payment-processor and consumer-protection implications — flag them `[verify-at-use]` and route to a professional. No patient PHI/PII — work in rates and models, never a patient record.

## Steps

1. State the membership **goal** (smooth cash / pre-fill the book / drive a specific service) — the goal shapes the design.
2. Traverse the **design the membership** tree in `knowledge/med-spa-decision-trees.md`.
3. Model the included value against **redemption**, not gross sale; price on redemption + margin. Model breakage honestly — it reduces the liability but is never the plan.
4. Check whether the included value pre-commits **peak** injector/room hours; if so, cap or steer redemption to off-peak to protect scarce capacity.
5. Wire enrollment into the consult and post-first-treatment moments (`patient-coordinator-lead`); define redemption-rate and churn tracking.
6. Flag any payment/consumer-protection specific `[verify-at-use]` and route it.
7. Emit using `templates/med-spa-kpi-dashboard.md` (mix + membership sections) + the Structured Output block, with the price, the modeled redemption, and the capacity it pre-commits.
