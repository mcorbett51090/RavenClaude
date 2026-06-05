---
scenario_id: 2026-06-05-build-vs-buy-vs-partner-capability
contributed_at: 2026-06-05
plugin: product-management
product: strategy
product_version: "n/a"
scope: likely-general
tags: [build-buy-partner, strategy, differentiation, opportunity-cost, capability]
confidence: medium
reviewed: false
---

## Problem

An engineering team proposed building a notifications/messaging infrastructure capability in-house because "we can build a better one." The decision had been framed entirely as feasibility and cost — *can* we build it, and how long — with no product-strategy input on whether *owning* the capability gave any durable advantage. The risk cut both ways: building a commodity would sink months of engineering with a measurable opportunity cost against the features that actually differentiate, while a careless partner choice in a core user flow could let a competitor match the capability overnight by signing the same vendor.

## Context

- Segment: B2B SaaS platform, post-PMF, scarce senior engineering capacity, an active roadmap of differentiated work competing for that capacity.
- Constraint: the capability in question (transactional messaging delivery) was *not* user-visible differentiation — customers would never choose the product *because* of who delivered its emails — but the team's instinct to build was strong and unexamined. Mature vendors covered the need at a fraction of the build cost.
- Classic build-trap shape (CLAUDE.md §2 #1): optimizing build quality on something that doesn't differentiate.

## Attempts

- Tried: **ran the differentiation test before the feasibility analysis.** Asked the load-bearing question — *would a customer ever choose us over a competitor specifically because of this capability?* — and answered honestly: no. Classified it core/context/commodity → **commodity**. Outcome: reframed the decision from "how do we build it well?" to "why are we building a commodity at all?"
- Tried: **sized the opportunity cost rather than asserting it.** Used a bottoms-up estimate of what the freed senior-engineering capacity could build instead (a differentiated roadmap item), so "engineering is too valuable for this" became a number, not a slogan. Outcome: the buy case became quantitatively obvious — the build's true cost was the differentiated feature it displaced.
- Tried: **chose BUY with an exit check, not PARTNER, for the commodity.** A mature vendor covered ≥80% of the requirement with sane unit economics at current and 3× volume; checked data portability and exit cost before committing. Reserved *partner* for capabilities where a third party brought domain expertise and mutual value (it didn't here). Outcome: bought the commodity, kept an exit path, redirected the engineering to the differentiated work.

## Resolution

The decision was strategic, not technical: **"can we build it?" is the wrong question — "does owning it give us a durable advantage over buying or partnering?" is the right one.** A commodity capability with a mature vendor market is a buy; building it burns engineering with a real opportunity cost against differentiated features. The fix was the core/context/commodity filter, an honestly-applied differentiation test, a *sized* opportunity cost, and a buy with an exit check — reserving build for true differentiators and partner for mutual-value access.

**Action for the next PM hitting this pattern:** when an engineering team frames a capability as build-feasibility, pull it back to strategy first. Traverse [`../knowledge/build-vs-buy-vs-partner-decision-tree.md`](../knowledge/build-vs-buy-vs-partner-decision-tree.md): pre-PMF → fastest path to learning; core differentiator → build; context/commodity with a ≥80%-fit vendor → buy; domain expertise + mutual value → partner. Size the opportunity cost with [`../scripts/pm_calc.py`](../scripts/pm_calc.py) `opportunity`, and put the call on the roadmap as a bet with explicit confidence.

**Sources (retrieved 2026-06-05):**
- ideaplan — *Build vs Buy vs Partner: The Product Leader's Decision* (build for differentiation / buy for proven capability / partner for access): https://www.ideaplan.io/compare/build-vs-buy-vs-partner
- Clear Function — *Build vs Buy vs Partner: A Decision Framework for Platform Teams* (core/context/commodity 10-second filter; ≥80%-fit, 3×-volume, exit-cost heuristics): https://www.clearfunction.com/insights/build-vs-buy-vs-partner-decision-framework

The core-vs-context lens is attributed to Geoffrey Moore `[unverified — training-knowledge attribution]`; any cost/volume figure is illustrative `[ESTIMATE]` and the differentiation call is `[verify-at-use]` for the specific capability (CLAUDE.md §2; claim-grounding).
