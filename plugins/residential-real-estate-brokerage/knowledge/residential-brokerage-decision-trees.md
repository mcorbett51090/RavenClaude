# Residential Real-Estate Brokerage — Decision Trees

> Reference decision trees for the `residential-real-estate-brokerage` team. Agents **traverse the relevant tree top-to-bottom before deciding** (the proactive complement to the Capability Grounding Protocol). Each `## Decision Tree` section is a Mermaid graph plus the rule it encodes.
>
> **Advisory operations knowledge, not legal, financial, or real-estate-license advice.** This domain is **fair-housing sensitive**: anything touching protected classes, agency disclosure, commission rates, or contingency periods is `[verify-at-use]` — confirm against current law, the contract, and the brokerage's own agreements before acting. No client PII.
>
> _Last reviewed: 2026-07-02 by `claude`. Principles are durable; dated benchmarks and norms live in [`residential-brokerage-reference-2026.md`](residential-brokerage-reference-2026.md)._

---

## Decision Tree: price this listing (CMA)

```mermaid
flowchart TD
    A[Seller wants a list price] --> B{Are there 3-6 truly<br/>comparable closed sales?}
    B -- no --> C[Widen carefully: adjust for<br/>distance/recency; note lower confidence]
    B -- yes --> D[Adjust each comp toward<br/>the subject explicitly]
    D --> E{Seller target inside the<br/>supported comp range?}
    E -- yes --> F[List within range;<br/>position on timeline + market direction]
    E -- "no, target is higher" --> G[Show the comps; script the<br/>overpricing cost — stale DOM, later cut]
    G --> H{Seller insists above range?}
    H -- yes --> I[Document the CMA; decide whether<br/>to take the listing at that price]
    H -- no --> F
```

**Rule:** the price is a **supported range from adjusted comparables**, positioned by the seller's timeline and market direction — never set to the seller's target to win the appointment. Overpricing costs a stale listing and a later drop below a right first price. Local figures are `[verify-at-use]`.

---

## Decision Tree: represent buyer vs seller / dual-agency conflict

```mermaid
flowchart TD
    A[New representation opportunity] --> B{Whom does the brokerage<br/>already represent in this deal?}
    B -- "no one yet" --> C[Disclose agency options;<br/>establish the relationship in writing FIRST]
    B -- "the seller (listing)" --> D{Buyer wants us too?}
    B -- "the buyer" --> E{Seller is our listing?}
    D -- yes --> F{Dual/designated agency<br/>allowed here? — verify-at-use}
    E -- yes --> F
    F -- "yes, with informed written consent" --> G[Get informed written consent<br/>from BOTH before proceeding]
    F -- "no / not this way" --> H[Refer out or use separate<br/>designated agents per policy]
    G --> I[Maintain strict confidentiality<br/>of each side's position]
```

**Rule:** the agency relationship is **disclosed and established in writing before you represent**. A dual/designated-agency situation proceeds only where allowed and only with informed written consent from both sides — otherwise refer out. Never let a commission drive an undisclosed conflict. Agency rules are `[verify-at-use]` by jurisdiction and brokerage policy.

---

## Decision Tree: offer & counter strategy

```mermaid
flowchart TD
    A[Buyer wants to make an offer] --> B{Competitive situation?}
    B -- "single offer, soft market" --> C[Lead with price/terms room;<br/>keep standard contingencies]
    B -- "multiple offers" --> D[Compete on structure + certainty,<br/>not price alone]
    D --> E{Buyer's real risk tolerance<br/>on contingencies?}
    E -- low --> F[Strengthen price/earnest/close date;<br/>KEEP inspection + financing protection]
    E -- high, informed --> G{Waive/shorten a contingency?}
    G -- "appraisal gap" --> H[Only with lender-confirmed<br/>cash-to-cover — verify-at-use]
    G -- "inspection" --> I[Document informed risk;<br/>consider info-only inspection]
    F --> J[Never compete on a lever<br/>touching a protected class]
    H --> J
    I --> J
    C --> J
```

**Rule:** win on **structure, financing strength, and certainty** matched to the buyer's informed risk tolerance — not on price alone, and never on any lever touching a protected class. A contingency waiver is advised only when the buyer understands and can absorb the risk (appraisal gaps need lender-confirmed funds). Terms are `[verify-at-use]`.

---

## Decision Tree: commission split-vs-cap model

```mermaid
flowchart TD
    A[Choosing/changing a comp model] --> B[Estimate the agent's<br/>expected annual GCI]
    B --> C{Where is the agent's GCI vs<br/>the cap crossover point?}
    C -- "below crossover" --> D[Split earns the house more;<br/>cap over-rewards a low producer]
    C -- "above crossover" --> E[Cap earns the agent more;<br/>high producers will demand it]
    D --> F{Is the agent a producer<br/>worth retaining?}
    E --> F
    F -- yes --> G[Offer cap/tier + the support stack;<br/>sell take-home + value, not split alone]
    F -- "no / new, unproven" --> H[Split or fee model;<br/>revisit as production grows]
    G --> I[Confirm company dollar per agent<br/>keeps the P&L whole — verify-at-use]
    H --> I
```

**Rule:** model on **company dollar per agent at expected GCI** and the **cap crossover**, then choose by production tier and retention value — recruit and retain on the whole value stack, not the headline split. Rates, caps, and fees are `[verify-at-use]` against the brokerage's agreements.

---

## See also

- [`residential-brokerage-reference-2026.md`](residential-brokerage-reference-2026.md) — dated norms + benchmarks (verify-at-use).
- Skills: [`../skills/cma-and-pricing-strategy/SKILL.md`](../skills/cma-and-pricing-strategy/SKILL.md), [`../skills/transaction-timeline-management/SKILL.md`](../skills/transaction-timeline-management/SKILL.md), [`../skills/commission-split-and-cap-economics/SKILL.md`](../skills/commission-split-and-cap-economics/SKILL.md), [`../skills/listing-launch-and-marketing/SKILL.md`](../skills/listing-launch-and-marketing/SKILL.md).
