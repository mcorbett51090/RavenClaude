# Behavioral Health Practice Decision Trees

> Mermaid decision trees for the three most common triage paths. Traverse top-to-bottom and pick the smaller-blast-radius leaf — don't keyword-match the symptom to a method. Each tree encodes the team's house opinions (CLAUDE.md §3).

## Tree 1 — No-show rate is killing us

```mermaid
flowchart TD
    A[High no-show / late-cancel] --> B{Quantified as a flow<br/>lost slots + revenue?}
    B -- "Just a rate" --> B1[Quantify lost slots and revenue<br/>first, §3 #1]
    B -- "Quantified" --> C{Reminder program<br/>in place?}
    C -- "None" --> C1[Stand up reminders;<br/>model the recovery lift, §3 #1]
    C -- "Yes" --> D{Empty slots<br/>backfilled?}
    D -- "No backfill" --> D1[Waitlist + telehealth fill;<br/>route telehealth rules out, §3 #1 #7]
    D -- "Backfilled" --> D2[Residual is access-time<br/>at first visit, route to access, §3 #2]
    C1 --> E[Owner · date · expected no-show + revenue movement]
    D1 --> E
    B1 --> E
```

## Tree 2 — Referrals don't convert

```mermaid
flowchart TD
    A[Referrals don't become patients] --> B{Access time<br/>measured?}
    B -- "Not measured" --> B1[Measure intake-to-first-appointment<br/>by source FIRST, §3 #2]
    B -- "Measured + long" --> C{Where's the<br/>delay?}
    C -- "Scheduling capacity" --> C1[Caseload/staffing gap,<br/>route to caseload, §3 #4]
    C -- "Intake paperwork" --> C2[Streamline intake flow,<br/>§3 #2]
    C -- "No-show at first visit" --> C3[First-visit reminder/flow,<br/>route to no-show, §3 #1]
    B -- "Measured + short" --> D[Not an access problem —<br/>check fit/marketing source quality]
    C1 --> E[Fix access BEFORE adding<br/>marketing spend, §3 #2]
    C2 --> E
    C3 --> E
```

## Tree 3 — Margin is thin despite full schedule

```mermaid
flowchart TD
    A[Thin margin, full schedule] --> B{Read margin<br/>by payer?}
    B -- "Blended only" --> B1[Break out per-payer<br/>reimbursement net of cost, §3 #5]
    B -- "By payer" --> C{Any payer below<br/>variable cost?}
    C -- "Yes" --> C1{Parity gap?}
    C1 -- "Possible" --> C2[Flag parity, route the<br/>determination to counsel, §3 #5 #8]
    C1 -- "No" --> C3[Mix-shift or renegotiate;<br/>capacity caveats, §3 #5]
    C -- "All above cost" --> D{Documentation<br/>denials?}
    D -- "Late/incomplete notes" --> D1[Documentation-as-billing fix,<br/>route to compliance, §3 #3]
    D -- "Clean" --> D2[Utilization/caseload gap,<br/>route to caseload, §3 #4]
    B1 --> E[Owner · date · expected margin movement]
    C2 --> E
    C3 --> E
    D1 --> E
```

## How to read these

- **Decompose before you act** — the first node of each tree is usually a STOP that prevents acting on an aggregate you haven't yet split.
- **Fix the constraint before adding volume** — more input into a leaking process wastes resource.
- Every leaf ends in the §6 Output Contract: owner · date · expected metric movement.
