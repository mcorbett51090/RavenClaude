---
scenario_id: 2026-06-05-ab-peeking-early-stop
contributed_at: 2026-06-05
plugin: applied-statistics
product: experiment-design
product_version: "n/a"
scope: likely-general
tags: [ab-testing, peeking, sequential, type-i-error, stopping-rule]
confidence: medium
reviewed: false
---

## Problem

An engineer reported a "clear winner": a new pricing-page layout hit **p = 0.03** four days into a test that had been sized for two weeks, and the team stopped the test and shipped it. A month later the metric had drifted back to baseline. The consultant was asked, on the *next* such test, why the win didn't hold — and what to do differently.

## Context

- Design: a fixed-horizon A/B test sized for 14 days (the sample-size math assumed a single look at the pre-planned end).
- The team had a dashboard that **recomputed significance continuously** and watched it daily — they stopped the moment it crossed p < 0.05 (day 4).
- This is an *experiment-apparatus* property (continuous significance readout + an ad-hoc stop), which is the lane of the `experimentation-growth-engineering` plugin; the **statistical-validity** read is this plugin's.

## Attempts

- Tried: named the error — **peeking / optional stopping on a fixed-horizon test** (pitfall: peeking; the A/B decision tree's `PEEK` leaf in [`../knowledge/stats-test-selection-decision-trees.md`](../knowledge/stats-test-selection-decision-trees.md)). Checking a fixed-horizon test repeatedly and stopping at the first p < 0.05 **inflates the Type I error far above 5%** — with many looks the false-positive rate climbs toward ~20-30%+. A "p = 0.03" obtained by stopping at the first threshold crossing is **not** a 3% false-positive result; the nominal p-value is invalid because the stopping rule wasn't accounted for. Outcome: the day-4 "win" was reclassified as **directional only**, consistent with it later regressing to the mean.
- Tried: separated *the inference fix* (this plugin) from *the apparatus fix* (the adjacent plugin). The inference fix for a result already collected this way: report it as directional, and **re-run** under a valid design. The apparatus fix: a **sequential testing** method that makes continuous monitoring *valid* — always-valid p-values / group-sequential boundaries (alpha-spending) / mSPRT — so the team *can* peek and stop early without inflating error.
- Tried (the move that worked): handed the sequential-harness build-out to `experimentation-growth-engineering` (their lane: assignment, exposure logging, the always-valid-p readout), and kept the statistical contract here — *if* the dashboard shows a sequential/always-valid p, an early stop is legitimate; if it shows a naive fixed-horizon p, it is not. Documented the seam so the two plugins don't duplicate the harness narrative.

## Resolution

The early "win" was a **peeking artifact**: stopping a fixed-horizon test at the first p < 0.05 inflates the false-positive rate, so the day-4 result was directional, not confirmatory — and it regressed because it was likely noise. The defensible path forward: either run fixed-horizon tests to their pre-planned end (no early peeking), or adopt a **sequential testing** method (always-valid p / alpha-spending / mSPRT) that licenses valid early stopping. The harness for the latter is the `experimentation-growth-engineering` plugin's lane.

**Action for the next consultant hitting this pattern:** when someone "stopped early because it crossed significance," ask **how the p-value was computed** — fixed-horizon p under repeated looks is invalid (peeking), and the result is directional at best. The fix is a sequential design, not a tighter ad-hoc threshold. Route the apparatus build (always-valid-p readout, group-sequential boundaries) to `experimentation-growth-engineering`; keep the validity verdict here. Pre-register the stopping rule in the [`../templates/experiment-design-doc.md`](../templates/experiment-design-doc.md) before launch.

**Sources for the methods cited:** peeking / optional-stopping inflates Type I error — Johari, Pekelis & Walsh (2017/2022), "Always Valid Inference: Continuous Monitoring of A/B Tests," *Operations Research* (the Optimizely "Stats Engine" basis); group-sequential alpha-spending — Lan & DeMets (1983), *Biometrika* 70(3):659-663. Sequential A/B context per [`../knowledge/experiment-design-and-ab-testing.md`](../knowledge/experiment-design-and-ab-testing.md). Figures are illustrative; validate against the engagement's actual data before a deliverable.
