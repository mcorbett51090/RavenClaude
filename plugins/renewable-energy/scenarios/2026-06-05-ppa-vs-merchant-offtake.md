---
scenario_id: 2026-06-05-ppa-vs-merchant-offtake
contributed_at: 2026-06-05
plugin: renewable-energy
product: offtake
product_version: "n/a"
scope: likely-general
tags: [ppa, merchant, offtake, financing, basis-risk]
confidence: medium
reviewed: false
---

## Problem

A developer with a project in a high-price ISO zone was tempted to go **merchant** (sell into the wholesale spot market) to capture the upside, instead of signing a fixed-price **PPA**. The lender, however, would only size debt against contracted revenue. The risk: choosing the offtake structure on headline price alone, without checking that the structure is **financeable** and that the merchant upside survives basis risk and a long-run wholesale price forecast (CLAUDE.md §3 — offtake structure determines financing eligibility *before* the pro-forma).

## Context

- Segment: utility-scale solar in a zone where recent solar PPA prints ran in the ~$60s/MWh range nationally [verify-at-use], with wide regional spread (low-priced ERCOT vs. higher PJM/CAISO).
- Constraint: a **merchant** project carries price + basis risk and typically supports **less leverage** (lenders haircut uncontracted revenue heavily); a **PPA** lowers the cost of capital by making revenue bankable but caps the upside and locks an escalator that must be tested against a long-run wholesale forecast.
- The developer was comparing a merchant *P50 revenue* against a PPA *contract price* — an apples-to-oranges comparison that ignored the discount-rate and leverage difference the two structures command.

## Attempts

- Tried: re-framed the comparison on a **risk-adjusted, after-financing** basis — PPA revenue at the lender's debt sizing and lower cost of capital, vs. merchant revenue at a higher equity discount rate and thinner leverage. Outcome: the merchant "upside" shrank materially once the higher cost of capital and lower debt were applied.
- Tried: tested the **PPA escalator against a long-run wholesale price forecast** (does the escalator out-run or under-run the forward curve?) and stress-tested basis (nodal-vs-hub) risk on the merchant case. Outcome: the merchant case was viable only under an optimistic price forecast it couldn't underwrite to.
- Tried: evaluated **hybrid / partial-contracting** (a PPA on a base layer plus a merchant tail on the balance, or a shorter PPA term with a merchant tail after) to keep some upside while preserving financeability. Outcome: the hybrid was the structure the lender would actually fund.

## Resolution

The project signed a **PPA on the financed base with a merchant tail** rather than going fully merchant, because the offtake structure has to clear the *financing* gate before the pro-forma matters, and the merchant upside didn't survive a long-run forecast plus basis risk. The output was a dated offtake recommendation with the financeability constraint stated first and the upside quantified at the correct (higher) merchant discount rate.

**Action for the next consultant hitting this pattern:** **check financeability before headline price — the offtake structure sets the cost of capital and the leverage, which usually swamp the price delta.** Compare structures risk-adjusted and after-financing, not contract-price-vs-P50. Test the PPA escalator against a long-run wholesale forecast and the merchant case against basis risk; reach for a hybrid/partial-contract when the lender won't fund full merchant — see [`../knowledge/renewables-ppa-vs-merchant-decision-tree.md`](../knowledge/renewables-ppa-vs-merchant-decision-tree.md). The economics lane is owned by [`energy-finance-analyst`](../agents/energy-finance-analyst.md).

**Sources (retrieved 2026-06-05):**
- LevelTen Energy — *North America PPA Price Index* (solar PPA price level + regional spread, ~$61.67/MWh Q4 2025): https://www.leveltenenergy.com/ppa
- pv-tech — *North American solar PPA prices climb to US$61.67/MWh* (2025): https://www.pv-tech.org/north-american-solar-ppa-prices-climb-us61-67-mwh-european-prices-continue-fall/

PPA price levels, regional basis, and merchant spreads are zone- and quarter-specific and moved up ~9% YoY through 2025 — treat every figure as `[verify-at-use]` against the project's actual ISO zone and a current index (§3 #8).
