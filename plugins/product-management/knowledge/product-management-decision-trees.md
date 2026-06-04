# Product Management — Decision Trees

_Decision trees + a dated capability map. Capability rows are `[verify-at-build]` — re-check against the vendor before quoting. Last reviewed: 2026-06-04._

Traverse before committing to build or ranking a backlog.

## Decision Tree: Should we build this?

Validate the problem and the riskiest assumption before committing engineering.

```mermaid
graph TD
  A[A feature idea] --> B{Is the problem validated real/frequent/painful for a segment?}
  B -- No --> C[Discovery first: interviews, problem validation]
  B -- Yes --> D{Tied to a strategic outcome / opportunity?}
  D -- No --> E[Park it - it's an output, not an outcome]
  D -- Yes --> F{Riskiest assumption tested cheaply?}
  F -- No --> G[Test it first: prototype/fake-door/concierge]
  F -- Yes, holds --> H{Prioritized above alternatives by evidence?}
  H -- No --> I[Score it RICE/cost-of-delay vs the backlog]
  H -- Yes --> J[Build - with the outcome metric + guardrails defined]
```

_Delivery scheduling of an approved build routes to project-management._

## Decision Tree: Is this metric worth tracking as a goal?

Prefer actionable, movable metrics that capture real value; drop vanity.

```mermaid
graph TD
  A[A candidate metric] --> B{Does it reflect value the customer actually gets?}
  B -- No --> C[Vanity / output - don't make it a goal]
  B -- Yes --> D{Can a team move it directly?}
  D -- No, lagging/aggregate --> E[Use as North Star; decompose into movable INPUT metrics]
  D -- Yes --> F{Rate/cohort/retention vs cumulative total?}
  F -- Cumulative total --> G[Reframe as a rate/cohort - totals flatter]
  F -- Rate/cohort --> H[Good input metric - pair with a guardrail]
```


## Capability map (dated — verify at build)

| Concept | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| Continuous discovery (Torres) | established | Weekly touchpoints, OST |
| Jobs-to-be-Done | established | Interview the 'job' |
| RICE / cost-of-delay | established | Transparent prioritization |
| North Star framework | established | Value + input metrics |
| Opportunity-solution tree | established | Outcome->opp->solution->experiment |
| Outcomes over outputs | mainstream | Judge the metric, not the ship |
