# Platform Engineering (IDP) Decision Trees

> Mermaid decision trees for the three most common triage paths. Traverse top-to-bottom and pick the smaller-blast-radius leaf — don't keyword-match the symptom to a method. Each tree encodes the team's house opinions (CLAUDE.md §3).

## Tree 1 — Nobody uses the platform

```mermaid
flowchart TD
    A[Low adoption] --> B{Is the golden path<br/>the EASY path?}
    B -- "Harder than workaround" --> B1[Friction problem: pave the road,<br/>not mandate it, §3 #2]
    B -- "Easy path" --> C{Measured with DORA<br/>or just sentiment?}
    C -- "Sentiment only" --> C1[Measure: four DORA keys +<br/>adoption ratio, §3 #3 #7]
    C -- "Measured" --> D{Reliable enough<br/>to depend on?}
    D -- "Flaky paved action" --> D1[Reliability problem: SLOs +<br/>error budget, §3 #6]
    D -- "Reliable" --> D2[Awareness/onboarding gap;<br/>product marketing the path, §3 #1]
    B1 --> E[Owner · date · expected adoption lift]
    C1 --> E
    D1 --> E
    D2 --> E
```

## Tree 2 — Pave or mandate?

```mermaid
flowchart TD
    A[Want a standard adopted] --> B{Can the compliant way<br/>be the EASIEST way?}
    B -- "Yes" --> B1[Pave it: self-service action<br/>+ guardrail, §3 #2 #4]
    B -- "No, genuinely harder" --> C{Is the cost of<br/>non-compliance high?}
    C -- "Low" --> C1[Leave optional; revisit when<br/>you can pave it, §3 #2]
    C -- "High security/legal" --> C2[Mandate WITH the easiest<br/>possible paved path, route<br/>determination to authority, §2]
    B1 --> D{Removes meaningful<br/>toil?}
    D -- "Yes, quantified" --> D1[Build it; toil ROI clears<br/>the bar, §3 #4]
    D -- "Rare edge case" --> D2[Defer; below the ROI bar]
    D1 --> E[Owner · date · expected adoption + toil saved]
    C2 --> E
```

## Tree 3 — Platform feels flaky

```mermaid
flowchart TD
    A[Platform unreliable] --> B{Are there<br/>platform SLOs?}
    B -- "No SLOs" --> B1[Define SLIs first: paved-path<br/>success, provisioning, pipeline, §3 #6]
    B -- "SLOs exist" --> C{Which SLI<br/>is breaching?}
    C -- "Paved-path success" --> C1[Path design fault, route to<br/>golden-path-architect, §3 #2]
    C -- "Provisioning latency" --> C2[Provisioning backend / quota;<br/>self-service promise at risk, §3 #4]
    C -- "Pipeline reliability" --> C3[CI/CD reliability; feeds MTTR<br/>+ change-fail, §3 #3]
    C1 --> D{Error budget<br/>spent?}
    C2 --> D
    C3 --> D
    D -- "Spent" --> D1[Freeze platform features;<br/>reliability work, §3 #6]
    D -- "Budget left" --> D2[Fix within budget;<br/>owner · date]
    B1 --> D2
```

## How to read these

- **Decompose before you act** — the first node of each tree is usually a STOP that prevents acting on an aggregate you haven't yet split.
- **Fix the constraint before adding volume** — more input into a leaking process wastes resource.
- Every leaf ends in the §6 Output Contract: owner · date · expected metric movement.
