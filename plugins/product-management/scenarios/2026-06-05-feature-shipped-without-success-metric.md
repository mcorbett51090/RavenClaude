---
scenario_id: 2026-06-05-feature-shipped-without-success-metric
contributed_at: 2026-06-05
plugin: product-management
product: metrics
product_version: "n/a"
scope: likely-general
tags: [success-metric, outcomes, north-star, ship-to-learn, guardrail]
confidence: medium
reviewed: false
---

## Problem

A team shipped a heavily-requested feature, celebrated the launch, and then could not answer the only question that mattered three weeks later: **did it work?** No success metric had been defined before the build, so the post-launch review devolved into anecdote ("sales loves it", "a few support tickets") with no way to tell whether the feature moved any behavior. Worse, with no metric named up front, nobody could decide whether to invest more, iterate, or kill it — so it sat in a permanent maintenance-tax limbo, neither doubled-down-on nor removed.

## Context

- Segment: B2B SaaS, mid-stage, product analytics instrumented but not wired to any per-feature outcome; PRDs described *what* to build, never *what behavior change would prove it worked*.
- Constraint: the feature was already live, so the team was reconstructing intent after the fact — the harder, lossier path. The "success" claim rested on a vanity signal (feature opens) that measured activity, not value.
- Classic feature-factory shape (CLAUDE.md §2 #1, #4): outputs shipped, outcome forgotten.

## Attempts

- Tried: **reconstructed the success metric retroactively and instrumented it.** Named the behavior the feature was *supposed* to change (a target-segment activation step), defined the metric as a rate/cohort (not a cumulative total that flatters), paired it with a **guardrail** it must not harm (overall task-completion time), and set a pre-committed read date. Outcome: turned an un-answerable "did it work?" into a measurable one — but a quarter late and with weaker baseline data than a pre-launch metric would have had.
- Tried: **made "success metric before spec" a PRD gate.** Adopted the rule that no PRD enters build without a named outcome metric, its baseline, the expected movement, and a guardrail (the `write-the-success-metric-before-writing-the-spec` best practice). Outcome: the next three features each shipped with a metric defined *before* the build, so the post-launch review was a 10-minute read against a pre-committed number instead of an argument.
- Tried: **ran the ship/iterate/kill decision against the now-instrumented metric** rather than sunk cost or who championed it. Outcome: the feature had *not* moved its target metric and had no plausible mechanism left to try, so it was minimally maintained, not further invested in — freeing the next cycle's capacity.

## Resolution

The miss was structural, not analytical: **the success metric must be written before the spec, not reconstructed after the launch.** A feature with no pre-committed outcome metric can't be judged a win or a loss, so it defaults to permanent limbo and a maintenance tax. The fix was a PRD gate (named metric + baseline + expected movement + guardrail, defined up front) plus a pre-committed read date, so "did it work?" is answered against a number the team agreed to in advance — and the ship/iterate/kill call follows the metric, not the champion.

**Action for the next PM hitting this pattern:** **write the success metric before the spec.** Name the behavior change, express it as a rate/cohort not a cumulative total, pair it with a guardrail it must not harm, set the read date, and gate the PRD on it. After it ships, traverse the "ship more, iterate, or kill it?" tree in [`../knowledge/product-management-decision-trees.md`](../knowledge/product-management-decision-trees.md) against that metric — a feature that changed nothing is a learning to act on, not a success to defend.

**Sources (retrieved 2026-06-05):**
- Amplitude — *North Star Metric* framework (value-capturing metric decomposed into movable inputs): https://amplitude.com/blog/product-north-star-metric
- Reforge / standard product-analytics practice — outcomes-over-outputs and guardrail-metric pairing are mainstream PM doctrine; treat the *specific* metric choice for a given feature as `[verify-at-use]` and calibrate to the team's funnel.

Any specific activation or completion-rate figure here is illustrative `[ESTIMATE]` — validate against the team's instrumented baseline (CLAUDE.md §2; claim-grounding).
