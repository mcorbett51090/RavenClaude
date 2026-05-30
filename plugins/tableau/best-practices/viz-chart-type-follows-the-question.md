# Let the question pick the chart, never the aesthetic

**Status:** Absolute rule — chart type is determined by the *class of question* (comparison / trend / distribution / correlation / part-to-whole / geographic), not by what looks impressive.

**Domain:** Viz design / encoding

**Applies to:** `tableau`

---

## Why this exists

The single most common dashboard failure is a chart chosen for its appearance rather than its fit to the question. A donut for a 9-category breakdown, a dual-axis line for two unrelated measures, a packed-bubble where a bar belongs — each forces the reader to work against the encoding to recover the answer. Cleveland & McGill's perceptual ranking is settled: position-along-a-common-scale (bars, dot plots) is read most accurately, then length, then angle/area (pie, bubble) far down the list. So when the question is "which is bigger," a bar answers it in one glance and a pie makes the reader estimate angles. Picking the chart from the question class — not the gallery — is house opinion #3: *the deliverable is the question answered, not the dashboard.*

## How to apply

Classify the question first, then map to the mark/encoding:

```
Comparison    ("which category is biggest / how do these rank?")
              -> Horizontal bar, sorted descending. Dot plot if many categories.

Trend         ("how has X moved over time?")
              -> Line, continuous (green) date axis. Needs >2 points to be a trend.

Distribution  ("how is X spread / where are the outliers?")
              -> Histogram, box-and-whisker, or jittered strip plot.

Correlation   ("does X move with Y?")
              -> Scatter, two measures on continuous axes, optional trend line.

Part-to-whole ("what share does each piece take of the total?")
              -> Stacked bar or treemap; pie ONLY for 2-3 slices and a static total.

Geographic    ("where, by region?")
              -> Filled (choropleth) map for rates/ratios; symbol map for counts.
```

**Do:**
- Write the question in one sentence and name its class *before* opening the Show Me menu.
- Default to a **sorted horizontal bar** for comparison — it is the most-accurately-read encoding and rarely wrong.
- Use a continuous (green) date pill for trend so gaps in time render as gaps, not as evenly-spaced ticks.

**Don't:**
- Reach for pie/donut/bubble/radar because the dashboard "needs variety" — variety is not a question class.
- Encode a count on a *filled* map (choropleth) — area size distorts counts; use a symbol map and reserve fills for rates.
- Build a dual-axis to show two measures that aren't being compared on the same scale (see the axis-integrity doc).

## Edge cases / when the rule does NOT apply

A single headline KPI is a **BAN (big-ass number)**, not a chart — and that's correct. Pie/donut is defensible for a 2-3 slice part-to-whole where the slices are far apart and the total is the point (e.g., "62% renewed"). A sparkline trades precise reading for density on purpose inside a table. Highly designed "data storytelling" pieces may break the ranking deliberately — but that is an explicit authored choice, defended out loud, not a default.

## See also

- [`./viz-axis-and-dual-axis-integrity.md`](./viz-axis-and-dual-axis-integrity.md) — when comparison/correlation tempts a dual axis
- [`./viz-formatting-and-accessibility.md`](./viz-formatting-and-accessibility.md) — encoding choices that survive colorblindness
- [`../knowledge/viz-calc-decision-trees.md`](../knowledge/viz-calc-decision-trees.md) — the chart-type-by-question-class tree
- [`../agents/tableau-viz-engineer.md`](../agents/tableau-viz-engineer.md) — owns chart-type selection
- Cleveland & McGill (1984), "Graphical Perception" — the encoding-accuracy ranking `[unverified — training knowledge]`

## Provenance

Codifies house opinion #3 from [`../CLAUDE.md`](../CLAUDE.md) ("the deliverable is the question answered, not the dashboard") and the anti-pattern against aesthetic-first chart choice. The perceptual ranking is from the data-viz literature (Cleveland & McGill); the question-class mapping is established Tableau practice.

---

_Last reviewed: 2026-05-30 by `claude`_
