# Accessibility Engineering Decision Trees

> Mermaid decision trees for the three most common triage paths. Traverse top-to-bottom and pick the smaller-blast-radius leaf — don't keyword-match the symptom to a method. Each tree encodes the team's house opinions (CLAUDE.md §3).

## Tree 1 — Where do we start on WCAG conformance?

```mermaid
flowchart TD
    A[Need to be accessible] --> B{Conformance target<br/>named?}
    B -- "No target/scope" --> B1[Pick WCAG version + level<br/>+ page set FIRST, §3 #1]
    B -- "Target set" --> C{Evidence type?}
    C -- "Automated scan only" --> C1[Floor only — add manual +<br/>AT testing, §3 #2]
    C -- "Manual + AT done" --> D{Any Level-A<br/>blocker?}
    D -- "Yes" --> D1[Not shippable — blockers<br/>lead remediation, §3 #2 #7]
    D -- "No" --> D2[Weighted score vs target;<br/>rank remaining, §3 #1]
    B1 --> E[Conformance read + ranked plan ·<br/>route liability to counsel, §2 #6]
    C1 --> E
    D1 --> E
    D2 --> E
```

## Tree 2 — Too many fixes, not enough time

```mermaid
flowchart TD
    A[Long issue list] --> B{Level-A<br/>blocker?}
    B -- "Yes" --> B1[Fix first — fails the page<br/>at every level, §3 #2]
    B -- "No" --> C{High user-impact?}
    C -- "Yes, low effort" --> C1[Quick win — do next, §3 #7]
    C -- "Yes, high effort" --> C2{Recurring<br/>pattern?}
    C2 -- "Yes" --> C3[Fix in design system once,<br/>route to inclusive-design, §3 #7]
    C2 -- "No" --> C4[Schedule as structural work]
    C -- "Low impact" --> C5[Defer / batch]
    B1 --> D[Sequenced plan · owners · dates ·<br/>expected impact, §3 #7]
    C1 --> D
    C3 --> D
    C4 --> D
```

## Tree 3 — Custom widget broken with a screen reader

```mermaid
flowchart TD
    A[Widget unusable in AT] --> B{Native element<br/>available?}
    B -- "Yes, not used" --> B1[Replace with native — gets role/<br/>state/keyboard free, §3 #4]
    B -- "No native fits" --> C{Name/Role/Value<br/>correct?}
    C -- "Missing/wrong" --> C1[Fix ARIA role/state/value<br/>SC 4.1.2, §3 #4]
    C -- "Correct" --> D{Keyboard<br/>operable?}
    D -- "Trap / no focus" --> D1[Fix focus management +<br/>keyboard handlers, §3 #3]
    D -- "Operable" --> D2{Dynamic updates<br/>announced?}
    D2 -- "No" --> D3[Add aria-live region]
    D2 -- "Yes" --> D4[Re-test across AT, §3 #2]
    B1 --> E[Fix in shared component,<br/>not per-page, §3 #7]
    C1 --> E
    D1 --> E
    D3 --> E
```

## How to read these

- **Decompose before you act** — the first node of each tree is usually a STOP that prevents acting on an aggregate you haven't yet split.
- **Fix the constraint before adding volume** — more input into a leaking process wastes resource.
- Every leaf ends in the §6 Output Contract: owner · date · expected metric movement.
