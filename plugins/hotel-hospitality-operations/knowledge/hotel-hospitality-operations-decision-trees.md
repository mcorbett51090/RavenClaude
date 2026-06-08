# Hotel & Hospitality Operations Decision Trees

> Mermaid decision trees for the three most common triage paths. Traverse top-to-bottom and pick the smaller-blast-radius leaf — don't keyword-match the symptom to a method. Each tree encodes the team's house opinions (CLAUDE.md §3).

## Tree 1 — Occupancy up but profit isn't

```mermaid
flowchart TD
    A[Occupancy up, profit flat/down] --> B{RevPAR up<br/>or flat?}
    B -- "RevPAR flat/down" --> B1[Rate was cut to fill —<br/>wrong trade-off, §3 #1]
    B -- "RevPAR up" --> C{GOPPAR<br/>following?}
    C -- "GOPPAR lagging" --> D{Acquisition or<br/>labor cost?}
    D -- "Channel cost" --> D1[Revenue bought via OTA<br/>commission; shift mix, §3 #2]
    D -- "Labor cost" --> D2[Over-staffed vs occupancy;<br/>flex labor, §3 #4]
    C -- "GOPPAR up" --> C1[Healthy: protect with<br/>guest experience, §3 #6]
    B1 --> E[Owner · date · expected RevPAR/GOPPAR lift]
    D1 --> E
    D2 --> E
```

## Tree 2 — Labor over budget

```mermaid
flowchart TD
    A[Labor over budget] --> B{Per-occupied-room<br/>or total?}
    B -- "Total only" --> B1[Re-read as hours per<br/>occupied room first, §3 #4]
    B -- "Per-occ-room high" --> C{Which<br/>department?}
    C -- "Rooms/housekeeping" --> C1[Hours standard vs<br/>occupancy forecast]
    C -- "F&B / other" --> C2[Volume-driven vs<br/>fixed coverage]
    C1 --> D{Service level<br/>at risk?}
    C2 --> D
    D -- "Yes" --> D1[Protect guest experience —<br/>it's a revenue input, §3 #6]
    D -- "No" --> D2[Flex roster to the<br/>pace forecast, §3 #4]
    B1 --> E[Owner · date · expected cost/occ-room lift]
    D1 --> E
    D2 --> E
```

## Tree 3 — Pacing behind for a future period

```mermaid
flowchart TD
    A[Behind pace] --> B{Demand soft<br/>broadly or a gap?}
    B -- "Specific gap night" --> B1{Stimulate or<br/>shift segment?}
    B1 -- "Transient soft" --> B2[Targeted promotion /<br/>channel push, §3 #2]
    B1 -- "Need certainty" --> B3[Group/corporate to<br/>de-risk pace, §3 #7]
    B -- "Broad softness" --> C{Comp set<br/>also soft?}
    C -- "Market-wide" --> C1[Hold rate integrity;<br/>don't lead a rate war, §3 #1]
    C -- "Just us" --> C2[Rate/positioning or<br/>reputation issue, §3 #6]
    B2 --> D[Owner · date · expected pickup]
    B3 --> D
    C1 --> D
    C2 --> D
```

## How to read these

- **Decompose before you act** — the first node of each tree is usually a STOP that prevents acting on an aggregate you haven't yet split.
- **Fix the constraint before adding volume** — more input into a leaking process wastes resource.
- Every leaf ends in the §6 Output Contract: owner · date · expected metric movement.
