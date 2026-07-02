# Fitness Studio / Gym Operations — Decision Trees

> Reference decision trees for the `fitness-studio-gym-operations` team. Agents **traverse the relevant tree top-to-bottom before deciding** (the proactive complement to the Capability Grounding Protocol). Each `## Decision Tree` section is a Mermaid graph plus the rule it encodes.
>
> **Advisory operations knowledge, not legal, financial, or medical/exercise-prescription advice.** Anything touching a churn/LTV benchmark, class-fill target, or instructor-pay norm is `[verify-at-use]` — confirm against your own books and current market data before acting. No member PII.
>
> _Last reviewed: 2026-07-02 by `claude`. Principles are durable; dated benchmarks and concepts live in [`fitness-studio-reference-2026.md`](fitness-studio-reference-2026.md)._

---

## Decision Tree: churn-save triage — catch and keep a member

```mermaid
flowchart TD
    A[Member at risk or requesting cancel] --> B{How was it detected?}
    B -- "attendance decay signal<br/>(visits/week down,<br/>days-since-last-visit high)" --> C[Proactive re-engage<br/>BEFORE they ask to cancel]
    B -- "explicit cancel request" --> D{What is the real cause?}
    D -- "price / affordability" --> E[Downgrade tier or class-pack<br/>NOT a permanent discount]
    D -- "life change / travel" --> F[Freeze or pause]
    D -- "injury / health" --> G[Medical pause + return plan]
    D -- "boredom / plateau" --> H[Program change / new class<br/>/ PT assessment]
    D -- "moved away" --> I[Graceful let-go<br/>+ add to win-back list]
    C --> J[Log the save + cause<br/>fix the pattern, not one member]
    E --> J
    F --> J
    G --> J
    H --> J
```

**Rule:** churn is predicted by **attendance decay, not the cancel form** — catch it early. When a cancel does come, **match the save to the cause**; a blanket discount cuts LTV and trains the threat. Benchmarks `[verify-at-use]`.

---

## Decision Tree: membership pricing / tier model

```mermaid
flowchart TD
    A[Set or change membership pricing] --> B{What commitment are you selling?}
    B -- "high-frequency, committed" --> C[Unlimited + contract<br/>highest LTV, lowest churn per member]
    B -- "moderate / variable use" --> D[Month-to-month unlimited<br/>higher churn, price the flexibility]
    B -- "low-frequency / trial" --> E[Class-pack or punch card<br/>no recurring anchor — win-back path]
    C --> F{Ancillary attach mapped?}
    D --> F
    E --> F
    F -- no --> G[Model PT/retail/cafe revenue-per-member<br/>BEFORE raising dues]
    F -- yes --> H[Price each tier on value + commitment<br/>name the churn + LTV of each]
```

**Rule:** price on **value and commitment**, not the competitor's sign. Contract/unlimited, month-to-month, and class-pack are distinct churn + LTV profiles — architect them deliberately, and check ancillary headroom before defaulting to a dues increase. All numbers `[verify-at-use]`.

---

## Decision Tree: schedule the class grid on fill

```mermaid
flowchart TD
    A[Reviewing a class slot] --> B{Fill vs break-even headcount}
    B -- "persistently below break-even" --> C{Waitlist ever forms<br/>at a nearby time?}
    C -- yes --> D[Re-time toward the demand]
    C -- no --> E[Cut or merge the slot]
    B -- "at / above break-even<br/>with headroom" --> F{Booked >> attended?}
    F -- yes --> G[No-show/late-cancel policy<br/>+ auto-promote waitlist]
    F -- no --> H{Waitlist forming?}
    H -- yes --> I[Add a parallel / adjacent slot]
    H -- no --> J[Healthy slot — hold it]
```

**Rule:** schedule the grid on **demand, not habit**. Defend a slot with its fill against a known break-even headcount, reclaim held-but-no-show seats with policy, and add capacity only where a waitlist proves demand. Fill targets `[verify-at-use]`.

---

## Decision Tree: instructor pay model

```mermaid
flowchart TD
    A[Choosing an instructor pay model] --> B{How variable is class fill?}
    B -- "high, predictable fill" --> C[Flat per class<br/>simple; you keep upside on full classes]
    B -- "variable / growth phase" --> D{Want to share empty-class risk?}
    D -- yes --> E[Per head<br/>instructor shares the fill risk]
    D -- "partly" --> F[Base + per head<br/>floor for the instructor,<br/>upside shared]
    C --> G[Check: does flat overpay<br/>your empty classes? verify-at-use]
    E --> H[Check: does per-head underpay<br/>a draw instructor you must retain?]
    F --> I[Set base + rate against<br/>per-class contribution margin]
```

**Rule:** match the pay model to **fill economics and contribution margin**, not convenience. Flat-per-class overpays empty classes and undersells packed ones; per-head shares the risk; base+per-head balances. Know the per-class break-even before you commit. Pay norms `[verify-at-use]`.

---

## See also

- [`fitness-studio-reference-2026.md`](fitness-studio-reference-2026.md) — dated concepts + benchmarks (verify-at-use).
- Skills: [`../skills/membership-growth-and-churn/SKILL.md`](../skills/membership-growth-and-churn/SKILL.md), [`../skills/member-onboarding-and-retention/SKILL.md`](../skills/member-onboarding-and-retention/SKILL.md), [`../skills/class-schedule-and-instructor-utilization/SKILL.md`](../skills/class-schedule-and-instructor-utilization/SKILL.md), [`../skills/ancillary-revenue-mix/SKILL.md`](../skills/ancillary-revenue-mix/SKILL.md).
