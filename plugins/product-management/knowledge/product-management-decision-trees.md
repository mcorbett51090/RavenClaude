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

## Decision Tree: Discovery — Is this finding signal or noise?

**When this applies:** The product-discovery-lead or product-metrics-analyst has a data point, user quote, or metric movement and must decide whether it warrants acting on — changing a prioritization decision, pivoting an assumption, or launching an investigation — versus noting it as one data point that may not generalize.

**Last verified:** 2026-06-05 against continuous discovery practice and standard statistical-literacy principles for product teams.

```mermaid
flowchart TD
    START[A data point or finding arrives] --> Q1{Is this qualitative - interview or quantitative - metric}
    Q1 -->|Qualitative - interview or observation| Q2{Does this finding appear in 3 or more independent sessions}
    Q2 -->|No - single instance| WEAK_QUAL[Note it - do not act - add to the question backlog for the next 3 sessions]
    Q2 -->|Yes - pattern across sessions| STRONG_QUAL[Signal - update the opportunity-solution tree - consider assumption impact]
    Q1 -->|Quantitative - metric movement| Q3{Is the sample size above the minimum detectable effect threshold}
    Q3 -->|No - too small| NOISE_QUANT[Insufficient power - do not conclude - extend observation window or increase sample]
    Q3 -->|Yes - adequate power| Q4{Is the movement outside normal week-over-week variance for this metric}
    Q4 -->|No - within variance| SEASONAL[Check for seasonality or external event - note but do not act]
    Q4 -->|Yes - outside variance| Q5{Is there a plausible causal mechanism - a recent ship or external change}
    Q5 -->|No causal candidate| INVESTIGATE[Unexplained signal - investigate before acting - do not assume good or bad]
    Q5 -->|Yes - known cause| SIGNAL_QUANT[Signal with cause - evaluate against success metric and guardrails - decide]
```

**Rationale per leaf:**
- *Single qualitative instance* — one customer's experience is an anecdote; three independent instances are a pattern; the distinction is whether the finding changes a decision or updates a backlog.
- *Multi-session pattern* — three or more independent sessions surfacing the same theme is strong qualitative signal; update the opportunity tree and check whether any open assumptions are affected.
- *Insufficient power* — a metric movement on a small sample is statistically uninterpretable; extending the window or increasing the sample is cheaper than making a wrong decision.
- *Within variance* — normal week-over-week variance is expected in most metrics; acting on noise creates churn in the roadmap without improving outcomes.
- *Unexplained signal outside variance* — an unexplained metric movement is a question, not an answer; investigate before attributing to a feature ship.
- *Signal with cause* — a metric movement with a plausible causal mechanism is interpretable; evaluate against the pre-committed success metric and guardrails.

**Tradeoffs summary:**

| Finding type | Action | Threshold |
|---|---|---|
| Single qualitative | Note and re-test | 3 independent sessions before acting |
| Qualitative pattern | Update OST and assumptions | 3 or more independent sessions |
| Metric - underpowered | Extend observation | Reach MDE threshold first |
| Metric - in variance | Note only | Within normal range |
| Metric - outside variance - causal | Act and evaluate | Against pre-committed metric and guardrail |
| Metric - outside variance - no cause | Investigate | Before acting |

---

## Decision Tree: Strategy — Is this a new opportunity worth pursuing

**When this applies:** A new market opportunity, customer segment, or product area has been proposed for the roadmap. The product-strategist must decide whether to investigate further, add it to the opportunity-solution tree, or decline it so the team can stay focused.

**Last verified:** 2026-06-05 against standard product opportunity assessment practice.

```mermaid
flowchart TD
    START[New opportunity proposed] --> Q1{Is the underlying problem real and validated for a named segment}
    Q1 -->|No - hypothesis only| VALIDATE[Validate first - 3 to 5 customer interviews before roadmap consideration]
    Q1 -->|Yes - evidence exists| Q2{Is the segment your target customer or a close adjacent}
    Q2 -->|No - different segment| OUTSIDE[Outside current strategy - document and defer - revisit at next strategy cycle]
    Q2 -->|Yes| Q3{Is the opportunity size meaningful relative to current focus}
    Q3 -->|No - too small| SMALL[Decline for now - set a revisit threshold - if market grows to X then reconsider]
    Q3 -->|Yes - meaningful| Q4{Can the team address it without sacrificing current priorities}
    Q4 -->|No - requires tradeoff| EXPLICIT_TRADEOFF[Make the tradeoff explicit - what gets deprioritized - get leadership alignment before adding]
    Q4 -->|Yes - additive| ADD_OST[Add to the opportunity-solution tree as a candidate opportunity - score vs. existing items]
```

**Rationale per leaf:**
- *Validate first* — an unvalidated opportunity is a hypothesis; adding it to the roadmap before validation risks investing in a problem that doesn't exist.
- *Outside strategy* — adjacent-segment opportunities are real but dilute focus; the right response is documentation and deferral, not rejection, so they can be revisited at the strategy cycle.
- *Too small* — opportunity size relative to current focus matters; a real but small problem does not warrant a strategy shift; set a threshold for reconsideration.
- *Explicit tradeoff* — if the opportunity requires displacing current priorities, the tradeoff must be made explicit and aligned before the roadmap is changed; invisible tradeoffs are how roadmaps expand without strategy.
- *Add to OST* — a validated, on-strategy, adequately-sized, additive opportunity is a legitimate candidate for the opportunity-solution tree; score it against existing items rather than auto-prioritizing.

**Tradeoffs summary:**

| Opportunity type | Action | Key question |
|---|---|---|
| Unvalidated | Validate with 3 to 5 interviews | Is the problem real? |
| Off-strategy | Defer to strategy cycle | Does it warrant a strategy pivot? |
| Too small | Decline with threshold | When would it become worth addressing? |
| On-strategy - requires tradeoff | Make tradeoff explicit | What gets dropped? |
| On-strategy - additive | Add to OST and score | Does it rank above what is already there? |

---

## Decision Tree: Metrics — Is this metric worth adding to the dashboard

**When this applies:** A stakeholder, analyst, or engineer proposes adding a new metric to the product dashboard or OKR framework. The product-metrics-analyst must decide whether to add it, replace something with it, or decline.

**Last verified:** 2026-06-05 against North Star metric framework and standard product analytics practice.

```mermaid
flowchart TD
    START[New metric proposed for dashboard] --> Q1{Does the metric reflect value the customer actually gets - not just activity}
    Q1 -->|No - vanity or activity metric| DECLINE_VANITY[Decline - it measures output not outcome - explain why to the proposer]
    Q1 -->|Yes - value signal| Q2{Can a team directly move this metric with their work}
    Q2 -->|No - too lagging or aggregate| NORTH_STAR_CANDIDATE[North Star candidate - pair with input metrics that a team can move]
    Q2 -->|Yes - movable| Q3{Is this metric already captured by an existing dashboard metric}
    Q3 -->|Yes - redundant| REDUNDANT[Decline - redundant - point to the existing metric; consolidate if definitions differ]
    Q3 -->|No - new signal| Q4{Does adding it risk creating a metric proliferation problem - more than 5 to 7 key metrics}
    Q4 -->|Yes - already at limit| REPLACE[Replace one existing metric with the new one - or decline until a slot opens]
    Q4 -->|No - room for it| ADD[Add with a guardrail pairing - name the metric it must not harm]
```

**Rationale per leaf:**
- *Vanity/activity metric decline* — metrics that count activity (page views, API calls, feature opens) measure the team being busy, not the customer getting value; the explanation to the proposer is part of the discipline.
- *North Star candidate* — aggregate or lagging metrics that capture real value but cannot be directly moved belong at the top of the hierarchy; they need input-metric decomposition to be actionable.
- *Redundant* — if the metric is already tracked under a different name or definition, the right action is consolidation, not addition; definitional drift between similar metrics is a data-quality risk.
- *Metric proliferation* — a dashboard with 15 metrics is a dashboard nobody reads; the limit of 5–7 key metrics is a forcing function for prioritization.
- *Add with guardrail* — every new metric should be paired with a metric it must not harm; this prevents local optimization that degrades a different part of the system.

**Tradeoffs summary:**

| Metric type | Decision | Action |
|---|---|---|
| Vanity or activity | Decline | Explain the vanity/outcome distinction |
| Aggregate / lagging | North Star candidate | Decompose into input metrics |
| Redundant | Decline | Consolidate definitions |
| New signal - at limit | Replace or decline | Make the explicit tradeoff |
| New signal - room available | Add | Pair with a guardrail metric |
