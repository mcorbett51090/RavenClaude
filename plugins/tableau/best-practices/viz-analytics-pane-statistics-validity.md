# Analytics-pane stats are real statistics — forecast, cluster, and trend only when they're defensible

**Status:** Primary diagnostic — before dragging a Forecast, Cluster, Trend Line, or reference distribution onto a viz, check that the statistical preconditions hold; an indefensible model on a dashboard is a wrong answer with a confidence band.

**Domain:** Viz / statistics

**Applies to:** `tableau`

---

## Why this exists

Tableau's Analytics pane makes forecasting, clustering, and trend/reference modeling a drag-and-drop — which means they get applied without the statistical judgment they require. A stakeholder asks for "a 12-month forecast," someone drops Forecast on a 6-point seasonal series, and the dashboard now ships an exponential-smoothing projection with prediction intervals that mean nothing. These are genuine statistical models (exponential smoothing for forecast, k-means for cluster, OLS for trend) with preconditions; presenting their output without checking the preconditions is the analytics equivalent of a truncated axis. (Deep statistical method-selection belongs to `applied-statistics`; this rule is the Tableau-surface guardrail — when to use the built-in feature vs. push back or model upstream.)

## How to apply

**Forecast (exponential smoothing):**
- Needs enough history and a stable pattern. As a rule of thumb you want at least **2 full seasonal cycles** to detect seasonality (≥24 months for monthly seasonality), and several points beyond that.
- Check Tableau's *Describe Forecast* — it reports the model chosen and quality; if it picked "no seasonality" on data you know is seasonal, the history is too short.
- The prediction interval widens with horizon — don't forecast 12 months from 8 points and present a narrow band.

**Clustering (k-means):**
- Tableau picks *k* automatically (or you set it) — a cluster result is only meaningful if the chosen variables actually separate the data; eyeball the scatter first.
- Standardize/consider the input measures; clusters on un-scaled mixed-unit measures are dominated by the largest-range variable.

**Trend lines (OLS) & reference bands:**
- A linear trend on 2–3 points, or on a clearly non-linear series, misleads — check R²/p-value (*Describe Trend Model*) before shipping.
- A reference distribution / band is descriptive, not inferential — don't read it as a significance test.

**The push-back move:** if the preconditions don't hold, say so and offer the alternative — more history, a different model, or escalate the real statistical question to `applied-statistics` — rather than shipping the drag-and-drop output.

**Do:** check *Describe Forecast / Describe Trend Model* before shipping; ensure ≥2 seasonal cycles for a seasonal forecast; eyeball cluster separation; state intervals honestly.

**Don't:** forecast from a handful of points; present a trend line without checking fit; read a reference band as inference; treat the auto-chosen model as automatically valid.

## Edge cases / when the rule does NOT apply

A purely *illustrative* trend line on a clearly-linear exploratory view (with the caveat stated) is fine. Genuinely hard statistical questions — is this forecast model appropriate, is this effect significant, what about non-stationarity — are out of Tableau's lane and escalate to `applied-statistics` (the seam). Exact Analytics-pane model internals and *Describe* outputs are version-sensitive — `[verify-at-build]`.

## See also

- [`./viz-densification-and-domain-padding.md`](./viz-densification-and-domain-padding.md) — forecasts rely on a padded continuous axis; control it
- [`./viz-axis-and-dual-axis-integrity.md`](./viz-axis-and-dual-axis-integrity.md) — the two-point-"trend" warning lives here too
- [`../agents/tableau-viz-engineer.md`](../agents/tableau-viz-engineer.md) — owns viz correctness; escalates real stats questions
- `applied-statistics` plugin — the seam for forecast-model-validity / significance questions
- [Tableau — forecasting / Describe Forecast](https://help.tableau.com/current/pro/desktop/en-us/forecast_describe.htm) — authoritative

## Provenance

Surfaced by the two-panel + tiebreak coverage campaign (2026-06-01, Panel 3 BUILD): trend-line *visual* honesty was covered (`viz-axis-and-dual-axis-integrity.md`) but the built-in **forecast-model validity** (seasonality/history) and **clustering validity** were absent (a grep for exponential-smoothing/k-means/seasonality returned nothing). Grounded in Tableau's forecasting/clustering docs; the statistical preconditions cross-reference `applied-statistics`. Model internals are `[verify-at-build]`.

---

_Last reviewed: 2026-06-01 by `claude`_
