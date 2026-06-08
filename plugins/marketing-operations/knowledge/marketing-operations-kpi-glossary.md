# Marketing Operations KPI Glossary

> The team's canonical metric definitions. Every metric carries a **definition**, a **window**, and a **baseline** before it ships (CLAUDE.md §3 #1). Benchmark ranges are `[unverified — training knowledge]` unless a dated source is attached — confirm against a current source before using in a deliverable (§3 #8).

## Funnel & conversion

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Stage conversion** | Records advancing stage N→N+1 ÷ entering N | Cohort | The leaking stage localizes the bottleneck (§3 #1). |
| **MQL→SQL rate** | SQLs accepted ÷ MQLs passed | Rolling, by source | A low rate is a scoring or hand-off problem, not a volume problem (§3 #6). |
| **Stage dwell** | Median days a record sits in a stage | Per stage | A long dwell is a routing/follow-up problem (§3 #1). |
| **Lead score validity** | Do score bands predict downstream conversion? | Cohort | A score that doesn't predict is noise (§3 #6). |

## Economics & attribution

| Metric | Definition | Window | Note |
|---|---|---|---|
| **CAC** | Fully-loaded acquisition cost ÷ customers acquired | Rolling | Include program + people + tooling, not just media. |
| **LTV** | Gross-margin lifetime value per customer | Cohort | Use gross-margin LTV, not revenue LTV. |
| **LTV:CAC** | LTV ÷ CAC | Rolling | A common health frame ≈ 3:1 [unverified] (§3 #3). |
| **CAC-payback** | CAC ÷ monthly gross-margin contribution | Months | The cash-recovery horizon (§3 #3). |
| **Channel ROI** | (Contribution − cost) ÷ cost, under a NAMED model | Rolling | Attribution model changes the ranking (§3 #2). |
| **Marginal ROI** | Return on the next incremental dollar | Rolling | Read this, not the average, at scale (§3 #5). |

## Contribution

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Sourced pipeline** | Pipeline where marketing created the first touch | Per period | The marketing scorecard headline (§3 #4). |
| **Influenced pipeline** | Pipeline with any marketing touch in the path | Per period | Depends on the attribution model (§3 #2). |

## The rule

A metric without a **window** and a **baseline** is not a finding — it's a number (§3 #1). A benchmark without a **source URL + retrieval date** is `[unverified — training knowledge]` (§3 #8).
