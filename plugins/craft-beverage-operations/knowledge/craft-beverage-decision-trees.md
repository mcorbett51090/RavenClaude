# Craft Beverage (Winery / Brewery / Distillery) — Decision Trees

> Reference decision trees for the `craft-beverage-operations` team. Agents **traverse the relevant tree top-to-bottom before deciding** (the proactive complement to the Capability Grounding Protocol). Each `## Decision Tree` section is a Mermaid graph plus the rule it encodes.
>
> **Operations and financial decision-support, not legal, tax, or regulatory advice.** Anything touching the three-tier system, franchise/distribution law, TTB or state licensing, direct-ship permits, or excise tax is jurisdiction-specific, `[verify-at-use]`, and routes to a licensed professional. Benchmarks (yields, COGS ranges, channel margins, club norms) are volatile — confirm before quoting. No PII.
>
> _Last reviewed: 2026-07-04 by `claude`. Principles are durable; dated benchmarks live in [`craft-beverage-reference-2026.md`](craft-beverage-reference-2026.md)._

---

## Decision Tree: channel mix (DTC vs wholesale)

```mermaid
flowchart TD
    A[Setting the DTC vs wholesale mix] --> B{Is COGS per unit known<br/>and defensible?}
    B -- no --> C[Nail COGS first<br/>channel margin is meaningless without it]
    B -- yes --> D{DTC demand<br/>can absorb more volume?}
    D -- "yes, room in club/tasting/e-comm" --> E[Tilt to DTC<br/>full retail margin kept]
    D -- "no, DTC demand tapped" --> F{Need volume/reach<br/>beyond DTC?}
    F -- "yes" --> G[Wholesale for scale<br/>net margin after distributor + retailer take]
    F -- "no" --> H[Hold; grow DTC demand first]
    E --> I[Allocate production to channels<br/>on net margin x absorbable demand]
    G --> I
```

**Rule:** channel mix is the margin decision, and it starts from a known COGS per unit. DTC keeps the full retail margin but is demand-limited; wholesale adds reach and volume but gives margin to the distributor and retailer. Allocate production on net margin per channel against the demand each can absorb. Margins are `[verify-at-use]`.

---

## Decision Tree: add production capacity

```mermaid
flowchart TD
    A[Considering more tanks/barrels/equipment] --> B{Is current capacity<br/>the binding constraint?}
    B -- "no, vessels not fully turned" --> C[Improve turns/scheduling first<br/>capacity isn't the problem]
    B -- "yes, fully turned at demand" --> D{Constraint is<br/>space or time?}
    D -- "time: aging/fermentation" --> E[Adding vessels locks more<br/>working capital in aging stock]
    D -- "space: throughput" --> F[Add vessels/equipment<br/>model payback on absorbable demand]
    E --> G{Demand plan supports<br/>the working-capital tie-up?}
    G -- yes --> F
    G -- no --> C
```

**Rule:** capacity is tanks, barrels, **and time**. Confirm current vessels are fully turned against the demand plan before adding, and recognize that in aging products the constraint is time — adding vessels locks more working capital in stock that won't sell for months or years. Model the payback on absorbable demand. `[verify-at-use]` on yields/turns.

---

## Decision Tree: design the club

```mermaid
flowchart TD
    A[Designing / fixing a club] --> B{Tiers priced on<br/>member LTV or one shipment?}
    B -- "one shipment" --> C[Reprice on LTV<br/>shipment value x frequency x tenure]
    B -- "LTV" --> D{Churn read<br/>by cohort?}
    D -- "no" --> E[Instrument churn cohorts<br/>find the drop point]
    D -- "yes" --> F{Churn driver:<br/>value/frequency fit or price?}
    F -- "value/frequency" --> G[Fix curation, frequency,<br/>flexibility skip/swap]
    F -- "price" --> H[Adjust tier value<br/>not just discount]
    G --> I[Coordinate allocation<br/>with production -> ops lead]
    H --> I
    C --> I
```

**Rule:** the club is the recurring-revenue engine — design tiers on member lifetime value, manage churn by cohort (the driver is usually value/frequency fit, not price), treat each shipment as a retention moment, and coordinate club allocation with production. Norms are `[verify-at-use]`.

---

## Decision Tree: self-distribute vs distributor

```mermaid
flowchart TD
    A[Going to market wholesale] --> B{Self-distribution<br/>legally available here?}
    B -- "jurisdiction-specific — FLAG + route" --> C[Confirm eligibility<br/>with a professional]
    B --> D{Volume/reach need<br/>beyond self-distribution capacity?}
    D -- "no, local + limited" --> E[Self-distribute:<br/>keep margin, bear sales/logistics cost]
    D -- "yes, need reach + depletion" --> F{Understand the<br/>franchise-law lock-in?}
    F -- "no" --> G[STOP: read franchise law<br/>you may not be able to leave — route]
    F -- "yes" --> H[Distributor: reach + depletion<br/>for margin given away]
    E --> I[Model net margin per channel]
    H --> I
    C --> I
```

**Rule:** model the economics (self-distribution keeps margin but costs effort and has eligibility limits; a distributor buys reach and depletion for margin and franchise-law lock-in), but **every** eligibility, licensing, franchise-law, and excise specific is jurisdiction-specific — flag it `[verify-at-use]` and route the determination to a licensed professional. Flag, never decide.

---

## See also

- [`craft-beverage-reference-2026.md`](craft-beverage-reference-2026.md) — dated benchmarks + concepts (verify-at-use).
- Skills: [`../skills/production-planning-and-cogs/SKILL.md`](../skills/production-planning-and-cogs/SKILL.md), [`../skills/tasting-room-throughput-and-conversion/SKILL.md`](../skills/tasting-room-throughput-and-conversion/SKILL.md), [`../skills/club-membership-and-dtc-revenue/SKILL.md`](../skills/club-membership-and-dtc-revenue/SKILL.md), [`../skills/three-tier-and-self-distribution-economics/SKILL.md`](../skills/three-tier-and-self-distribution-economics/SKILL.md).
