# People-Ops Decision Trees

> Mermaid decision trees for the three most common People-Ops triage paths. Traverse top-to-bottom and pick the smaller-blast-radius leaf — don't keyword-match the symptom to a method. Each tree encodes the team's house opinions (CLAUDE.md §3).

## Tree 1 — Rising attrition

```mermaid
flowchart TD
    A[Attrition is up] --> B{Split regretted vs<br/>non-regretted?}
    B -- "Not split yet" --> B1[STOP: split first.<br/>Non-regretted may be<br/>intended managing-out, §3 #1]
    B -- "Regretted is up" --> C{Localized to a<br/>team / manager / level?}
    C -- "Concentrated" --> C1[Manager / span / role issue.<br/>Team-level deltas, §3 #7]
    C -- "Broad-based" --> D{Driver?}
    D -- "Comp" --> D1[Route: total-rewards-comp-analyst<br/>band vs market, compression, §3 #2]
    D -- "Manager / growth" --> D2[Engagement read by cohort, §3 #4<br/>+ internal-mobility check]
    D -- "Workload / burnout" --> D3[Span + capacity vs hiring plan, §3 #6]
    C1 --> E[Cost it: regretted × replacement cost, §3 #1]
    D1 --> E
    D2 --> E
    D3 --> E
    E --> F[Ranked actions: owner · date · expected movement]
```

## Tree 2 — Open req won't close

```mermaid
flowchart TD
    A[Req open too long] --> B{Where does the<br/>funnel leak?}
    B -- "Top: few sourced" --> B1[Sourcing/JD/market problem.<br/>Channel mix + JD, not just 'post more', §3 #3]
    B -- "Screen→onsite low" --> B2[Calibration: screen bar vs<br/>role profile misaligned]
    B -- "Onsite→offer low" --> B3[Interview loop / hiring-manager<br/>decisiveness; debrief discipline]
    B -- "Offer→accept low" --> B4{Comp competitive?}
    B4 -- "Below band/market" --> B5[Route: total-rewards-comp-analyst<br/>offer band, §3 #2]
    B4 -- "At band" --> B6[Candidate experience / speed /<br/>close process]
    B1 --> C[Cost the vacancy: daily role value × days open]
    B2 --> C
    B3 --> C
    B5 --> C
    B6 --> C
    C --> D[Fix the leaking stage FIRST,<br/>then add volume, §3 #3]
```

## Tree 3 — Pay-equity gap surfaced

```mermaid
flowchart TD
    A[A pay gap is reported] --> B{Raw or controlled?}
    B -- "Raw only" --> B1[STOP: raw gap is mostly composition.<br/>Compute residual after controls, §3 #5]
    B -- "Residual computed" --> C{Residual material<br/>after level/role/tenure/<br/>location/performance?}
    C -- "Negligible" --> C1[Document method + controls.<br/>Monitor on cadence]
    C -- "Material residual" --> D[Signal to investigate —<br/>NOT a legal conclusion]
    D --> E[Route: qualified counsel<br/>privileged review, §2]
    E --> F[Remediation modeled to band,<br/>budgeted, §3 #2 #6]
    F --> G[Re-audit next cycle;<br/>fix the band, not one-offs]
```

## How to read these

- **Always split / control before diagnosing** — the first decision node in Trees 1 and 3 is a STOP that prevents the most common error (acting on an uncosted or uncontrolled number).
- **Fix the leak before adding volume** (Tree 2) — more sourcing into a leaking funnel wastes recruiter capacity (§3 #3).
- **Legal is counsel's** — Tree 3 hard-routes a material residual gap to counsel; the team frames it, counsel determines it (§2).
- Every leaf ends in the §6 Output Contract: owner · date · expected metric movement.
