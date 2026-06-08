# Mortgage Lending Operations Decision Trees

> Mermaid decision trees for the three most common triage paths. Traverse top-to-bottom and pick the smaller-blast-radius leaf — don't keyword-match the symptom to a method. Each tree encodes the team's house opinions (CLAUDE.md §3).

## Tree 1 — Pull-through dropped

```mermaid
flowchart TD
    A[Pull-through down] --> B{Which stage<br/>falls out worst?}
    B -- "App→approved" --> B1[Application quality / doc<br/>completeness at intake, §3 #1]
    B -- "Approved→CTC" --> B2{Cycle bottleneck?}
    B2 -- "Yes" --> B3[Processing bottleneck,<br/>route to cycle, §3 #2 #4]
    B2 -- "No" --> B4[Conditions/QC backlog,<br/>route to compliance, §3 #6]
    B -- "CTC→funded" --> B5[Late-stage lock/rate or<br/>conditions; frame pipeline risk, §3 #3]
    B1 --> C[Fix the worst stage FIRST,<br/>then buy apps, §3 #1]
    B3 --> C
    B4 --> C
    B5 --> C
```

## Tree 2 — Cycle time too long

```mermaid
flowchart TD
    A[Cycle time climbing] --> B{Bottleneck stage<br/>localized?}
    B -- "Not localized" --> B1[Measure dwell by stage<br/>FIRST, §3 #2]
    B -- "Localized" --> C{Capacity or<br/>process?}
    C -- "Capacity" --> C1[Staff to cycle, not a fixed<br/>ratio; size capacity, §3 #4]
    C -- "Process" --> C2[Rework the bottleneck<br/>stage workflow, §3 #2]
    C1 --> D{Rate cycle<br/>turning?}
    D -- "Yes" --> D1[Staff to the swing/breakeven,<br/>not the peak, §3 #7]
    D -- "No" --> E[Owner · date · expected cycle + capacity movement]
    C2 --> E
    D1 --> E
```

## Tree 3 — Is this a compliance question?

```mermaid
flowchart TD
    A[Compliance / audit concern] --> B{Operational workflow<br/>or a determination?}
    B -- "Workflow / QC signal" --> B1[Team frames the operational<br/>gap + defect rate, §3 #6]
    B -- "TRID/ECOA/HMDA/<br/>fair-lending/UDAAP" --> C[Route the determination to<br/>counsel — NEVER in-team, §2 #6]
    B1 --> D{Does the gap<br/>need a ruling?}
    D -- "Yes" --> C
    D -- "No" --> E[Operational fix with owner · date]
    C --> F[Counsel renders the determination;<br/>team executes the operational fix]
```

## How to read these

- **Decompose before you act** — the first node of each tree is usually a STOP that prevents acting on an aggregate you haven't yet split.
- **Fix the constraint before adding volume** — more input into a leaking process wastes resource.
- Every leaf ends in the §6 Output Contract: owner · date · expected metric movement.
