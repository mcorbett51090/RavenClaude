# Marketing Operations Decision Trees

> Mermaid decision trees for the three most common triage paths. Traverse top-to-bottom and pick the smaller-blast-radius leaf — don't keyword-match the symptom to a method. Each tree encodes the team's house opinions (CLAUDE.md §3).

## Tree 1 — Leads up but pipeline flat

```mermaid
flowchart TD
    A[Leads up, pipeline flat] --> B{Data hygiene/tracking<br/>clean?}
    B -- "Dedup/UTM gaps" --> B1[Fix data first; every rate is<br/>suspect, route to martech, §3 #7]
    B -- "Clean" --> C{Which stage<br/>leaks?}
    C -- "Lead→MQL" --> C1[Lead quality / ICP fit /<br/>scoring, not 'more leads', §3 #1 #6]
    C -- "MQL→SQL" --> C2[Scoring or sales hand-off bar, §3 #6]
    C -- "SQL→opp" --> C3[Qualification / discovery depth]
    C -- "Opp→win" --> C4[Sales-side; route to RevOps, §3 #1]
    C1 --> D[Fix the leaking stage FIRST,<br/>then scale volume, §3 #1]
    C2 --> D
    C3 --> D
```

## Tree 2 — Is our CAC sustainable?

```mermaid
flowchart TD
    A[CAC question] --> B{LTV:CAC<br/>computed?}
    B -- "Only cost-per-lead" --> B1[Wrong metric: leads aren't<br/>customers, compute CAC, §3 #3 #4]
    B -- "LTV:CAC known" --> C{Ratio vs<br/>health frame?}
    C -- "Below ~1:1" --> C1[Unsustainable; fix economics<br/>before scaling spend, §3 #3]
    C -- "Healthy blended" --> D{Marginal ROI<br/>by channel?}
    D -- "Saturated channel" --> D1[Marginal ROI gone; reallocate<br/>off the channel, §3 #5]
    D -- "Headroom" --> D2[Scale the channel with<br/>positive marginal ROI, §3 #5]
    C1 --> E[Owner · date · expected CAC movement]
    D1 --> E
    D2 --> E
```

## Tree 3 — Attribution data is a mess

```mermaid
flowchart TD
    A[Attribution data suspect] --> B{Duplicate-lead<br/>rate?}
    B -- "Above a few %" --> B1[Dedup first; funnel + CAC<br/>math is corrupt, §3 #7]
    B -- "Clean" --> C{UTM/tracking<br/>consistent?}
    C -- "Untagged/mixed" --> C1[Enforce UTM taxonomy;<br/>attribution non-computable, §3 #2 #7]
    C -- "Consistent" --> D{Orphaned<br/>touches?}
    D -- "Yes" --> D1[Re-link touches to contacts/opps]
    D -- "No" --> D2[Data trustworthy; release to<br/>funnel + attribution analysis]
    B1 --> E[Owner · date · re-audit before reporting]
    C1 --> E
    D1 --> E
```

## How to read these

- **Decompose before you act** — the first node of each tree is usually a STOP that prevents acting on an aggregate you haven't yet split.
- **Fix the constraint before adding volume** — more input into a leaking process wastes resource.
- Every leaf ends in the §6 Output Contract: owner · date · expected metric movement.
