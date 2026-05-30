# Don't let the axis lie — zero-baseline bars, synchronized dual axes, real trends

**Status:** Absolute rule — a truncated quantitative axis, an unsynchronized dual axis, or a two-point "trend" misleads the reader, and a misleading chart is a defect regardless of how it looks.

**Domain:** Viz design / integrity

**Applies to:** `tableau`

---

## Why this exists

The chart's geometry *is* the argument. A bar's length encodes magnitude, so a bar axis that doesn't start at zero exaggerates differences — a 5% gap can be drawn as a 3× gap by cropping the baseline. A dual-axis chart overlays two measures on two independent scales; if the scales aren't synchronized (or aren't intentionally, explicitly different), the crossing point and relative heights imply a relationship that is an artifact of axis choice, not of the data. And a "trend" drawn through two points is just a line between two dots — it has no information about direction. Each of these is on the plugin's anti-pattern list because each ships a *visually convincing* but *false* claim, which is worse than an ugly-but-honest one.

## How to apply

Three checks, run on every quantitative view before it ships:

```
1. BAR BASELINE
   Bars/areas encode magnitude by length -> axis MUST include zero.
   (Right-click axis -> Edit Axis -> uncheck "Include zero" only for
    line/dot charts where position, not length, carries the meaning.)

2. DUAL-AXIS SYNC
   Two measures, same unit (e.g., Sales vs Forecast in $):
     -> right-click the second axis -> "Synchronize Axis". Now heights compare.
   Two measures, different units (Sales $ vs Orders count):
     -> a dual axis is usually the WRONG chart; prefer two panes or a
        connected scatter. If you keep it, the differing scales are a
        deliberate, labeled choice — never an accident.

3. TREND REALITY
   A trend line / "is it going up?" claim needs >2 points and enough
   span to be meaningful. Two months is two dots, not a trend.
```

**Do:**
- Start every bar and area axis at zero.
- Click **Synchronize Axis** on any same-unit dual axis so the two series are literally comparable.
- Label both axes when a dual axis intentionally uses different scales, so the reader knows the heights aren't directly comparable.

**Don't:**
- Truncate a bar axis to "make the difference pop" — that is fabricating a difference.
- Leave a dual axis unsynchronized and let the reader infer a correlation from where the lines cross.
- Draw a trend line through 2-3 points or extrapolate a forecast the data can't support.

## Edge cases / when the rule does NOT apply

**Line and dot/scatter charts** encode by *position*, not length, so a non-zero baseline is legitimate and often necessary to see variation in a tight range — the zero rule is specifically for **bars and areas**. Index/indexed-to-100 and log axes are honest when **labeled as such** (the transformation is disclosed). A dual axis with two genuinely different units (price vs volume) can be defensible as an authored, labeled exception — but it is the exception, defended out loud, not the default.

## See also

- [`./viz-chart-type-follows-the-question.md`](./viz-chart-type-follows-the-question.md) — the dual-axis temptation usually means the wrong chart class
- [`./viz-formatting-and-accessibility.md`](./viz-formatting-and-accessibility.md) — axis labels, number formats, contrast
- [`../agents/tableau-viz-engineer.md`](../agents/tableau-viz-engineer.md) — owns viz integrity
- Tableau Help: "Edit Axes" / "Synchronize dual axes" `[verify-at-build]`

## Provenance

Codifies the final anti-pattern in [`../CLAUDE.md`](../CLAUDE.md) ("a two-point trend, a truncated/aspect-distorted axis, or a dual-axis not synchronized") and the viz-engineer's integrity directive. The zero-baseline-for-length-encodings principle is standard data-viz ethics (Tufte; Cleveland) `[unverified — training knowledge]`.

---

_Last reviewed: 2026-05-30 by `claude`_
