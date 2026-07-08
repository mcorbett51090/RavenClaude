# Med-Spa / Medical Aesthetics — Decision Trees

> Reference decision trees for the `med-spa-aesthetics` team. Agents **traverse the relevant tree top-to-bottom before deciding** (the proactive complement to the Capability Grounding Protocol). Each `## Decision Tree` section is a Mermaid graph plus the rule it encodes.
>
> **Operations and financial decision-support, not legal, tax, or medical advice.** Anything touching scope of practice, supervision, good-faith exam, consent sufficiency, or corporate-practice-of-medicine is state-specific, `[verify-at-use]`, and routes to the medical director and a licensed professional. Clinical treatment plans and intervals are the provider's call. Benchmarks (injector productivity, service margins, membership norms) are volatile — confirm before quoting. No patient PHI/PII.
>
> _Last reviewed: 2026-07-04 by `claude`. Principles are durable; dated benchmarks live in [`med-spa-reference-2026.md`](med-spa-reference-2026.md)._

---

## Decision Tree: add a service or capital device

```mermaid
flowchart TD
    A[Considering a new service or device] --> B{Is the current scarce resource<br/>injector or room already full at peak?}
    B -- "no, capacity is idle" --> C[Fill existing capacity first<br/>a new device won't fix a fill problem]
    B -- "yes, running full" --> D{Capital device or<br/>consumable-only service?}
    D -- "consumable-only" --> E{Contribution per injector-hour<br/>clears the menu?}
    E -- yes --> F[Add it; wire consult conversion + cadence]
    E -- no --> C
    D -- "capital device" --> G{Payback on REALISTIC volume<br/>clears the room-hours it locks up?}
    G -- "no / only at vendor's full-util" --> H[Decline or renegotiate<br/>idle device beats displaced hours]
    G -- "yes, at honest volume" --> I[Buy; name break-even utilization<br/>+ compliance structure -> advisor]
```

**Rule:** capacity first, contribution second, honest payback third. Never add a capital device to fix a fill problem, and never accept the vendor's full-utilization payback — model the practice's realistic booking against the room-hours the device locks up. Every device that touches scope routes its compliance structure to `aesthetics-compliance-advisor`. Margins/payback are `[verify-at-use]`.

---

## Decision Tree: design the membership

```mermaid
flowchart TD
    A[Designing a membership / package] --> B{Goal: smooth cash, pre-fill book,<br/>or drive a specific service?}
    B --> C{Included value modeled<br/>against redemption?}
    C -- "no, priced on gross" --> D[Stop: breakage is a liability<br/>model redemption first]
    C -- "yes" --> E{Does the included value<br/>pre-commit scarce injector/room hours?}
    E -- "yes, at peak" --> F[Cap or steer redemption to off-peak<br/>protect peak capacity]
    E -- "no / off-peak" --> G[Price on redemption + margin<br/>enroll at consult & post-treatment]
    F --> G
    G --> H[Track redemption rate + churn<br/>hand economics to ops-lead]
```

**Rule:** a membership is a demand-smoothing and retention tool, not free money. Model redemption before counting revenue, steer redemption away from peak scarce hours, and enroll at the moments of trust (consult, post-first-treatment). Breakage is a liability, not a windfall. Membership norms are `[verify-at-use]`.

---

## Decision Tree: rebook on the treatment cadence

```mermaid
flowchart TD
    A[Patient finishing a treatment] --> B{Did the provider set a<br/>clinically recommended return interval?}
    B -- no --> C[Provider sets the cadence<br/>coordinator does NOT prescribe]
    B -- yes --> D{Front desk offers the specific<br/>next appointment at that interval?}
    C --> D
    D -- "'we'll call you'" --> E[Weak: retention leaks<br/>reframe to book-it-now]
    D -- "offers a real slot" --> F{Patient hesitant<br/>to commit the date?}
    F -- yes --> G[Deposit-to-hold or<br/>tentative + reminder]
    F -- no --> H[Book it -> patient retained on cadence<br/>track rebook rate per provider]
    G --> H
```

**Rule:** the highest-yield retention act is booking the next visit at the **provider-set** clinical interval before the patient leaves. The provider owns the cadence; the coordinator operationalizes booking it. "We'll call you" is a hope; a booked slot is retention. Track rebook rate per provider.

---

## Decision Tree: scope & supervision structure

```mermaid
flowchart TD
    A[Service raises a who-may-perform question] --> B{Is this an operations question<br/>or a determination?}
    B -- "structure: who delegates, what exam, what consent" --> C[Map the structure<br/>elements that must exist]
    B -- "the actual rule: may X inject? what supervision?" --> D[Do NOT answer<br/>state-specific determination]
    C --> E{Any specific rule quoted?}
    E -- yes --> F[Flag state-specific + verify-at-use]
    E -- no --> G[Structure map delivered]
    F --> H[Route determination to medical director<br/>+ licensed professional]
    D --> H
    G --> H
```

**Rule:** separate **structure** (which you may map) from **determination** (which you may not make). Scope, supervision level, good-faith-exam requirements, consent sufficiency, and corporate-practice-of-medicine are state-specific legal/medical determinations — flag every specific `[verify-at-use]` and route it to the medical director and a licensed professional. Flag, never decide.

---

## See also

- [`med-spa-reference-2026.md`](med-spa-reference-2026.md) — dated benchmarks + concepts (verify-at-use).
- Skills: [`../skills/service-mix-injectables-devices-memberships/SKILL.md`](../skills/service-mix-injectables-devices-memberships/SKILL.md), [`../skills/consult-to-treatment-conversion/SKILL.md`](../skills/consult-to-treatment-conversion/SKILL.md), [`../skills/treatment-room-and-injector-utilization/SKILL.md`](../skills/treatment-room-and-injector-utilization/SKILL.md), [`../skills/scope-of-practice-and-supervision/SKILL.md`](../skills/scope-of-practice-and-supervision/SKILL.md).
