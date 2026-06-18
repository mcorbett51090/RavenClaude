---
scenario_id: 2026-06-18-vanity-metric-board-deck
contributed_at: 2026-06-18
plugin: developer-relations
product: strategy-metrics
product_version: "n/a"
scope: likely-general
tags: [vanity-metrics, activation, funnel, board-reporting, stars]
confidence: medium
reviewed: false
---

## Problem

A DevRel lead's quarterly board slide led with "25,000 GitHub stars (+40% QoQ)" and "1.2M impressions."
The board's question back was blunt: "what did that get us?" — and the lead had no answer tied to the
business. Leadership was a week from cutting the DevRel budget because the program couldn't connect its
numbers to any outcome. The lead asked how to report the program so it survived the review.

## Context

- Product: a developer API; ~18 months of DevRel investment.
- Audience: backend developers integrating the API; mostly *aware* (the stars), few activating.
- Funnel state: strong awareness, **leaking activation** — sign-up → first successful API call was the
  unmeasured gap.
- Constraint: no activation instrumentation existed; the only numbers on hand were the vanity ones.

## Attempts

- Tried: the **vanity tell** ([`../knowledge/devrel-funnel-and-metrics.md`](../knowledge/devrel-funnel-and-metrics.md)) —
  asked of each headline metric, "can it go *down*, and if it did would we change something?" Stars and
  impressions failed the test (they only ratchet up, force no decision). That diagnosed the deck:
  every headline was applause, not outcome.
- Tried: stood up the **activation headline** the program never had — instrumented time-to-first-success
  and the sign-up→first-call conversion ([`../best-practices/measure-developer-activation-not-vanity-metrics.md`](../best-practices/measure-developer-activation-not-vanity-metrics.md)).
  First read was uncomfortable: activation rate ≈ 12% `[ESTIMATE]`, median TTFS ≈ 40 minutes across 9
  steps. That uncomfortable number was the point — it could move, and it tied to revenue (activated
  devs become paying usage).
- Tried (the move that worked): **re-anchored the deck on the funnel.** Headline became "activation
  rate 12% → target 25%, TTFS 40min → target <10min"; stars/impressions were demoted to a context line
  below the fold. The narrative shifted from "look how popular we are" to "here's the leak we found and
  the plan to fix it," which is a story a board funds.

## Resolution

The deck's vanity headline was the symptom; the real defect was that the program had **never measured
activation**, so it couldn't tie effort to outcome. Re-anchoring on the awareness→activation→advocacy
funnel — activation rate + TTFS as the headline, vanity demoted to context — gave the board a metric
that can get worse and a plan to make it better. The budget survived; the next quarter's work was the
TTFS audit, not more top-of-funnel reach.

**Action for the next advocate hitting this pattern:** never let a board deck lead with stars /
followers / impressions. Run the vanity tell on every headline; if a metric can't go down, it isn't
measuring. Stand up the activation headline (TTFS + activation rate) even if the first number is ugly —
an ugly number that ties to outcome beats a pretty one that doesn't. Demote vanity to context, don't
delete it (it's a weak awareness signal). Then route the fix work to a
[`../templates/developer-onboarding-audit.md`](../templates/developer-onboarding-audit.md).

**Note:** all figures are illustrative `[ESTIMATE]` ranges — validate against the engagement's actual
instrumentation before a deliverable.
