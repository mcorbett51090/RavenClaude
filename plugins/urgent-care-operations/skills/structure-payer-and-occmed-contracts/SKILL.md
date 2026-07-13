---
name: structure-payer-and-occmed-contracts
description: Turn an urgent-care center's payer and revenue picture into a contract-and-economics plan by reading the payer mix against the local market, prioritizing in-network contracting (which payers to join, renegotiate, or stay out of by revenue-per-visit impact), designing occupational-medicine employer contracts as a distinct high-margin line (sales motion, service menu, pricing, scheduling, capacity), diagnosing revenue per visit across its three drivers (E/M level distribution, ancillary capture, contracted rate), and setting transparent self-pay/price-transparency pricing — returning the recommended moves with projected lift and the coding/billing determinations handed off to medical-revenue-cycle. Reach for this when the user asks "what should my payer mix be?", "how do I win occ-med employer contracts?", "why is revenue per visit flat?", or "how do I set self-pay pricing?". Used by `urgent-care-revenue-and-payer-specialist` (primary).
---

# Skill: structure-payer-and-occmed-contracts

> **Invoked by:** `urgent-care-revenue-and-payer-specialist` (primary). Also consulted by `urgent-care-operations-lead` to understand the payer/occ-med capacity implications before routing the revenue call.
>
> **When to invoke:** "What should my payer mix be / which contracts do I renegotiate?"; "how do I win and price occ-med employer contracts?"; "why is my revenue per visit flat?"; "how do I set self-pay/price-transparency pricing?"; any move from a payer/revenue picture to a contract-and-economics plan.
>
> **Output:** the payer-mix read + in-network contracting priorities + the occ-med line plan + the visit-economics diagnosis (which of the three drivers is the constraint) + the self-pay schedule + projected lift + the coding/billing hand-off + the 1-2 flip conditions. Capture it in [`../../templates/payer-and-occmed-contract-plan.md`](../../templates/payer-and-occmed-contract-plan.md).

> ⚠️ **This is operational and economic guidance — NOT a coding, billing, or legal determination.** The **CPT/E/M code on any claim, claim scrubbing, and denial appeals are `medical-revenue-cycle`'s** call; **contract law and corporate-practice-of-medicine questions are counsel's**. This skill decides economics and level *distribution*, flags the code and the law, and attaches a retrieval date to every volatile contract/pricing claim.

## Procedure

1. **Read the payer mix against the local market first.** Lay out visit share and contracted rate by payer (commercial, Medicare, Medicaid, workers'-comp/occ-med, self-pay). Revenue per visit follows the mix and the contracted rates more than raw volume — a low-reimbursing-payer-heavy center can out-volume and under-earn. See [`../../knowledge/urgent-care-patterns-2026.md`](../../knowledge/urgent-care-patterns-2026.md).
2. **Prioritize in-network contracting as a portfolio decision.** Which payers to **join**, **renegotiate**, or **stay out of** is a rate-vs-volume trade — prioritize by revenue-per-visit impact and the local patient base. Re-verify contract norms with a retrieval date; the contract *law* routes to counsel.
3. **Design the occ-med line as its own high-margin business.** Occupational medicine — pre-employment physicals, drug/alcohol screens, injury care, workers'-comp, DOT physicals, employer wellness — is employer-paid, contracted, and insulated from payer-mix erosion. Plan the **employer sales motion** (HR/safety-manager relationships), the **service menu + pricing**, the **scheduling**, and the **capacity** it demands (route the capacity/throughput design to the operations lead — occ-med can absorb the morning trough of the acute curve).
4. **Diagnose revenue per visit across its three drivers.** Revenue per visit = **E/M level distribution × ancillary capture × contracted rate**. Name which is the constraint: an under-leveled **distribution**, **ancillary capture** leakage (an x-ray/POCT delivered but not recorded), or a stale **contracted rate**. **The code on the claim is `medical-revenue-cycle`'s determination — diagnose the distribution and the capture, don't assign the code.**
5. **Set self-pay pricing transparently and defensibly.** Build a posted self-pay / price-transparency schedule against the local market and the acute + ancillary menu — a regulatory expectation and a demand lever for the uninsured segment. The price-transparency legal-compliance question routes to counsel.
6. **Project the lift and state the flip conditions.** Estimate the revenue lift from the mix/contract/occ-med/economics moves, and name the 1-2 facts that would change the plan (e.g. "if a dominant local employer signs, the occ-med line reshapes the capacity plan and the intraday staffing").

## Worked example

> User: "Volume is up 15% but revenue is flat. What's wrong?"

- **Payer-mix read:** the growth came almost entirely from a **low-reimbursing Medicaid** share while commercial share fell — volume up, revenue-per-visit down. Mix, not volume, is the story.
- **Contracting priority:** two commercial contracts are ~3 years stale and below market — **renegotiate** those first (highest revenue-per-visit impact); evaluate joining one payer the local base uses that the center is out-of-network with.
- **Revenue-per-visit diagnosis:** of the three drivers, the constraint is **contracted rate** (stale contracts) plus some **ancillary capture** leakage (x-rays read but not consistently recorded). The **level distribution** looks reasonable — but whether any visit is correctly coded is a **`medical-revenue-cycle`** question, flagged, not answered here.
- **Occ-med:** no occ-med line exists; standing one up (physicals/drug-screens for 2-3 local employers) would add a **contracted, higher-margin** stream insulated from the Medicaid drift — routed to the operations lead for morning-trough capacity.
- **Flip condition:** if a commercial payer exits the local market, the mix and the renegotiation priority change.

## Guardrails

- Never make a revenue-per-visit call before reading the payer mix and the contracted rates — mix is destiny for the acute line.
- Occ-med is a **distinct high-margin line** — plan its sales motion, pricing, scheduling, and capacity separately; never bury it in "acute visits."
- Revenue per visit is **three drivers** — name the constraint (level distribution / ancillary capture / contracted rate) before prescribing.
- **The CPT/E/M code, claim scrubbing, and denial appeals are `medical-revenue-cycle`'s — flag, don't freelance a code.** This skill diagnoses the distribution and the capture only.
- Self-pay pricing must be transparent and defensible against the local market; the price-transparency *legal* question routes to counsel — not legal advice.
- Volatile claims (payer contract norms, occ-med pricing, UCA benchmarks, price-transparency rules, EMR/PM features) carry a **retrieval date** — re-verify before a client commitment.
