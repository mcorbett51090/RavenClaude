# Property Management Operations Decision Trees

> Mermaid decision trees for the three most common triage paths. Traverse top-to-bottom and pick the smaller-blast-radius leaf — don't keyword-match the symptom to a method. Each tree encodes the team's house opinions (CLAUDE.md §3).

## Tree 1 — NOI is soft

```mermaid
flowchart TD
    A[NOI soft] --> B{EGI or<br/>opex driven?}
    B -- "EGI down" --> C{Occupancy or<br/>rate/loss?}
    C -- "Occupancy" --> C1[Route to leasing funnel +<br/>renewals, §3 #1 #6]
    C -- "Rate / loss-to-lease" --> C2[Concession + rent discipline,<br/>§3 #5]
    B -- "Opex up" --> D{Recurring or<br/>one-off?}
    D -- "Recurring" --> D1[Structural opex line;<br/>investigate driver, §3 #4]
    D -- "One-off / capital" --> D2[Capex vs opex<br/>classification, §3 #7]
    C1 --> E[Owner · date · expected NOI lift]
    C2 --> E
    D1 --> E
    D2 --> E
```

## Tree 2 — Property won't lease up

```mermaid
flowchart TD
    A[Slow lease-up] --> B{Renewals<br/>holding?}
    B -- "Renewals dropping" --> B1[Fix retention FIRST —<br/>cheaper than acquisition, §3 #6]
    B -- "Renewals fine" --> C{Where does the<br/>funnel leak?}
    C -- "Leads/traffic low" --> C1[Marketing / pricing-to-market,<br/>§3 #5]
    C -- "Tour->application" --> C2[Product / model-unit / price]
    C -- "Application->signed" --> C3{Screening or<br/>turn-ready?}
    C3 -- "Screening" --> C4[Application process / criteria]
    C3 -- "No ready units" --> C5[Turn-time gate, route to<br/>maintenance, §3 #3]
    B1 --> D[Owner · date · expected occupancy lift]
    C1 --> D
    C2 --> D
    C4 --> D
    C5 --> D
```

## Tree 3 — Delinquency rising

```mermaid
flowchart TD
    A[Delinquency rising] --> B{Read the aging}
    B -- "Concentrated in 0-30" --> B1[Recent / process issue;<br/>collectable, push now, §3 #2]
    B -- "Migrating to 60+" --> C{Broad or<br/>few residents?}
    C -- "Few residents" --> C1[Resident-specific; route<br/>legal/eviction to counsel, §2]
    C -- "Broad" --> C2[Systemic: billing, screening,<br/>or affordability, §3 #2]
    B1 --> D[Carry realistic bad-debt into<br/>the EGI bridge, §3 #4]
    C1 --> D
    C2 --> D
```

## How to read these

- **Decompose before you act** — the first node of each tree is usually a STOP that prevents acting on an aggregate you haven't yet split.
- **Fix the constraint before adding volume** — more input into a leaking process wastes resource.
- Every leaf ends in the §6 Output Contract: owner · date · expected metric movement.
