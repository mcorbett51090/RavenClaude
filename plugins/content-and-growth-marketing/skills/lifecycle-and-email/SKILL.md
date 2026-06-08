---
name: lifecycle-and-email
description: "Engineer email and lifecycle marketing as a system: map the lifecycle stages, build segmentation and behavior-triggered nurture flows, protect deliverability (SPF/DKIM/DMARC, list hygiene, sender reputation), and instrument the demand-gen funnel with the metrics that matter — conversion and engaged-list health, never vanity opens."
---

# Lifecycle & Email

## Map the lifecycle, then the flows
Lay out the stages (acquisition → activation → nurture → conversion → retention → reactivation) and the job of each. Design triggered flows against them: welcome, onboarding, nurture, abandonment/cart, re-engagement/win-back — each with a trigger, entry/exit criteria, branching, and suppression.

## Segment or don't send
Relevance is the whole game. A segmented, triggered message beats a generic blast on every metric *and* raises engagement, which protects deliverability. The unsegmented batch-and-blast is the default failure mode.

## Deliverability is the foundation
An email in spam converts at zero. Authentication (SPF/DKIM/DMARC), list hygiene with a sunset policy, and sender reputation come before copy. Sunset the unengaged before they tank your reputation — a smaller engaged list out-delivers a big stale one.

## The welcome flow is the highest-ROI automation
New subscribers are at peak intent; an automated welcome/nurture beats waiting for the next newsletter. If you can't name the trigger and the exit, it's a broadcast, not a flow.

## Measure what matters, not opens
Open rate is a privacy-inflated proxy. Anchor on inbox placement, clicks, conversion, engaged-list health, and revenue per recipient. Diagnose the funnel stage-by-stage to find the leak before automating a fix.

## Output
A lifecycle-flow design per the [`lifecycle-flow-spec`](../../templates/lifecycle-flow-spec.md) template, a deliverability fix plan, or a funnel-leak diagnosis. Route content slots to `content-strategist`, A/B variants to `experimentation-growth-engineering`, and attribution/warehouse to `data-platform`.
