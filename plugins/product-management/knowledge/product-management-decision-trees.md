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

## Decision Tree: Which prioritization method?

The framework should fit the decision; the wrong one launders a bad ranking with false rigor.

```mermaid
graph TD
  A[Need to prioritize] --> B{Is time-sensitivity / cost of waiting the dominant factor?}
  B -- Yes --> C[Cost-of-delay / WSJF - rank by value lost per week of delay]
  B -- No --> D{Is it about which features satisfy vs delight customers?}
  D -- Yes --> E[Kano - basic vs performance vs delighter]
  D -- No --> F{Comparing many items on value-for-effort?}
  F -- Yes --> G[RICE - reach x impact x confidence / effort]
  F -- No --> H{One big strategic bet, not a backlog?}
  H -- Yes --> I[Skip the spreadsheet - argue it on strategy + opportunity size]
  H -- No --> G
```

_The point is making reach/impact/confidence/effort explicit and arguable, not the decimal places._

## Decision Tree: Ship more, iterate, or kill it?

After a bet ships, the outcome decides — not sunk cost or who championed it.

```mermaid
graph TD
  A[Feature has shipped + run long enough] --> B{Did the target outcome metric move vs baseline?}
  B -- Yes --> C{Guardrails OK no harm elsewhere?}
  C -- No --> D[Not a win - fix the harm or roll back]
  C -- Yes --> E[Double down - invest in the winning bet]
  B -- No --> F{Is the mechanism sound but the execution weak?}
  F -- Yes --> G[Iterate - one more cheap cycle, pre-committed]
  F -- No --> H{Anyone actually using / needing it?}
  H -- No --> I[Kill it - remove the maintenance + complexity tax]
  H -- Yes, a few --> J[Maintain minimally; don't keep investing]
```

_A feature that changed nothing is a learning to act on, not a success to defend._

## Decision Tree: Is this a product call or a project call?

Keep the what/why here; route how/when to project-management. The litmus is the question being asked.

```mermaid
graph TD
  A[A decision lands on the table] --> B{Is it about WHAT to build or WHY?}
  B -- Yes --> C{Problem validation / opportunity?}
  C -- Yes --> D[product-discovery-lead]
  C -- No --> E{Positioning / roadmap of bets?}
  E -- Yes --> F[product-strategist]
  E -- No --> G[product-metrics-analyst - the outcome metric]
  B -- No, it's HOW or WHEN --> H[Route to project-management: schedule, scope/change, RAID]
  B -- It's whether a result is statistically real --> I[Route to applied-statistics]
```

_Conflating what/why with how/when turns the roadmap into a dated Gantt and loses the outcome context._

## Capability map (dated — verify at build)

| Concept | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| Continuous discovery (Torres) | established | Weekly touchpoints, OST |
| Jobs-to-be-Done | established | Interview the 'job' |
| RICE / cost-of-delay | established | Transparent prioritization |
| North Star framework | established | Value + input metrics |
| Opportunity-solution tree | established | Outcome->opp->solution->experiment |
| Outcomes over outputs | mainstream | Judge the metric, not the ship |
