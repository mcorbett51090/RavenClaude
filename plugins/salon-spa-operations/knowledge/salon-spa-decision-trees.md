# Salon / Spa / Barbershop — Decision Trees

> Reference decision trees for the `salon-spa-operations` team. Agents **traverse the relevant tree top-to-bottom before deciding** (the proactive complement to the Capability Grounding Protocol). Each `## Decision Tree` section is a Mermaid graph plus the rule it encodes.
>
> **Operations and financial decision-support, not legal, tax, or employment-classification advice.** Anything touching worker classification, a deposit/consumer-protection rule, or a lease term is `[verify-at-use]` and routes to a licensed professional. Benchmarks (utilization, retail-attach, no-show norms) are volatile — confirm before quoting. No client PII.
>
> _Last reviewed: 2026-07-02 by `claude`. Principles are durable; dated benchmarks live in [`salon-spa-reference-2026.md`](salon-spa-reference-2026.md)._

---

## Decision Tree: choose the compensation model (commission vs booth-rent vs hourly)

```mermaid
flowchart TD
    A[Setting or changing provider pay] --> B{Who controls the chair:<br/>schedule, product, pricing?}
    B -- "shop controls it" --> C{Provider's book<br/>full and high-priced?}
    C -- "yes, strong book" --> D[Tiered commission<br/>shop shares the upside it helped build]
    C -- "building / variable" --> E[Hourly + commission<br/>wage floor protects the slow week]
    B -- "provider controls it<br/>own hours, product, pricing" --> F{Provider wants full<br/>upside + own risk?}
    F -- "yes, established clientele" --> G[Booth / chair rent<br/>fixed rent, provider keeps service revenue]
    F -- "not yet" --> E
    D --> H[Flag classification:<br/>employee vs 1099 -> professional, verify-at-use]
    E --> H
    G --> H
```

**Rule:** the comp model follows **who actually controls the chair** and how strong the book is — model it on the provider's real revenue and cost, never a rule of thumb. Employee vs booth-renter/1099 is a legal determination: model the economics, `[verify-at-use]`, and route the classification call to a licensed professional.

---

## Decision Tree: set the no-show / late-cancel policy & deposit

```mermaid
flowchart TD
    A[No-shows / late cancels hurting the book] --> B{Current no-show rate?<br/>verify-at-use on norms}
    B -- "low / occasional" --> C[Light policy:<br/>reminder cadence + clear notice window]
    B -- "chronic / high-value slots" --> D{Payment on file<br/>at booking possible?}
    D -- "yes" --> E[Card-on-file or deposit<br/>+ notice window + fair fee]
    D -- "no" --> F[Deposit for new clients<br/>and long/high-value services]
    C --> G{Easy one-tap<br/>reschedule in reminders?}
    E --> G
    F --> G
    G -- no --> H[Fix reminders FIRST<br/>prevention beats the fee]
    G -- yes --> I[Enforce consistently<br/>with a fair exception path]
```

**Rule:** the policy exists to **change behavior, not collect fees** — prevent the no-show with a confirming reminder cadence first, then enforce a deposit/card-on-file sized to the actual no-show rate, consistently and with a fair exception path. A no-show is inventory you can't resell. Norms are `[verify-at-use]`.

---

## Decision Tree: rebook at checkout

```mermaid
flowchart TD
    A[Client finishing their service] --> B{Did the provider recommend<br/>a next-visit interval?}
    B -- no --> C[Provider sets the interval<br/>at the chair — part of the service]
    B -- yes --> D{Front desk offers the<br/>specific next appointment?}
    C --> D
    D -- "'call us to book'" --> E[Weak: retention leaks<br/>reframe to book-it-now]
    D -- "offers a real slot" --> F{Client hesitant<br/>to commit a date?}
    F -- yes --> G[Deposit-to-hold or<br/>tentative + reminder]
    F -- no --> H[Book it -> client is retained<br/>track rebook rate per provider]
    G --> H
```

**Rule:** the highest-yield front-desk act is booking the **next** appointment before the client leaves the chair, at the provider's recommended interval. "Call us to book" is a hope; a booked slot is retention. Track rebooking rate per provider as the leading indicator of a full future calendar.

---

## Decision Tree: price the service menu (time and demand)

```mermaid
flowchart TD
    A[Pricing or repricing a service] --> B{Contribution per chair-hour<br/>after product + time cost?}
    B -- "low vs the menu" --> C{Is the service a<br/>loss-leader / traffic driver?}
    C -- "no" --> D[Reprice up or add<br/>a margin add-on]
    C -- "yes, feeds retail/rebook" --> E[Keep, but measure the<br/>downstream attach it drives]
    B -- "healthy contribution" --> F{Demand even across<br/>the week?}
    F -- "peaks Saturday, empty Tuesday" --> G[Demand-based pricing:<br/>fill off-peak, protect peak]
    F -- "even" --> H[Hold; revisit on cost change]
```

**Rule:** price on **contribution per chair-hour and on demand**, not on what the shop down the street charges. Reprice the low-contribution service (or attach margin to it), and use demand-based pricing to fill the empty daypart and protect the peak. Chair-hours are perishable — an empty Tuesday is spoiled inventory. Local price data is `[verify-at-use]`.

---

## See also

- [`salon-spa-reference-2026.md`](salon-spa-reference-2026.md) — dated benchmarks + concepts (verify-at-use).
- Skills: [`../skills/compensation-models-commission-vs-booth-rent/SKILL.md`](../skills/compensation-models-commission-vs-booth-rent/SKILL.md), [`../skills/booking-and-no-show-control/SKILL.md`](../skills/booking-and-no-show-control/SKILL.md), [`../skills/chair-and-room-utilization/SKILL.md`](../skills/chair-and-room-utilization/SKILL.md), [`../skills/retail-attach-and-service-mix/SKILL.md`](../skills/retail-attach-and-service-mix/SKILL.md).
