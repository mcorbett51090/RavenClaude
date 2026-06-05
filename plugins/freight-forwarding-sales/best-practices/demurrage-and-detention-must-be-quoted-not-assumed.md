# Quote free-time and demurrage/detention terms explicitly — never let them be a surprise

**Status:** Absolute rule
**Domain:** Ocean freight quoting / commercial terms
**Applies to:** `freight-forwarding-sales`

---

## Why this exists

Demurrage and detention are the most common source of unexpected charges in ocean FCL freight. Demurrage is the cost of keeping a container at the terminal beyond the free days allowed. Detention is the cost of retaining the container (empty or laden) beyond the free days allowed at the customer's premises. These are carrier-controlled charges and they escalate daily — a single FCL can generate USD 500–3,000+ per day in demurrage on a busy port after free time expires. A customer who was not told their free time is "5 days" on a port that regularly holds containers for 8 days on customs inspection will be blindsided by an invoice they did not budget for. The seller who warned them is the seller they trust; the seller who didn't is the seller they blame.

## How to apply

Every ocean FCL quote includes explicit free time for demurrage and detention, either as a stated number or as a named reference to the carrier's terms.

**Minimum disclosure in a quote:**

```
Free time:
  - Origin detention (container at your facility pre-load): [X days] — as per [CARRIER] tariff / [contract terms]
  - Destination demurrage (container at terminal post-arrival): [X days] — as per [CARRIER] tariff / [contract terms]
  - Destination detention (container at your facility post-pickup): [X days] — as per [CARRIER] tariff / [contract terms]

Beyond free time:
  - Demurrage rate: [USD X/day for days 1–Y, USD Z/day thereafter — or refer to carrier tariff]
  - Detention rate: [USD X/day — or refer to carrier tariff]
  - Important: free time and demurrage/detention rates are carrier-controlled and may change; confirm against the current carrier D&D tariff before loading.
```

**Free time norms (indicative — confirm from the carrier tariff):**

| Port / region | Typical destination demurrage free time | Note |
|---|---|---|
| North Europe main ports | 5–7 days | Can be extended by contract on high-volume lanes |
| US East/West Coast | 4–5 days | Port congestion can eliminate effective free time quickly |
| Southeast Asia | 3–5 days | Varies significantly by carrier and terminal |
| Middle East / Gulf | 3–5 days | Carriers often have short free time + escalating rates |

These are market norms only — always confirm the specific carrier tariff.

**Proactive risk advisory (for destinations with known congestion):**

When quoting to a port with known congestion risk (e.g., US gateway during peak season, any port under labour action), add a one-line advisory:

```
Congestion advisory: [PORT] has experienced extended container dwell times in recent months. 
We recommend planning for [X days] beyond standard free time. 
We can monitor arrival + terminal entry and alert you before free time expires.
```

**Do:**
- State free time in every FCL quote, not just contract rates.
- Alert the customer operationally when their free time is within 48 hours of expiry — proactive notification is a retention behaviour.
- Include D&D terms in the RFQ response pack when the customer is running a formal tender — many procurement teams now score forwarders on free time offered.

**Don't:**
- Write "D&D as per carrier tariff" without also stating the number of free days — "per tariff" is not a budget figure.
- Assume the customer knows the free time on their current lane; they often do not until they receive the invoice.
- Quote a custom extended free time that you cannot actually deliver from the carrier; confirm the free time with your carrier before quoting it to the customer.

## Edge cases / when the rule does NOT apply

For LCL shipments, demurrage and detention in the same form do not apply (there is no dedicated container). CFS charges and re-delivery fees apply instead and should be named. For air freight, storage charges at the airport are the equivalent; quote the free storage period and the daily storage rate on consignments that may not clear customs immediately.

## See also
- [`../agents/freight-rate-quoter.md`](../agents/freight-rate-quoter.md) — all-in quote construction
- [`../skills/freight-pricing-mechanics/SKILL.md`](../skills/freight-pricing-mechanics/SKILL.md) — surcharge and charge-basis glossary (demurrage vs detention definitions)

## Provenance

Codifies `freight-rate-quoter`'s anti-pattern discipline (§4 in CLAUDE.md) and house opinion §6 ("Name the charge correctly"). Demurrage/detention surprise invoices are among the most cited complaints in shipper satisfaction surveys across the freight industry.

---

_Last reviewed: 2026-06-05 by `claude`_
