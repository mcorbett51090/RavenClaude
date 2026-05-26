---
name: statistical-qa-of-metrics
description: Decide whether a dashboard metric movement, comparison, or trend is signal or noise — and annotate it honestly (significance, confidence interval, "not enough data yet"). The interop seam with data-platform — invoked by `data-platform/dashboard-builder` when a widget shows a comparison/trend that needs a statistical-validity annotation. data-platform answers "is this number correct?"; this skill answers "is it real?". Used by `applied-statistician` (primary) + `data-platform/dashboard-builder`.
---

# Skill: statistical-qa-of-metrics

> **Invoked by:** `applied-statistician` (primary) **and** `data-platform/dashboard-builder` (the seam — when a widget shows a comparison/trend that needs a significance/CI annotation).
>
> **The seam:** `data-platform` owns *"is this number correct?"* — present, in-range, reconciled, fresh (its [`data-quality-tests`](../../../data-platform/skills/data-quality-tests/SKILL.md) skill). **This skill owns *"is this number real?"*** — is the movement signal or sampling noise; does the comparison have enough data; is the trend honest. Non-overlapping by design.
>
> **When to invoke:** "revenue is up 18% — is that real or noise?"; "this KPI tile shows a WoW change — should we annotate it?"; "the dashboard shows variant B winning — can we trust it?"
>
> **Output:** a signal-vs-noise verdict + the annotation to put on the widget (CI, significance flag, or "insufficient data") + the caveat.

## Procedure

1. **Classify the widget's claim:** a *point comparison* (this period vs last), a *trend* (slope over time), or a *group comparison* (segment A vs B).
2. **Get the denominators.** A "+18%" on n=40 is very different from n=40,000. No sample size → the only honest annotation is "insufficient data to call."
3. **Attach uncertainty, not just a point estimate:**
   - **Rate/proportion KPI** → Wilson confidence interval on the rate; flag whether the period-over-period change's CI excludes zero.
   - **Mean/continuous KPI** → CI on the difference (t-based or bootstrap if skewed).
   - **Count/rare events** → Poisson CI; warn that small counts swing wildly.
4. **Distinguish noise from signal explicitly.** "Up 18%, 95% CI [−4%, +40%]" → the honest annotation is *"within normal variation — not yet distinguishable from noise,"* not "up 18%."
5. **For trends,** prefer a fitted slope + CI (or a control chart band) over eyeballing two points. Two-point "trends" are the most common dashboard lie.
6. **Return the annotation** the dashboard widget should display, plus the one-line caveat.

## Annotation patterns for widgets

| Widget shows | Honest annotation |
|---|---|
| "Revenue +18% WoW" (small n) | "+18% (95% CI −4% to +40%) — within normal weekly variation" |
| "Conversion 6.5% vs 5.0%" | "+1.5pp (95% CI +0.6 to +2.4pp), significant at α=0.05" |
| "Signups trending up" (2 points) | replace with a slope + band, or "1 week of data — trend not yet established" |
| A/B winner on the dashboard | route to [`../experiment-analysis/SKILL.md`](../experiment-analysis/SKILL.md) for the full verdict |

## Guardrails
- **Never let a widget assert a movement without an uncertainty band** when the sample is small enough for noise to dominate.
- A KPI provenance note (source query, date range, baseline) is `data-platform`'s job (its house opinion #7); the **statistical** annotation is this skill's job. Don't duplicate; complement.
- Anomaly **detection method** lives here; anomaly **operational alerting** lives in `data-platform`. Keep the seam at "method vs ops."
