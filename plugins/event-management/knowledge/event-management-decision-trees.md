# Event Management — Decision Trees

> Reference decision trees for the `event-management` team. Agents **traverse the relevant tree top-to-bottom before choosing** (the proactive complement to the Capability Grounding Protocol). Each `## Decision Tree` section is a Mermaid graph plus the rule it encodes.
>
> _Last reviewed: 2026-06-22 by `claude`. Principles are durable; specific platform/benchmark names live (dated) in [`event-management-reference-2026.md`](event-management-reference-2026.md)._

---

## Decision Tree: in-person, virtual, or hybrid?

```mermaid
flowchart TD
    A[Choosing a format] --> B{Primary goal}
    B -- "depth / relationships / serendipity" --> C{Budget supports in-person?}
    C -- yes --> D[In-person<br/>highest cost, highest engagement]
    C -- no --> E[Virtual<br/>reach over depth]
    B -- "reach / low cost / scale" --> E
    B -- "both reach AND in-room depth" --> F{Can you staff + fund<br/>two productions?}
    F -- yes --> G[Hybrid<br/>budget + crew it as two events]
    F -- no --> H[Pick one format<br/>and do it well]
```

**Rule:** format follows goal + audience + budget. In-person buys depth at the highest cost; virtual buys reach cheaply at shallower engagement; hybrid buys both only if you fund and staff two simultaneous productions. Don't default to hybrid because it sounds inclusive.

---

## Decision Tree: budget & break-even model

```mermaid
flowchart TD
    A[Building the budget] --> B[List fixed costs<br/>venue, AV, platform, staff]
    B --> C[List variable costs<br/>per-attendee F&B, swag, badges]
    C --> D[Add a named contingency line<br/>10-20%]
    D --> E{Revenue sources}
    E -- "tickets" --> F[Break-even = fixed / contribution per ticket]
    E -- "tickets + sponsorship" --> G[Break-even = fixed - sponsorship<br/>/ contribution per ticket]
    F --> H{Projected registrations >= break-even?}
    G --> H
    H -- no --> I[Cut scope / raise price / add sponsorship<br/>or no-go]
    H -- yes --> J[Proceed; set the go/no-go threshold<br/>at/above break-even with a date]
```

**Rule:** every budget carries a named contingency line; break-even is a computed number (registrations and/or sponsorship to cover cost), and it sets the go/no-go threshold. A budget with no buffer breaks on the first surprise.

---

## Decision Tree: sponsorship tiering

```mermaid
flowchart TD
    A[Designing sponsorship] --> B{What does the sponsor want?}
    B -- "leads / pipeline" --> C[Tier built on lead capture<br/>scans, list opt-ins, meetings]
    B -- "brand exposure" --> D[Tier built on placement<br/>logo surfaces, branded moments]
    B -- "thought leadership" --> E[Tier built on stage time<br/>speaking slot, session]
    C --> F[Define deliverables per tier]
    D --> F
    E --> F
    F --> G{Each deliverable has an owner<br/>+ due date + proof method?}
    G -- no --> H[Not sellable yet —<br/>a tier is a fulfilled promise]
    G -- yes --> I[Publish prospectus; sell against value]
```

**Rule:** a sponsorship tier is a set of *delivered* deliverables, each with an owner, a due date, and a proof method — not a logo size. Sell against value; fulfill and prove every promise, because proof is what renews.

---

## Decision Tree: go / no-go gate

```mermaid
flowchart TD
    A[Approaching a go/no-go date] --> B{Registrations >= threshold?}
    B -- no --> C{Time + budget to recover?}
    C -- yes --> D[Push promotion / extend early-bird<br/>re-gate at a new date]
    C -- no --> E[No-go: cancel or pivot format<br/>before non-refundable spend]
    B -- yes --> F{Sponsorship secured >= target?}
    F -- no --> G{Can the gap be cut from scope?}
    G -- yes --> H[Trim scope to fit; GO]
    G -- no --> E
    F -- yes --> I{Speakers / key vendors confirmed?}
    I -- no --> J[Hold; confirm or trigger backups]
    I -- yes --> K[GO]
```

**Rule:** name the go/no-go criteria early — each gate has a date and a hard threshold (registrations, sponsorship, speaker/vendor confirmations). Decide it before non-refundable spend ramps; a gate with no date is decoration.

---

## See also

- [`event-management-reference-2026.md`](event-management-reference-2026.md) — dated tooling/benchmark map (re-verify before quoting platforms or rates).
- Skills: [`../skills/design-event-plan-and-budget/SKILL.md`](../skills/design-event-plan-and-budget/SKILL.md), [`../skills/build-run-of-show/SKILL.md`](../skills/build-run-of-show/SKILL.md), [`../skills/sponsorship-and-revenue/SKILL.md`](../skills/sponsorship-and-revenue/SKILL.md), [`../skills/registration-and-attendee-ops/SKILL.md`](../skills/registration-and-attendee-ops/SKILL.md), [`../skills/post-event-measurement/SKILL.md`](../skills/post-event-measurement/SKILL.md).
