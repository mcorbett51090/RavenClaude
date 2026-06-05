---
scenario_id: 2026-06-05-maverick-spend-noncompliance
contributed_at: 2026-06-05
plugin: procurement-sourcing
product: spend-analytics
product_version: "n/a"
scope: likely-general
tags: [maverick-spend, compliance, tail-spend, contract-coverage, p2p]
confidence: medium
reviewed: false
---

## Problem

A function with strong negotiated contracts kept missing its savings target, and nobody could explain why — the rates were good on paper. The driver turned out to be **maverick spend**: a meaningful share of category spend was being bought off-contract, at non-contract prices, by requisitioners who bypassed the agreed supplier. The contracts existed; people just weren't using them, so the negotiated savings never reached the P&L.

## Context

- Segment: indirect (MRO + office + services), multi-business-unit, decentralized buying with weak P2P discipline — purchase requests routed around the catalog when the agreed supplier was "slower" or "harder."
- Constraint: spend visibility was poor — the spend cube wasn't classified well enough to see contract coverage by category, so off-contract buying was invisible until the savings miss forced the question (§3 #5: visibility before strategy).
- The team conflated "we have a contract" with "spend is on the contract." Contract *existence* is not contract *coverage* — the gap between the two is maverick spend.

## Attempts

- Tried: built/cleaned the spend cube enough to compute **contract-coverage rate** by category (share of addressable spend flowing through an agreed contract) and **maverick-spend rate** (off-contract share). Outcome: surfaced which categories leaked and by how much — moving from "we're missing target" to "category X is 40% off-contract."
- Tried: decomposed *why* requisitioners went off-contract — friction (slow PO, hard catalog), preference (a favored local supplier), and ignorance (didn't know a contract existed). Each cause has a different fix; treating all maverick spend as "non-compliance to punish" misdiagnoses it. Outcome: targeted the friction (catalog the contracted items, default the requisition to the agreed supplier) before reaching for policy enforcement.
- Tried: ran `scripts/sourcing_calc.py savings` with the on-contract-compliance fraction to quantify how much realized savings the maverick leak was costing, so the P2P-fix business case was sized in P&L terms, not abstract "compliance." Outcome: a funded clamp on the leak.

## Resolution

The savings miss was **maverick spend, not bad rates** — contracts existed but coverage was low. The fix was demand-and-compliance plumbing: classify spend to see coverage, catalog the contracted items, default requisitions to the agreed supplier, and address the *friction* that drove people off-contract before escalating to policy. Realized savings rose as coverage rose, with no re-negotiation.

**Action for the next consultant hitting this pattern:** when negotiated savings don't show up, **measure contract-coverage and maverick-spend rates before re-sourcing** (§3 #5). Contract existence ≠ coverage. Decompose *why* spend goes off-contract (friction / preference / ignorance) — fix the friction and the catalog first; enforcement is the last lever, not the first. Quantify the leak's P&L cost (on-contract-compliance fraction in the savings calc) so the P2P fix is funded, not just asserted.

**Sources (retrieved 2026-06-05):** maverick/off-contract spend as a leakage point + delayed-implementation / buyer-bypass leakage — https://www.traceconsultants.com.au/thinking/why-procurement-savings-leak-after-award ; identified-to-realized stage discipline + contract leakage — https://suplari.com/blog/realize-savings-in-procurement-how-to-prove-what-your-team-actually-delivered . Coverage/maverick percentages here are illustrative; treat any figure as `[ESTIMATE]` and compute from the client's classified spend (§3 #8).
