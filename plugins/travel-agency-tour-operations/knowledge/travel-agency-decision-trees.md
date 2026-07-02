# Travel Agency / Tour Operations — Decision Trees

> Reference decision trees for the `travel-agency-tour-operations` team. Agents **traverse the relevant tree top-to-bottom before deciding** (the proactive complement to the Capability Grounding Protocol). Each `## Decision Tree` section is a Mermaid graph plus the rule it encodes.
>
> **Advisory operations knowledge, not legal, tax, or financial advice.** Anything touching a supplier fare rule, commission rate, cancellation penalty, settlement mechanic, or seller-of-travel requirement is `[verify-at-use]` — confirm against the live supplier agreement, settlement statement, or jurisdiction before acting. No traveler PII.
>
> _Last reviewed: 2026-07-02 by `claude`. Principles are durable; dated norms and numbers live in [`travel-agency-reference-2026.md`](travel-agency-reference-2026.md)._

---

## Decision Tree: revenue model — commission, service fee, or markup?

```mermaid
flowchart TD
    A[New booking to price] --> B{Is the product<br/>commissionable?}
    B -- "yes (cruise, tour, hotel,<br/>package, insurance)" --> C{Does commission cover<br/>the planning effort?}
    C -- yes --> D[Commission-only<br/>book it, track the commission]
    C -- "no (complex FIT, heavy<br/>research, low-value trip)" --> E[Commission + service/planning fee<br/>price the labor]
    B -- "no / minimal (bare air<br/>via BSP/ARC)" --> F{Net rate available?}
    F -- yes --> G[Markup on net<br/>margin = your markup]
    F -- no --> H[Service/planning fee<br/>+ any ticketing fee — verify-at-use]
    D --> I[Disclose fees; confirm host<br/>split + seller-of-travel rules]
    E --> I
    G --> I
    H --> I
```

**Rule:** match the revenue model to the **work and the commissionability**. Commission subsidizes your time; when it won't cover the effort — or the product isn't commissionable — charge a **service fee** or price a **markup on net**. Disclose fees, honor the host split, and confirm seller-of-travel obligations. Rates and rules are `[verify-at-use]`.

---

## Decision Tree: structure this trip as group or FIT?

```mermaid
flowchart TD
    A[Multi-traveler request] --> B{Party size + shared<br/>inclusions?}
    B -- "small party, custom pacing,<br/>no shared block" --> C[FIT<br/>book each element individually]
    B -- "enough pax for a block<br/>+ shared components" --> D{Block economics worth<br/>the attrition risk?}
    D -- "yes (TC comps, group rate,<br/>shared events)" --> E[Group: contract the block FIRST<br/>deposit + cutoff + attrition]
    D -- "no (flexibility > leverage)" --> C
    E --> F{Can you fill the block<br/>before cutoff?}
    F -- unsure --> G[Smaller block or FIT<br/>to cap attrition exposure]
    F -- confident --> H[Hold the block;<br/>manage pickup to cutoff]
    C --> I[Each element carries its<br/>own penalty schedule — verify-at-use]
```

**Rule:** choose on **block economics vs flexibility**. A group is a contracted liability (deposit, cutoff, attrition) — build and hold the block **before** you sell against it; if you can't confidently fill it, cap exposure with a smaller block or FIT. Tour-conductor comps and group rates are `[verify-at-use]`.

---

## Decision Tree: travel disruption / service recovery

```mermaid
flowchart TD
    A[Disruption reported mid-trip] --> B{Traveler safe +<br/>immediate need met?}
    B -- no --> C[Rebook / re-accommodate NOW<br/>speed before fault]
    B -- yes --> D{Who owns the failure?}
    C --> D
    D -- "supplier (IROPS, overbook,<br/>default)" --> E[Escalate to supplier<br/>rebooking desk / remedy]
    D -- "covered peril" --> F[File travel-insurance /<br/>card-protection claim — verify-at-use]
    D -- "no one owes a remedy" --> G{Goodwill worth the<br/>retained relationship?}
    G -- yes --> H[Agency goodwill gesture<br/>frame margin with ops-lead]
    G -- no --> I[Explain honestly;<br/>offer options]
    E --> J[Document every change<br/>in the itinerary log]
    F --> J
    H --> J
    I --> J
```

**Rule:** **rebook first, litigate fault second.** Route the remedy to whoever owes it (supplier, insurer, card), decide goodwill deliberately when no one does, and **document every change**. A well-run recovery earns the repeat booking. Policy/supplier remedies are `[verify-at-use]`.

---

## Decision Tree: commission-recovery chase

```mermaid
flowchart TD
    A[Commission earned but not paid] --> B{On the ledger as<br/>booked-vs-paid?}
    B -- no --> C[Ledger it first<br/>you cannot chase what you don't track]
    B -- yes --> D{Statement received<br/>+ reconciled?}
    D -- "no statement" --> E[Request/await settlement<br/>per supplier cadence — verify-at-use]
    D -- "paid short or wrong" --> F[Open a commission claim<br/>with booking evidence]
    D -- "not paid, past due" --> G[Escalate per supplier<br/>agreement / consortia support]
    E --> H[Confirm collected;<br/>update the ledger]
    F --> H
    G --> H
    H --> I[Fix the PROCESS that let it<br/>slip, not just this one booking]
```

**Rule:** **booked is not paid.** Track every commission, reconcile against the statement, and chase shorts/non-payments with booking evidence on a cadence — then fix the process that let it slip. Settlement timing and supplier remedies are `[verify-at-use]`.

---

## See also

- [`travel-agency-reference-2026.md`](travel-agency-reference-2026.md) — dated norms + numbers (verify-at-use).
- Skills: [`../skills/itinerary-design-and-quoting/SKILL.md`](../skills/itinerary-design-and-quoting/SKILL.md), [`../skills/supplier-and-commission-management/SKILL.md`](../skills/supplier-and-commission-management/SKILL.md), [`../skills/group-vs-fit-trip-operations/SKILL.md`](../skills/group-vs-fit-trip-operations/SKILL.md), [`../skills/service-recovery-and-disruption/SKILL.md`](../skills/service-recovery-and-disruption/SKILL.md).
