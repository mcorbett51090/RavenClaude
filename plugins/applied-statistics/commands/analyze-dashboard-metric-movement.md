---
description: "Decide whether a dashboard metric movement is real or noise — quantify the metric's baseline variation, test the move against it, require more than two points for a trend, and emit the uncertainty band the widget should carry."
argument-hint: "[the metric move, e.g. 'revenue is up 18% this week — is that real?']"
---

# Analyze a dashboard metric movement

You are running `/applied-statistics:analyze-dashboard-metric-movement`. For the movement the user flagged (`$ARGUMENTS`), answer "is it *real*?" — distinguishable from the metric's own week-to-week noise — not "is the number correct?" (the data platform already answers that). This is the statistical-QA-of-metrics discipline the `applied-statistician` agent owns.

## When to use this

Someone is about to act on (or present) a single-period metric jump or a two-point "trend" off a dashboard. NOT for confirming a number's correctness (a data-platform/ETL question), and NOT for a designed A/B test (that is `/applied-statistics:design-experiment-and-power`).

## Steps

1. **Establish the metric's natural variation first** (`test-distinguish-signal-from-noise-on-dashboard-metrics.md`): build a baseline mean + a variation band (SD / control-chart limits / a CI on the rate) before judging any single move.
2. **Account for the structure that fakes signal** (`test-distinguish-signal-from-noise-on-dashboard-metrics.md`): denominator size, seasonality, day-of-week effects, and a few whale accounts — an 18% move on 30 events is noise; on 30,000 it may be signal; the rate's CI tells you which.
3. **Test the move against the band** (`test-distinguish-signal-from-noise-on-dashboard-metrics.md`): a single move → is it outside the baseline band? Use a proportion/rate test with a CI on the delta. A "trend" → needs MORE than two points; fit a trend with a CI or a control chart, never eyeballing two dots.
4. **Watch for a Simpson's reversal** (`test-distinguish-signal-from-noise-on-dashboard-metrics.md`): don't pool across a lurking variable (channel, region, a whale account) and miss a reversal hiding inside the segments.
5. **If the data is time-ordered, respect temporal dependence** (`timeseries-test-stationarity-and-autocorrelation.md`): two consecutive points are not a trend, and serial correlation makes naive significance overstated — fit with the temporal-dependence gate before calling a direction.
6. **Emit the widget annotation** (`test-distinguish-signal-from-noise-on-dashboard-metrics.md`): show the uncertainty band, not just the point, and label "within normal variation" vs "signal" — the `statistical-qa-of-metrics` skill's deliverable.

## Guardrails

- Never present a two-point movement as a trend or a single-week jump as "real" without checking it against the metric's own noise.
- A small denominator turns ordinary variation into dramatic-looking swings — always carry the rate's CI.
- The dashboard answers "is the number right?"; this command answers "is it real?" — don't conflate the two, and don't re-litigate the ETL.
