---
scenario_id: 2026-06-05-false-positive-risk-tier-segment
contributed_at: 2026-06-05
plugin: customer-success-analytics
product: signal-design
product_version: "n/a"
scope: segment-specific
tags: [false-positive, segment-override, threshold, alert-fatigue, recalibrate]
confidence: medium
reviewed: false
---

## Problem

A CS team's Red list was so long nobody worked it. More than a third of the Reds were renewing fine — the tier was crying wolf, and the CSMs had quietly started ignoring it. The risk wasn't a bad signal; it was a **threshold that was right for one segment and wrong for another**, producing a flood of false positives.

## Context

- Segment: B2B SaaS with two very different books — a high-touch enterprise tier and a high-volume SMB tier — scored by **one global threshold set**.
- Constraint: the over-flagged accounts were **concentrated in the SMB segment**. SMB accounts naturally have spikier usage and lower-touch support patterns, so a support-volume / usage-dip threshold tuned on enterprise behavior fired constantly on healthy SMB accounts.
- The team's instinct was to "loosen the thresholds globally," which would have *under*-flagged the enterprise book — trading one failure mode for another.

## Attempts

- Tried: measured the false-Red rate and checked **where** the false positives concentrated before changing anything (the retune-vs-rebuild tree in `customer-success-decision-trees.md`). Finding: >25% false-Red rate, concentrated in one segment, no recent product change. Outcome: the tree pointed at a **segment override**, not a global loosen.
- Tried: added a **segment-specific threshold** for the SMB book (looser support-spike and usage-dip cut-points reflecting its baseline behavior) while leaving the enterprise thresholds untouched. Validated in a parallel test before promoting. Outcome: the SMB false-Red rate dropped sharply without blinding the enterprise tier.
- Tried: instrumented the false-Red rate as an ongoing metric so alert-fatigue couldn't silently creep back, and committed to **recalibrating each renewal cycle** (the retune-after-every-cycle best practice). Outcome: the Red list became short enough that CSMs worked it again.

## Resolution

A long, ignored Red list is usually a **false-positive problem, not a missing-signal problem** — and when the false positives concentrate in one segment, the fix is a **segment override, not a global threshold change**. Loosening globally would have under-flagged the other segment. The discipline: measure the false-Red rate, check whether it concentrates in a segment, apply a segment-specific threshold, validate in parallel before promoting, and instrument the rate so fatigue can't return.

**Action for the next consultant hitting this pattern:** when the Red list is too long to triage, **segment the false positives before touching thresholds.** Concentrated in one segment → segment override (the targeted fix). Diffuse → loosen globally in a parallel test. Product/integration change shifted the baseline → recalibrate, don't replace the signal. Track the false-Red rate as a first-class metric; an ignored tier is worse than no tier. (`segment-overrides-before-global-threshold-changes` best practice.)

**Sources (retrieved 2026-06-05):** segment-specific health scores improve prediction accuracy + calibrate quarterly — https://www.everafter.ai/glossary/customer-health-score ; effective models keep false-positive rates below 30% — https://www.supportbench.com/building-health-score-predicts-churn/ . Accuracy/false-positive figures are vendor-reported `[ESTIMATE]` ranges; validate against the team's own back-test.
