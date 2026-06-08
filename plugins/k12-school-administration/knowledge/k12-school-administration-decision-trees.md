# K-12 School Administration Decision Trees

> Mermaid decision trees for the three most common triage paths. Traverse top-to-bottom and pick the smaller-blast-radius leaf — don't keyword-match the symptom to a method. Each tree encodes the team's house opinions (CLAUDE.md §3).

## Tree 1 — Enrollment down, budget tight

```mermaid
flowchart TD
    A[Enrollment down, budget tight] --> B{Intake or<br/>retention?}
    B -- "Mid-year attrition" --> B1[Retention flow problem;<br/>fix re-enrollment, §3 #1]
    B -- "Intake low" --> B2[Pipeline / marketing<br/>+ program fit, §3 #1]
    B1 --> C{ADA also<br/>soft?}
    B2 --> C
    C -- "ADA low" --> C1[Attendance recovery —<br/>dual funding + outcome lever, §3 #2 #5]
    C -- "ADA fine" --> D[Fit staffing to the lower<br/>funded envelope, §3 #3]
    C1 --> E[Owner · date · expected funding recovery]
    D --> E
```

## Tree 2 — Can we afford this staffing?

```mermaid
flowchart TD
    A[Proposed staffing ratio] --> B{Within the<br/>budget envelope?}
    B -- "Over budget" --> C{Funded enrollment<br/>realistic?}
    C -- "Enrollment soft" --> C1[Re-base on funded enrollment<br/>first, §3 #1]
    C -- "Enrollment solid" --> C2[Re-allocate per-pupil to<br/>highest-need, §3 #4]
    B -- "Within budget" --> D{Retention<br/>cost factored?}
    D -- "High turnover" --> D1[Turnover cost erodes the room;<br/>retention lever, §3 #7]
    D -- "Stable" --> D2[Ratio fits — commit]
    C1 --> E[Owner · date · expected variance]
    C2 --> E
    D1 --> E
    D2 --> E
```

## Tree 3 — Scores flat / chronic absence rising

```mermaid
flowchart TD
    A[Scores flat or absence up] --> B{Read outcomes<br/>segmented}
    B -- "Average flat, subgroup falling" --> B1[Target intervention to the<br/>falling subgroup, §3 #6]
    B -- "Broadly flat" --> C{Attendance<br/>signal?}
    C -- "Chronic absence high" --> C1[Attendance recovery FIRST —<br/>it predicts achievement, §3 #2 #5]
    C -- "Attendance fine" --> C2[Instructional / resourcing;<br/>allocate per-pupil to need, §3 #4]
    B1 --> D{Special-ed<br/>involved?}
    C1 --> D
    C2 --> D
    D -- "Yes" --> D1[Frame and route IEP/special-ed<br/>to counsel, §2]
    D -- "No" --> D2[Owner · date · expected outcome lift]
    D1 --> D2
```

## How to read these

- **Decompose before you act** — the first node of each tree is usually a STOP that prevents acting on an aggregate you haven't yet split.
- **Fix the constraint before adding volume** — more input into a leaking process wastes resource.
- Every leaf ends in the §6 Output Contract: owner · date · expected metric movement.
