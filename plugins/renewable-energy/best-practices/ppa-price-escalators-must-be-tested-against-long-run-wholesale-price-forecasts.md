# PPA Price Escalators Must Be Tested Against Long-Run Wholesale Price Forecasts

**Status:** Pattern
**Domain:** Project finance / offtake economics
**Applies to:** `renewable-energy`

---

## Why this exists

Power Purchase Agreements with annual price escalators (1–2% per year is common) protect the project against inflation but create a counterparty risk for the buyer: if wholesale power prices stay flat or decline as more renewables enter the market, the PPA price escalates above the buyer's alternative supply cost, incentivizing them to renegotiate or exit the contract. A developer who models only the revenue side (escalating PPA prices) without testing the buyer's willingness to remain in the contract — by comparing PPA prices in the out-years to long-run wholesale price forecasts — is building an IRR on a counterparty risk the model ignores.

## How to apply

Build the PPA buyer economics test alongside the project IRR:

```
PPA price sustainability test:
  PPA price year 1:               $______/MWh
  Annual escalator:               ______%
  PPA price year 10:              PPA yr1 × (1 + escalator)^10 = $______/MWh
  PPA price year 20:              $______/MWh

  Long-run wholesale price forecast (use publicly available):
    Source and date:              ______
    Forecast wholesale price year 10: $______/MWh [unverified — forecast]
    Forecast wholesale price year 20: $______/MWh [unverified — forecast]

  PPA premium vs. market (year 10): PPA price yr10 − forecast yr10 = $______/MWh
  PPA premium vs. market (year 20): $______/MWh

  Risk flag: if PPA price exceeds forecast wholesale price by > 30% in year 10–15:
    → High counterparty exit or renegotiation risk in the mid-contract years.
    → Structure a review clause, a collar, or a shorter initial term with renewal option.

  IRR sensitivity:
    If buyer exits at year 12 and project goes merchant for remaining term:
    IRR under merchant scenario: ______% (vs. base case: ______%)
```

**Do:**
- Present the buyer economics test alongside the project IRR in any offtake discussion — buyers who model this on their own will ask about it.
- Use third-party long-run wholesale price forecasts from credible sources (Wood Mackenzie, Enverus, EIA) and cite them with date.
- For fixed-price (non-escalating) PPAs in a potentially deflationary wholesale market, run the test in reverse — a fixed price may become increasingly favorable to the buyer, reducing renegotiation risk.

**Don't:**
- Present only the project IRR to buyers or investors without the counterparty-sustainability test — sophisticated buyers will run it independently and flag the risk.
- Use a static wholesale price assumption in the test; the long-run forecast must include the expected effect of growing renewable capacity on wholesale price suppression.

## Edge cases / when the rule does NOT apply

Community solar subscription PPAs in states with fixed retail rate credits may be insulated from wholesale price dynamics if the credit is set by regulation; the test applies at the retail tariff level instead. Behind-the-meter C&I PPAs compared against the host's retail rate are governed by retail rate escalation, not wholesale — the same test structure applies but with retail price forecasts.

## See also

- [`../agents/energy-finance-analyst.md`](../agents/energy-finance-analyst.md) — owns the PPA price model and the counterparty sustainability test.
- [`../agents/renewables-engagement-lead.md`](../agents/renewables-engagement-lead.md) — frames the offtake risk during the initial engagement.
- [`./offtake-structure-determines-financing-eligibility-before-the-pro-forma.md`](./offtake-structure-determines-financing-eligibility-before-the-pro-forma.md) — the PPA structure must be established before this test can be run.

## Provenance

PPA price sustainability and counterparty exit risk analysis is standard in utility-scale solar project finance; the comparison to long-run wholesale forecasts is a common lender due-diligence requirement. Long-run price forecasts should be sourced from cited, dated third-party providers.

---

_Last reviewed: 2026-06-05 by `claude`_
