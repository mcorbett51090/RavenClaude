# Wealth Management (RIA Practice) Decision Trees

> Mermaid decision trees for the three most common triage paths. Traverse top-to-bottom and pick the smaller-blast-radius leaf — don't keyword-match the symptom to a method. Each tree encodes the team's house opinions (CLAUDE.md §3).

## Tree 1 — Is the practice actually growing?

```mermaid
flowchart TD
    A[AUM up] --> B{Separated net new<br/>flows from market?}
    B -- "Not separated" --> B1[Decompose: AUM growth − net new<br/>flows = market, §3 #1]
    B -- "Separated" --> C{Organic growth<br/>positive?}
    C -- "Flat/negative" --> C1{Net new flows<br/>or attrition?}
    C1 -- "Low inflows" --> C2[New-client engine weak;<br/>but defend the book first, §3 #5]
    C1 -- "High outflows" --> C3[Attrition compounding; protect<br/>retention/capacity, §3 #4 #5]
    C -- "Positive organic" --> C4[Real growth; check it's profitable<br/>clients, route to segmentation, §3 #2]
    B1 --> D[Owner · date · organic growth target]
    C2 --> D
    C3 --> D
```

## Tree 2 — Which clients make us money?

```mermaid
flowchart TD
    A[Client value question] --> B{Ranking by AUM<br/>or profit?}
    B -- "AUM" --> B1[Wrong rank: use revenue −<br/>cost-to-serve, §3 #2]
    B -- "Profit" --> C{Below breakeven<br/>AUM?}
    C -- "Yes" --> C1{High touch /<br/>discounted fee?}
    C1 -- "Both" --> C2[Re-price, re-tier, or right-size<br/>service, §3 #2 #3]
    C1 -- "Cost-to-serve" --> C3[Reduce service intensity or<br/>raise breakpoint, §3 #2]
    C -- "Above breakeven" --> C4[Profitable; protect retention<br/>and capacity, §3 #4 #5]
    B1 --> D[Owner · date · expected margin lift]
    C2 --> D
    C3 --> D
```

## Tree 3 — Advisors over capacity?

```mermaid
flowchart TD
    A[Service/retention concern] --> B{Households per advisor<br/>vs target band?}
    B -- "Above band" --> B1[Over-capacity: a leading<br/>retention risk, §3 #4]
    B1 --> C{Review cadence<br/>slipping?}
    C -- "Yes" --> C1[Add capacity or re-tier before<br/>attrition lands, §3 #4 #5]
    C -- "Compliance cadence" --> C2[Cadence non-negotiable; protect<br/>it, route to compliance, §3 #6]
    B -- "Within band" --> D{Attrition rising<br/>anyway?}
    D -- "Yes" --> D1[Not capacity; segmentation/service<br/>fit, route to segmentation, §3 #2 #5]
    D -- "No" --> D2[Capacity healthy; pursue<br/>profitable organic growth, §3 #7]
    C1 --> E[Owner · date · expected retention movement]
    C2 --> E
    D1 --> E
```

## How to read these

- **Decompose before you act** — the first node of each tree is usually a STOP that prevents acting on an aggregate you haven't yet split.
- **Fix the constraint before adding volume** — more input into a leaking process wastes resource.
- Every leaf ends in the §6 Output Contract: owner · date · expected metric movement.
