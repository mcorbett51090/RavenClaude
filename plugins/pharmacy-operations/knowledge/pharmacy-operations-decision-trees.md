# Pharmacy Operations Decision Trees

> Mermaid decision trees for the three most common triage paths. Traverse top-to-bottom and pick the smaller-blast-radius leaf — don't keyword-match the symptom to a method. Each tree encodes the team's house opinions (CLAUDE.md §3).

## Tree 1 — Drowning in scripts

```mermaid
flowchart TD
    A[Fill backlog / pressure] --> B{Verification capacity<br/>covers fill volume?}
    B -- "No — deficit" --> B1[SAFETY risk, not just backlog:<br/>protect verification first, §3 #1]
    B -- "Yes" --> C{Staffed to volume<br/>PLUS clinical time?}
    C -- "Fixed ratio" --> C1[Re-size to volume + clinical<br/>service time, §3 #5]
    C -- "Volume only" --> C2[Add the clinical-service<br/>hours load, §3 #5]
    C -- "Both covered" --> D{Stockouts<br/>stalling fills?}
    D -- "Yes" --> D1[Inventory problem,<br/>route to inventory, §3 #2]
    D -- "No" --> D2[Workflow/automation tuning<br/>— safety still the constraint, §3 #1]
    B1 --> E[Owner · date · expected safety + throughput movement]
    C1 --> E
    D1 --> E
```

## Tree 2 — Margin is thin despite volume

```mermaid
flowchart TD
    A[Thin margin, high volume] --> B{Margin computed<br/>net of DIR?}
    B -- "Sticker only" --> B1[Recompute net of DIR/clawback<br/>FIRST, §3 #3]
    B -- "Net of DIR" --> C{Negative-margin<br/>scripts?}
    C -- "Yes" --> C1{Specialty/340B/<br/>refrigerated?}
    C1 -- "Yes" --> C2[Price/handle distinctly;<br/>route 340B compliance out, §3 #6]
    C1 -- "No" --> C3[Drug-class mix / contract<br/>renegotiation, §3 #3]
    C -- "All positive" --> D{Days-on-hand<br/>tying up cash?}
    D -- "High on specialty" --> D1[Right-size specialty DOH,<br/>§3 #2 #6]
    D -- "Balanced" --> D2[Throughput/staffing cost,<br/>route to fill-workflow, §3 #5]
    B1 --> E[Owner · date · expected margin movement]
    C2 --> E
    C3 --> E
    D1 --> E
```

## Tree 3 — Star adherence measure dropped

```mermaid
flowchart TD
    A[Adherence star measure down] --> B{PDC measured over<br/>a defined period?}
    B -- "No clear period" --> B1[Define the measurement<br/>period FIRST, §3 #4 #8]
    B -- "Yes" --> C{Where do patients sit<br/>vs the band threshold?}
    C -- "Near threshold" --> C1[Target intervention here —<br/>moves the measure most, §3 #4]
    C -- "Far below" --> C2{Fill gap / refill<br/>timing?}
    C2 -- "Operational gap" --> C3[Refill sync / reminders,<br/>operational fix, §3 #4]
    C2 -- "Therapy question" --> C4[Route drug-therapy judgment<br/>to the pharmacist, §3 #8 §2]
    C1 --> D[Owner · date · expected PDC + star movement]
    C3 --> D
    C4 --> D
```

## How to read these

- **Decompose before you act** — the first node of each tree is usually a STOP that prevents acting on an aggregate you haven't yet split.
- **Fix the constraint before adding volume** — more input into a leaking process wastes resource.
- Every leaf ends in the §6 Output Contract: owner · date · expected metric movement.
