---
name: pipeline-hygiene-and-routing
description: "Run the GTM machinery: pipeline-hygiene rules, lead routing & scoring with a speed-to-lead SLA and a validated model, territory/quota built bottoms-up from capacity, comp modeled by the behavior it rewards, attribution-model selection as a named lens, and CRM data-quality enforcement at the point of entry — specifying the automation and handing the platform build to salesforce."
---

# Pipeline Hygiene & Routing

## Hygiene is the substrate
Duplicates, missing fields, stuck/aged deals, and dead accounts corrupt every downstream metric. Enforce required fields and dedupe at the **point of entry**, not in a quarterly scrub. Define the hygiene rules (required fields per stage, dedupe/matching, dead-account decay); hand the validation-rule/flow build to `salesforce`.

## Routing and scoring are SLAs
Every lead has a defined owner and a speed-to-lead clock — an unrouted lead is lost revenue. Design the routing model (territory / round-robin / account-based) with an accept/reject + re-route loop. A lead score is a documented model (fit + engagement) with a feedback loop that revisits the weights against actual conversion — not a static point table nobody validates.

## Quota is bottoms-up from capacity
Build quota from ramped-rep capacity × productivity and reconcile it against the top-down board number; surface the over/under-capacity gap. A quota that's the board number ÷ headcount is a wish that misses predictably.

## Comp models behavior, not just math
Every comp/quota/territory design is a behavior change. Name what it rewards *and* what it accidentally rewards — sandbagging, cherry-picking, end-of-quarter dumping — before it ships. Every plan is gamed in exactly the way it pays.

## Attribution is a chosen lens
First/last/linear/W-shaped/data-driven each answer a different question and distort in a known way. Name the model, name what it under/over-credits, and never let one model silently drive budget — triangulate and treat divergence as signal.

## Output
A hygiene/routing design: the data-quality rules (enforced at entry), the routing + speed-to-lead SLA, the validated scoring model, the capacity-derived quota + territory model, the comp behavior analysis, and the attribution lens — with the platform build (`salesforce`), the warehouse mart (`data-platform`), and significance tests (`applied-statistics`) routed out.
