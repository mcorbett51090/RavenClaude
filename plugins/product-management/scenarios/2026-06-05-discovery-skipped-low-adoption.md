---
scenario_id: 2026-06-05-discovery-skipped-low-adoption
contributed_at: 2026-06-05
plugin: product-management
product: discovery
product_version: "n/a"
scope: likely-general
tags: [discovery, jtbd, assumption-testing, adoption, opportunity-solution-tree]
confidence: medium
reviewed: false
---

## Problem

A team built and shipped a feature straight from an executive's confident description of "what customers want," skipping discovery entirely. It launched to **near-zero adoption**. The post-mortem found the feature solved a problem real customers didn't actually have in the shape described — the team had built the *solution* an exec imagined rather than validating the *job* customers were trying to get done. The expensive part wasn't the wasted build; it was that a single round of customer conversations would have caught it for a fraction of the cost.

## Context

- Segment: consumer subscription app, growth-stage, strong engineering throughput, weak discovery muscle — interviews happened "when there was time," which meant rarely.
- Constraint: the requirement arrived as a fully-formed solution ("add a social feed"), not as a problem or an outcome, so there was nothing to validate against — the assumption that customers *wanted* this had never been written down, let alone tested.
- Classic skipped-discovery shape (CLAUDE.md §2 #2): a discoverable assumption nobody checked.

## Attempts

- Tried: **reframed the failed feature as a problem and ran belated discovery.** Interviewed for the *job* (what were users actually trying to accomplish?) rather than the feature, and found the underlying need was real but mis-shaped — users wanted a *lightweight* way to share progress, not a full social feed. Outcome: salvaged a cheaper, better-fitting V2 from the wreckage, but only after the costly V1 miss.
- Tried: **stood up an opportunity-solution tree** anchored on the actual outcome, mapped the validated opportunities (unmet needs from the interviews) beneath it, and only *then* generated candidate solutions — so the next bet started from evidence, not an exec's hunch. Outcome: the riskiest assumption of the V2 (that users would share at all) was named and tested with a cheap fake-door before any build.
- Tried: **made a weekly customer touchpoint infrastructure, not a phase.** Adopted continuous discovery (regular interviews + assumption testing) so the team stopped treating discovery as a one-time gate that gets skipped under deadline pressure. Outcome: subsequent features carried a validated problem and a tested riskiest-assumption before entering build.

## Resolution

Low adoption was the symptom; **skipped discovery was the cause.** Building an exec's imagined solution without validating the customer's job is a discoverable miss — and discovery is continuous infrastructure, not a phase to skip when the deadline is tight. The fix: reframe requirements as problems/outcomes, run weekly customer touchpoints, build an opportunity-solution tree from validated needs, and test the riskiest assumption cheaply (fake-door / prototype / concierge) before committing engineering.

**Action for the next PM hitting this pattern:** when a requirement arrives as a *solution*, convert it to a problem and validate the job before building. Traverse the "Should we build this?" tree in [`../knowledge/product-management-decision-trees.md`](../knowledge/product-management-decision-trees.md) — an unvalidated problem routes to discovery first, and an untested riskiest assumption routes to a cheap test, *before* the build leaf. Interview for the job, not the feature (Jobs-to-be-Done).

**Sources (retrieved 2026-06-05):**
- Teresa Torres — *Opportunity Solution Trees* (outcome → opportunity → solution → experiment; continuous discovery): https://www.producttalk.org/opportunity-solution-trees/
- Product School — *Opportunity Solution Trees for Enhanced Product Discovery* (Torres, introduced 2016; four-step framework): https://productschool.com/blog/product-fundamentals/opportunity-solution-tree

Adoption figures here are illustrative `[ESTIMATE]`; the *application* of JTBD / OST to a specific product is `[verify-at-use]` and calibrated to the team's customer base (CLAUDE.md §2; claim-grounding).
