# Salon & Spa Operations — Decision Trees

> Reference decision trees for the `salon-spa-operations` team. Agents **traverse the relevant tree top-to-bottom before choosing** (the proactive complement to the Capability Grounding Protocol). Each `## Decision Tree` section is a Mermaid graph plus the rule it encodes.
>
> _Last reviewed: 2026-06-25 by `claude`. Principles are durable; specific benchmark numbers live (dated) in [`salon-spa-operations-reference-2026.md`](salon-spa-operations-reference-2026.md). Worker-classification and tax outcomes are jurisdiction-dependent — these trees frame the operational trade only; the legal verdict escalates to `people-operations-hr` / `accounting-bookkeeping`._

---

## Decision Tree: commission vs booth/chair rental vs hybrid?

```mermaid
graph TD
    A[Choosing a compensation model] --> B{What do you most need to control?}
    B -- "brand, schedule, pricing, client book" --> C{Can you carry payroll + employer obligations?}
    C -- yes --> D[Commission / salary+commission<br/>employee: you control, you carry the cost]
    C -- "not yet" --> E{Would a hybrid bridge it?}
    B -- "low overhead, predictable income" --> F{Stylists have their own book + clients?}
    F -- yes --> G[Booth / chair rental<br/>independent: fixed rent, you give up control]
    F -- no --> E
    E -- yes --> H[Hybrid<br/>rental+service-fee, commission+product-charge, or suites]
    E -- no --> D
    D --> I[Flag the worker-classification test<br/>-> people-operations-hr]
    G --> I
    H --> I
```

**Rule:** the model is a control/risk trade, not just a split. Commission = control + employer cost; rental = low overhead + lost control; hybrid splits it. **Every branch ends at the classification flag** — employee-vs-contractor is a legal test (control, tools, schedule), jurisdiction-dependent, and never a label of convenience. Frame the operational trade here; escalate the verdict to `people-operations-hr` and the tax mechanics to `accounting-bookkeeping`.

---

## Decision Tree: is the chair empty because of demand or scheduling?

```mermaid
graph TD
    A[Empty / under-booked chairs] --> B{Do clients want this slot but can't get it cleanly?}
    B -- "no — not enough want it" --> C[DEMAND problem]
    C --> D[Seam: marketing-operations<br/>promotion, offers, new-client acquisition]
    C --> E[Operational lever: off-peak pricing,<br/>service mix that fills mid-week]
    B -- "yes — demand exists, calendar fails it" --> F[SCHEDULING problem]
    F --> G{Why can't the calendar hold it?}
    G -- "no / clunky online booking" --> H[Add or fix online booking]
    G -- "gaps between appointments" --> I[Gap-fill: shorter buffers, stack add-ons,<br/>book color processing overlap as capacity]
    G -- "skill / shift mismatch" --> J[Align stylist skills + shifts to demand]
    G -- "no-shows leaving holes" --> K[No-show/deposit policy<br/>-> deposit-policy tree]
```

**Rule:** diagnose before you fix. An empty chair is either too little *demand* (a `marketing-operations` seam, plus off-peak/mix levers) or a *scheduling* failure (online booking, gaps, color-overlap capacity, skill/shift fit, or no-shows). The fix differs entirely by cause — never throw a marketing promotion at a scheduling problem (or vice versa).

---

## Decision Tree: should I raise prices, and how?

```mermaid
graph TD
    A[Considering a price increase] --> B{Are you clearing target margin?}
    B -- "no — underpriced vs cost" --> C[Increase is warranted]
    B -- "yes, but market moved" --> C
    B -- "yes, healthy margin" --> D[Hold; revisit on schedule]
    C --> E{How loyal / price-sensitive is the book?}
    E -- "loyal, value-driven" --> F[Raise on a schedule, lead with value]
    E -- "price-sensitive / fragile retention" --> G[Stagger: by service, by stylist level,<br/>or grandfather the existing book]
    F --> H[Communicate to the existing book FIRST]
    G --> H
    H --> I[Never spring it at checkout]
```

**Rule:** raise to a target margin, not to a competitor; raise on a *schedule*; lead with *value*; *segment/grandfather* where retention is fragile; and **communicate to the existing book before the change.** The surprise at checkout — not the price — is what burns the trust rebooking depends on.

---

## Decision Tree: what no-show / deposit policy fits?

```mermaid
graph TD
    A[Setting a no-show policy] --> B{Service cost + chair time}
    B -- "quick / low-cost (trim, blowout)" --> C[Card-on-file + modest fee<br/>shorter window 24h]
    B -- "high-cost / long (color, package)" --> D[Deposit at booking<br/>longer window 48-72h]
    C --> E{Can the booking system hold a card / take a deposit?}
    D --> E
    E -- no --> F[Fix the system first<br/>a policy with no mechanism is a wish]
    E -- yes --> G[Set fee = unresellable chair-time]
    G --> H[Add reminder cadence<br/>booking / 48h / 24h]
    H --> I[Publish client-facing wording BEFORE booking]
```

**Rule:** the policy is a *mechanism*, not a sentence. Match the deposit/card and window to the service's cost and chair-time, make the system actually enforce it, set the fee to the chair-time you can't resell, and show the wording before booking. Reminders reduce honest mistakes; the deposit covers the deliberate no-show.

---

## How the agents use these trees

- `salon-spa-operations-lead` → the **compensation-model** tree before any pay-structure recommendation (always ending at the classification flag).
- `booking-and-retention-analyst` → the **empty-chair** and **deposit-policy** trees before diagnosing utilization or writing a no-show policy.
- `service-menu-and-pricing-strategist` → the **price-increase** tree before any increase.

Traverse top-to-bottom; don't keyword-match. Volatile numbers are dated in the reference map and re-verified before quoting.
