# Customer Support & CX Operations Decision Trees

> Mermaid decision trees for the three most common triage paths. Traverse top-to-bottom and pick the smaller-blast-radius leaf — don't keyword-match the symptom to a method. Each tree encodes the team's house opinions (CLAUDE.md §3).

## Tree 1 — Queue backing up, SLAs slipping

```mermaid
flowchart TD
    A[Backlog + SLA slip] --> B{Volume modeled<br/>for deflection?}
    B -- "Not yet" --> B1[Model deflection FIRST; remove<br/>contacts before hiring, §3 #1]
    B -- "Deflected" --> C{Arrivals vs<br/>capacity?}
    C -- "Arrivals > capacity" --> C1[Flow gap: staff to workload<br/>or tier, not 'work faster', §3 #5]
    C -- "Capacity adequate" --> D{Occupancy in<br/>healthy band?}
    D -- "Over-occupied" --> D1[Burnout + AHT creep;<br/>add capacity, §3 #2]
    D -- "Healthy" --> D2[Routing/tiering or FCR issue,<br/>route to CSAT, §3 #4 #7]
    B1 --> E[Owner · date · expected SLA movement]
    C1 --> E
    D1 --> E
```

## Tree 2 — How many agents do we need?

```mermaid
flowchart TD
    A[Staffing question] --> B{Using a fixed<br/>agent:ticket ratio?}
    B -- "Yes" --> B1[Wrong model: ratio ignores AHT<br/>and occupancy, §3 #2]
    B -- "Workload-based" --> C{Forecast volume<br/>+ AHT known?}
    C -- "No" --> C1[Forecast arrivals and measure<br/>AHT by channel first, §3 #2]
    C -- "Yes" --> D{Target occupancy<br/>set?}
    D -- "No / 100%" --> D1[Set a healthy band; 100% =<br/>burnout + AHT creep, §3 #2]
    D -- "Healthy band" --> D2[Agents = workload ÷<br/>(interval × occupancy), §3 #2]
    B1 --> E[Owner · date · staffing plan]
    C1 --> E
    D2 --> E
```

## Tree 3 — Why is CSAT dropping?

```mermaid
flowchart TD
    A[CSAT down] --> B{Reading blended<br/>or segmented?}
    B -- "Blended" --> B1[Segment by channel/tier/issue;<br/>blended hides both ends, §3 #3]
    B -- "Segmented" --> C{Which segment<br/>drags it?}
    C -- "A channel/tier" --> C1{FCR falling /<br/>reopens rising?}
    C1 -- "Yes" --> C2[FCR is the driver; fix resolution,<br/>not first-reply speed, §3 #4]
    C1 -- "No" --> C3{Occupancy or<br/>routing pressure?}
    C3 -- "Over-occupied" --> C4[Staffing/burnout, route to<br/>staffing, §3 #2]
    C3 -- "Routing" --> C5[Tier/escalation redesign, §3 #7]
    B1 --> D[Owner · date · expected CSAT lift]
    C2 --> D
    C4 --> D
```

## How to read these

- **Decompose before you act** — the first node of each tree is usually a STOP that prevents acting on an aggregate you haven't yet split.
- **Fix the constraint before adding volume** — more input into a leaking process wastes resource.
- Every leaf ends in the §6 Output Contract: owner · date · expected metric movement.
