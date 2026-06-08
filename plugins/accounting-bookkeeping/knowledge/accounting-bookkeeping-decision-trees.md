# Accounting & Bookkeeping Practice Decision Trees

> Mermaid decision trees for the three most common triage paths. Traverse top-to-bottom and pick the smaller-blast-radius leaf — don't keyword-match the symptom to a method. Each tree encodes the team's house opinions (CLAUDE.md §3).

## Tree 1 — Close keeps slipping

```mermaid
flowchart TD
    A[Close slipping past target] --> B{Accounts<br/>reconciled?}
    B -- "Un-reconciled" --> B1[Reconcile FIRST; close can't finish<br/>on books that don't tie, §3 #2]
    B -- "Reconciled" --> C{Bottleneck on the<br/>critical path?}
    C -- "One long task" --> C1[Attack that task; parallelize<br/>the rest, §3 #1]
    C -- "Many small tasks" --> C2{AP/AR cutoff or<br/>accrual timing?}
    C2 -- "Cutoff" --> C3[Tighten cutoff, route to<br/>AP/AR, §3 #4]
    C2 -- "COA coding" --> C4[Clean COA, route to<br/>controls, §3 #7]
    B1 --> D[Owner · date · target days-to-close]
    C1 --> D
    C3 --> D
```

## Tree 2 — Profitable but cash is tight

```mermaid
flowchart TD
    A[Profit up, cash tight] --> B{Basis stated?}
    B -- "Not stated" --> B1[State accrual vs cash; profit and<br/>cash diverge by basis, §3 #6]
    B -- "Stated" --> C{DSO high?}
    C -- "Yes" --> C1[Cash trapped in AR; collections +<br/>aging/bad-debt, §3 #3]
    C -- "No" --> D{DPO too low?}
    D -- "Paying too early" --> D1[Surrendering free financing;<br/>tune AP timing, §3 #4]
    D -- "DIO high" --> D2[Cash tied in inventory;<br/>review stock]
    C1 --> E[Owner · date · expected cash freed]
    D1 --> E
    D2 --> E
```

## Tree 3 — Books don't tie out

```mermaid
flowchart TD
    A[Books don't tie] --> B{Accounts<br/>reconciled to source?}
    B -- "No" --> B1[Reconcile each bank/balance-sheet<br/>account before reporting, §3 #2]
    B -- "Yes" --> C{COA clean?}
    C -- "Catch-alls/dupes" --> C1[Clean the chart of accounts<br/>before analysis, §3 #7]
    C -- "Clean" --> D{Segregation of<br/>duties intact?}
    D -- "Approve=enter=reconcile" --> D1[Control gap; add SoD or<br/>compensating controls, §3 #5]
    D -- "Separated" --> D2{Variance looks like<br/>fraud or error?}
    D2 -- "Possible fraud" --> D3[Route to licensed CPA +<br/>qualified authority, §2]
    B1 --> E[Owner · date · re-reconcile before reporting]
    C1 --> E
    D1 --> E
```

## How to read these

- **Decompose before you act** — the first node of each tree is usually a STOP that prevents acting on an aggregate you haven't yet split.
- **Fix the constraint before adding volume** — more input into a leaking process wastes resource.
- Every leaf ends in the §6 Output Contract: owner · date · expected metric movement.
