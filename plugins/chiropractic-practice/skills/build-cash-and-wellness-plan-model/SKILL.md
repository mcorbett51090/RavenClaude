---
name: build-cash-and-wellness-plan-model
description: "Price a compliant cash / membership / wellness-plan model for a chiropractic practice: a supportive-care membership priced to the clinical cadence and above delivery cost, the covered-active-care vs cash-maintenance boundary drawn cleanly, and the ABN/discount-compliance guardrails so a plan isn't an illegal inducement or a way to bill maintenance as active. Reach for it when designing memberships or a cash model. Used by `chiropractic-practice-lead` (primary)."
---

# Skill: build-cash-and-wellness-plan-model

> **Invoked by:** `chiropractic-practice-lead` (primary). Compliance boundary co-owned with `chiro-billing-compliance-specialist`.
>
> **When to invoke:** designing a membership / cash / wellness-plan model, or setting cash-visit pricing.
>
> **Output:** a priced, compliant cash/membership model with the covered/cash boundary and discount guardrails. Regulatory specifics are `[verify-at-use]` and flagged for counsel.

## Procedure

1. **Segment the model by care type first.** Active, medically-necessary care follows the insurance/covered path; supportive/maintenance and wellness care is the cash/membership model. The membership is for the *maintenance* patient — not a discount on covered care.
2. **Cost the delivered visit.** Provider time, room, supplies, front-desk, and overhead per visit — the membership floor is above this, not below.
3. **Price to the clinical cadence.** A wellness-cadence patient (e.g. 1-2x/month) sets the visit count the membership covers; price the monthly fee to that cadence and to value, with a margin. A plan that assumes fewer visits than patients use loses money; one priced above what they'll use churns.
4. **Draw the covered/cash boundary explicitly.** Document that membership visits are supportive/maintenance (non-covered) care and that active covered care is billed separately — so nothing bills as both.
5. **Apply the compliance guardrails.** Cash discounts and memberships can implicate discount, dual-fee-schedule, and inducement rules that are state- and payer-specific — keep the cash fee defensible, avoid routinely waiving insured patients' cost-share, and flag the ABN for the transition. **This is where you route to a certified compliance professional / counsel — `[verify-at-use]`.**
6. **Model the P&L.** Members × fee − delivery cost = contribution; sensitivity on utilization and churn. Show the practice lead the break-even utilization.

## Worked example

> Wellness membership for maintenance patients.

- Cost/visit ≈ \$28 delivered. Cadence ≈ 2 visits/month.
- Fee → \$79/month (covers 2 supportive visits + a member rate on extras), floor cleared, priced to value.
- Boundary → membership = supportive/maintenance only; any flare that becomes active care is re-examined and billed on the covered path with fresh necessity.
- Compliance → cash fee defensible, no insured cost-share waivers; state discount/inducement rules flagged for counsel.

## Guardrails

- **A membership is not a discount on covered care** — that blurs the necessity line and invites audit.
- **Never routinely waive an insured patient's cost-share** to fill a plan.
- **Discount / dual-fee / inducement rules are state-specific** — flag them for counsel; don't improvise compliance.
