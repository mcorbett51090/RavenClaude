# A two-point move is not a trend — quantify the noise before calling a metric movement "real"

**Status:** Absolute rule
**Domain:** Statistical QA of metrics / the data-platform seam
**Applies to:** `applied-statistics`

---

## Why this exists

"Revenue is up 18% — is that real?" is a different question from "is revenue up 18%?". The dashboard already answers the second (data-platform's job: *is the number correct?*); this plugin answers the first (*is it real?* — distinguishable from the metric's own week-to-week noise). The reflex failure is reading two consecutive points as a trend, or any week's jump as signal, when the metric's natural variation easily spans that move. Almost every business metric is noisy: small denominators, seasonality, day-of-week effects, and a handful of large accounts make a single-period swing look dramatic and mean nothing. The discipline: before endorsing a movement, quantify the baseline variation and ask whether this move clears it — and attach the uncertainty band so the dashboard stops presenting noise as news.

## How to apply

Quantify the metric's own variability, then test the movement against it — and emit the annotation the widget should carry:

```
1. What is the metric's NATURAL variation?
   baseline period -> mean + a variation band (SD / control-chart limits / a CI on the rate)
   account for: denominator size, seasonality, day-of-week, a few whale accounts (Simpson's risk)

2. Does THIS move clear the noise?
   single move    -> is it outside the baseline band? a proportion/rate test with a CI on the delta
   "trend"        -> need MORE than two points; fit a trend with a CI / control chart, not eyeballing

3. ANNOTATE the widget (the data-platform seam)
   show the uncertainty band, not just the point; label "within normal variation" vs "signal"
```

**Do:**
- Establish the metric's baseline variation (control limits / CI / SD band) before judging any single move.
- Require more than two points before calling something a trend; fit it with an interval rather than connecting two dots.
- Emit the uncertainty band / annotation for the dashboard widget — the `statistical-qa-of-metrics` skill's deliverable.

**Don't:**
- Present a two-point movement as a trend, or a single-week jump as "real", without checking it against the metric's noise.
- Ignore denominator size — an 18% move on 30 events is noise; on 30,000 it may be signal; the rate's CI tells you which.
- Pool across a lurking variable (channel, region, a whale account) and miss a Simpson's reversal inside the segments.

## Edge cases / when the rule does NOT apply

- **A pre-registered A/B test** answers "is it real?" through its design — use the experiment analysis, not a post-hoc control chart on the dashboard.
- **Step-changes with a known cause** (a launch, an outage, a pricing change at a known date) are interventions to analyze (interrupted time series / DiD), not random noise to band — name the event.
- **Operational alerting thresholds** set by the business (SLA breaches) are decision rules, not statistical-significance claims — honor the threshold, but don't dress it up as "statistically significant".

## See also

- [`../skills/statistical-qa-of-metrics/SKILL.md`](../skills/statistical-qa-of-metrics/SKILL.md) — the signal-vs-noise workhorse and the widget annotation it emits.
- [`./report-communicate-uncertainty-to-non-statisticians.md`](./report-communicate-uncertainty-to-non-statisticians.md) — how the uncertainty band is communicated.
- [`./timeseries-test-stationarity-and-autocorrelation.md`](./timeseries-test-stationarity-and-autocorrelation.md) — when the metric is a genuine time series needing a temporal model.
- [`../knowledge/statistical-pitfalls.md`](../knowledge/statistical-pitfalls.md) — Simpson's paradox (#4) lurking inside a pooled dashboard rate.

## Provenance

Codifies the data-platform seam in [`../CLAUDE.md`](../CLAUDE.md) §2 ("data-platform = is the number correct?; this plugin = is it real?") and the anti-patterns "a two-point 'trend' on a dashboard presented as a trend" and "a forecast point line with no prediction interval" in §4. Grounded in the [`../skills/statistical-qa-of-metrics/SKILL.md`](../skills/statistical-qa-of-metrics/SKILL.md) deliverable. Tier 1 / consensus (control-chart / variation-vs-special-cause is standard SPC; Wheeler, *Understanding Variation*).

---

_Last reviewed: 2026-05-30 by `claude`_
