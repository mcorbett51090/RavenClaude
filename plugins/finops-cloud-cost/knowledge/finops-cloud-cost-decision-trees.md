# FinOps & Cloud Cost Decision Trees

> Mermaid decision trees for the three most common triage paths. Traverse top-to-bottom and pick the smaller-blast-radius leaf — don't keyword-match the symptom to a method. Each tree encodes the team's house opinions (CLAUDE.md §3).

## Tree 1 — Bill jumped, where to start

```mermaid
flowchart TD
    A[Bill up sharply] --> B{Is spend<br/>allocated?}
    B -- "Below usable coverage" --> B1[Allocate first: tagging + showback;<br/>can't govern what you can't see, §3 #1]
    B -- "Allocated" --> C{Obvious waste<br/>present?}
    C -- "Idle/orphaned/oversized" --> C1[Harvest waste first — pure<br/>savings, no trade-off, §3 #5]
    C -- "Lean" --> D{Unit cost rising<br/>or just the bill?}
    D -- "Bill up, unit cost flat/down" --> D1[Healthy scaling; forecast +<br/>budget, not panic, §3 #2 #7]
    D -- "Unit cost rising" --> D2[Decay: attribute the driving<br/>service, route to unit economics, §3 #2]
    B1 --> E[Owner · date · $ impact]
    C1 --> E
    D2 --> E
```

## Tree 2 — Bill grows faster than revenue

```mermaid
flowchart TD
    A[Spend outpaces revenue] --> B{Allocated to a<br/>unit denominator?}
    B -- "No unit" --> B1[Pick the unit (customer/txn/<br/>feature) and allocate, §3 #1 #2]
    B -- "Has units" --> C{Cost per unit<br/>trend?}
    C -- "Falling" --> C1[Healthy: growth is buying<br/>efficiency; forecast it, §3 #2 #7]
    C -- "Rising" --> D{Which service<br/>drives it?}
    D -- "Idle/oversized" --> D1[Waste/rightsizing problem,<br/>route to commitments, §3 #5 #4]
    D -- "Genuine usage growth" --> D2[Architecture/efficiency review;<br/>frame, route design to authority, §2]
    C1 --> E[Owner · date · expected unit-cost movement]
    D1 --> E
    D2 --> E
```

## Tree 3 — Should we buy commitments?

```mermaid
flowchart TD
    A[Considering RIs/Savings Plans] --> B{Baseline<br/>rightsized?}
    B -- "Not rightsized" --> B1[STOP: rightsize + kill waste first,<br/>or you lock in waste, §3 #4 #5]
    B -- "Lean baseline" --> C{Usage steady<br/>or volatile?}
    C -- "Steady floor" --> C1[Cover the steady-state floor;<br/>model coverage, §3 #3]
    C -- "Volatile" --> C2[Lower coverage; flexibility has<br/>value, utilization risk is real, §3 #3]
    C1 --> D{Marginal discount ><br/>marginal lock-in risk?}
    C2 --> D
    D -- "Yes" --> D1[Buy that coverage tier; verify<br/>discount vs live pricing, §3 #8]
    D -- "No" --> D2[Hold coverage; revisit at<br/>next cycle]
    D1 --> E[Owner · date · $ savings + utilization risk]
    B1 --> E
```

## How to read these

- **Decompose before you act** — the first node of each tree is usually a STOP that prevents acting on an aggregate you haven't yet split.
- **Fix the constraint before adding volume** — more input into a leaking process wastes resource.
- Every leaf ends in the §6 Output Contract: owner · date · expected metric movement.
