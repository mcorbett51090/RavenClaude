# TPM engagement decision trees

Traverse these top-to-bottom before picking a move. They keep this team from
absorbing work that belongs to a PM or EM, and from escalating (or launching) on
mood instead of criteria.

## 1. Is this a program (TPM), a project (PM), or people (EM)?

```mermaid
flowchart TD
    A[A request lands] --> B{Spans >=2 teams<br/>with cross-team dependencies?}
    B -- No --> C{Mostly about people:<br/>hiring, performance, headcount?}
    C -- Yes --> EM[Route to engineering-management]
    C -- No --> PM[Route to project-management<br/>single project / backlog / plan]
    B -- Yes --> D{Is there one outcome<br/>the teams jointly own?}
    D -- No --> E[Not a program yet —<br/>clarify the outcome first<br/>or it's parallel projects]
    D -- Yes --> F{Is the hard part the<br/>seams/handoffs between teams?}
    F -- No --> PM
    F -- Yes --> TPM[This is a program —<br/>charter it, own the seams]
```

**Rule:** the TPM earns the work only when the difficulty is the *cross-team
coordination*. A big single-team effort is still a project. A pile of unrelated
team work sharing a deadline is not a program until someone names the joint
outcome.

## 2. Escalate or not?

```mermaid
flowchart TD
    A[A blocker / slip appears] --> B{Is it on the<br/>critical path?}
    B -- No --> C{Will its slack run out<br/>before next status?}
    C -- No --> TRACK[Track in RAID — no escalation]
    C -- Yes --> WATCH[Flag in status as a watch item<br/>with the date slack expires]
    B -- Yes --> D{Can the owning team<br/>resolve it themselves<br/>before it moves the date?}
    D -- Yes --> SUPPORT[Offer unblock help,<br/>set a check-in date]
    D -- No --> E{Does resolving it need<br/>a decision/resource above<br/>the team's authority?}
    E -- Yes --> ESC[Escalate NOW —<br/>frame as a specific decision<br/>request to a named owner]
    E -- No --> SUPPORT
```

**Rule:** escalation is framed as a *decision request* ("I need X to choose
between A and B by Friday or we slip two weeks"), never as a complaint. Early is
leadership; late is a postmortem.

## 3. Go / no-go

```mermaid
flowchart TD
    A[Launch approaching] --> B{Are go/no-go criteria<br/>written and pre-agreed?}
    B -- No --> STOP[Not ready to decide —<br/>define criteria first,<br/>do not invent them in the room]
    B -- Yes --> C{All criteria GO?}
    C -- Yes --> GO[GO — record decision + owner,<br/>start staged rollout]
    C -- No --> D{Are the unmet criteria<br/>waivable with accepted risk?}
    D -- No --> NOGO[NO-GO — record blockers,<br/>set the re-review date]
    D -- Yes --> E{Has a named owner<br/>accepted the risk in writing?}
    E -- No --> NOGO
    E -- Yes --> GOW[Conditional GO —<br/>record the waiver + risk acceptance]
```

**Rule:** a launch decision is only as good as its written criteria. No criteria →
no decision, only an accident waiting for a retro. Every waiver has an owner who
accepted the risk on the record.
