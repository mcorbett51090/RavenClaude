---
scenario_id: 2026-06-05-underpowered-test-mde-miss
contributed_at: 2026-06-05
plugin: experimentation-growth-engineering
product: experimentation
product_version: "n/a"
scope: likely-general
tags: [underpowered, mde, sample-size, power, null-result]
confidence: high
reviewed: false
---

## Problem

A team ran a checkout redesign A/B test for two weeks, saw a flat result (p = 0.34), and concluded "the redesign doesn't help — kill it." A month later a near-identical redesign at a partner org showed a clear +6% relative lift. The first team had not been wrong about the design; they had run a test that **could never have detected the effect they cared about**. The flat result was an underpowered null, read as "no effect."

## Context

- Baseline checkout-completion rate ~5%; the page was deep in the funnel, so eligible traffic was only ~3,500 users/day across both arms.
- The team wanted to detect a meaningful lift but had never computed the minimum detectable effect for their available sample and duration.
- A two-week run gave them roughly 49,000 total / ~24,500 per arm.

## Attempts

- Tried: re-running the same test "to be sure." Same flat result — re-running an underpowered test reproduces the underpowering, not signal.
- Tried (the diagnosis): computed the MDE the sample could actually support. At ~24,500/arm, 5% baseline, alpha 0.05, 80% power, the smallest detectable absolute effect is ~+0.56pp (a ~+11% relative lift). A realistic redesign lift of +5-6% relative (~+0.25-0.30pp absolute) was **well below the detectable floor** — the test was structurally blind to the effect they were hoping for. (`python3 scripts/experiment_calc.py mde --baseline 5% --per-arm 24500` reproduces the floor.)
- Tried (the move that worked): pre-sized the next test. To detect a +0.3pp absolute lift at 80% power they needed ~85,000/arm — ~7 weeks at their traffic, not 2. They (a) accepted a longer horizon, (b) moved the test up the funnel where eligible traffic was higher, and (c) pre-registered the horizon so the result couldn't be read early or killed prematurely.

## Resolution

**A flat result from an underpowered test is "we couldn't see it," not "it isn't there."** The fix was to compute MDE *before* committing a horizon: size for the smallest effect worth shipping, and if the required N exceeds available traffic × a sane duration, either extend, move the test to a higher-traffic surface, pick a more sensitive metric, or accept that this change can't be measured here.

**Action for the next engineer:** before any test, run the sizing — `experiment_calc.py sample-size --baseline <p> --mde <smallest-worth-shipping> --daily-traffic <eligible/day>` — and refuse to launch (or relabel as "directional only") if the horizon is unrealistic. Treat every flat result as a power question first: was the test even capable of detecting the effect? The significance / confidence-interval verdict is `applied-statistics`'; the apparatus owns the sizing (CLAUDE.md §3 #1).

Cross-reference: complements [`../best-practices/metric-sensitivity-before-launch.md`](../best-practices/metric-sensitivity-before-launch.md) and the "Ship, iterate, or kill" tree's *underpowered-vs-no-effect* branch in [`../knowledge/experimentation-growth-engineering-decision-trees.md`](../knowledge/experimentation-growth-engineering-decision-trees.md).

**Sources (retrieved 2026-06-05):**
- Two-proportion sample-size / power / MDE formula — https://en.wikipedia.org/wiki/Two-proportion_Z-test ; derivation https://towardsdatascience.com/probing-into-minimum-sample-size-formula-derivation-and-usage/
- MDE & underpowered-study framing — https://mbrenndoerfer.com/writing/sample-size-minimum-detectable-effect-power-analysis-mde-underpowered-studies
- The specific MDE/N figures here are reproduced by the bundled `scripts/experiment_calc.py`; validate against your real baseline + traffic at use.
