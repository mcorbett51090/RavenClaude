# Sales & Revenue Operations Decision Trees

> Mermaid decision trees for the three most common triage paths. Traverse top-to-bottom and pick the smaller-blast-radius leaf — don't keyword-match the symptom to a method. Each tree encodes the team's house opinions (CLAUDE.md §3).

## Tree 1 — Forecast keeps missing

```mermaid
flowchart TD
    A[Forecast missing] --> B{Coverage adequate<br/>against quota?}
    B -- "Below target ratio" --> B1[Pipeline-creation problem.<br/>Lead/demand gen + coverage gap, §3 #1 #5]
    B -- "Adequate" --> C{Forecast weighted<br/>and aged?}
    C -- "Summed commits" --> C1[Model problem: weight by stage<br/>win-rate, age the pipeline, §3 #2 #6]
    C -- "Weighted+aged" --> D{Slip concentrated<br/>or broad?}
    D -- "A few whales" --> D1[Deal-specific risk; not a<br/>process finding]
    D -- "Broad slip" --> D2[Stage dwell / qualification<br/>problem, route to funnel, §3 #3]
    C1 --> E[Owner · date · expected accuracy lift]
    B1 --> E
    D2 --> E
```

## Tree 2 — Win-rate dropped

```mermaid
flowchart TD
    A[Win-rate down] --> B{Which stage<br/>leaks?}
    B -- "Lead→qual" --> B1[Lead quality / ICP fit;<br/>not 'more leads', §3 #3]
    B -- "Qual→demo" --> B2[Qualification bar mis-set]
    B -- "Demo→proposal" --> B3[Value/fit or competitor;<br/>discovery depth]
    B -- "Proposal→close" --> B4{Price/terms or<br/>decision process?}
    B4 -- "Price" --> B5[Packaging/discount discipline]
    B4 -- "Process" --> B6[Champion/decision-maker access]
    B1 --> C[Fix the leaking stage FIRST,<br/>then add volume, §3 #3]
    B2 --> C
    B3 --> C
    B5 --> C
    B6 --> C
```

## Tree 3 — Half the team misses quota

```mermaid
flowchart TD
    A[Chronic under-attainment] --> B{Read the distribution}
    B -- "Median near 100%, few low" --> B1[Performance/coaching issue<br/>on specific reps]
    B -- "Median well below 100%" --> C{Capacity-tied<br/>quota?}
    C -- "Top-down number" --> C1[Quota-design error: refit to<br/>ramped capacity, §3 #4]
    C -- "Capacity-tied" --> D{Territories<br/>balanced?}
    D -- "Imbalanced TAM/accounts" --> D1[Territory design, not<br/>performance, §3 #7]
    D -- "Balanced" --> D2[Funnel/velocity constraint,<br/>route to funnel, §3 #3]
    C1 --> E[Owner · date · expected attainment lift]
    D1 --> E
    D2 --> E
```

## How to read these

- **Decompose before you act** — the first node of each tree is usually a STOP that prevents acting on an aggregate you haven't yet split.
- **Fix the constraint before adding volume** — more input into a leaking process wastes resource.
- Every leaf ends in the §6 Output Contract: owner · date · expected metric movement.
