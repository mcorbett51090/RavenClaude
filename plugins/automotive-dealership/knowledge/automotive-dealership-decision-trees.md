# Automotive Dealership Operations Decision Trees

> Mermaid decision trees for the three most common triage paths. Traverse top-to-bottom and pick the smaller-blast-radius leaf — don't keyword-match the symptom to a method. Each tree encodes the team's house opinions (CLAUDE.md §3).

## Tree 1 — Store profitability is thin

```mermaid
flowchart TD
    A[Thin profitability] --> B{Below service<br/>absorption?}
    B -- "Yes (<100%)" --> B1[Structural: fix fixed-ops FIRST,<br/>store can't live on front, §3 #1 #5]
    B -- "No (>=100%)" --> C{Inventory carrying<br/>cost high?}
    C -- "High days-supply" --> C1[Floorplan drag: price-to-turn<br/>aged units, §3 #2]
    C -- "In line" --> D{Total gross or<br/>volume?}
    D -- "Total gross/unit low" --> D1[Read front + back;<br/>lift compliant F&I, §3 #3 #4]
    D -- "Volume low" --> D2[Funnel conversion step,<br/>not traffic, §3 #6]
    B1 --> E[Owner · date · expected gross/absorption lift]
    C1 --> E
    D1 --> E
    D2 --> E
```

## Tree 2 — Absorption below 100%

```mermaid
flowchart TD
    A[Absorption < 100%] --> B{Fixed-ops gross<br/>or overhead?}
    B -- "Gross low" --> C{Labor or<br/>parts?}
    C -- "Labor" --> C1[Effective labor rate /<br/>tech productivity]
    C -- "Parts" --> C2[Parts margin / mix]
    B -- "Overhead high" --> B1[Fixed-expense structure;<br/>not a service-gross fix]
    C1 --> D{Retention<br/>feeding it?}
    C2 --> D
    D -- "Retention low" --> D1[Service retention erodes the<br/>annuity, §3 #7]
    D -- "Retention fine" --> D2[Capacity / throughput]
    B1 --> E[Owner · date · expected absorption lift]
    D1 --> E
    D2 --> E
```

## Tree 3 — Sales volume is short

```mermaid
flowchart TD
    A[Volume short] --> B{Traffic (ups)<br/>down?}
    B -- "Ups low" --> B1[Marketing / inventory mix;<br/>then re-check funnel]
    B -- "Ups fine" --> C{Which step<br/>leaks?}
    C -- "Up->write-up" --> C1[Lead handling / response time]
    C -- "Write-up->sold" --> C2{Desk or<br/>F&I/finance?}
    C2 -- "Desk/price" --> C3[Desking / gross discipline, §3 #3]
    C2 -- "Finance" --> C4[Approval / structure; lending<br/>questions to counsel, §2]
    B1 --> D[Owner · date · expected close-rate lift]
    C1 --> D
    C3 --> D
    C4 --> D
```

## How to read these

- **Decompose before you act** — the first node of each tree is usually a STOP that prevents acting on an aggregate you haven't yet split.
- **Fix the constraint before adding volume** — more input into a leaking process wastes resource.
- Every leaf ends in the §6 Output Contract: owner · date · expected metric movement.
