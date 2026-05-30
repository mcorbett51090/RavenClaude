# Format for legibility and accessibility — color is never the only channel

**Status:** Pattern — format every shipped view for fast reading and for users who can't perceive color, contrast, or fine detail; treat accessibility as a build requirement, not a polish step.

**Domain:** Viz design / formatting & accessibility

**Applies to:** `tableau`

---

## Why this exists

Roughly 1 in 12 men and 1 in 200 women have a color-vision deficiency `[unverified — training knowledge]`, so a red/green KPI that encodes meaning **only** in hue is unreadable to a meaningful slice of any audience — and that's before low-contrast text, unformatted raw numbers, and label clutter that slow down *every* reader. Formatting and accessibility are the same discipline: reduce the work the reader does to extract the answer. A view that's correct and fast but illegible still fails its job. The fix is cheap when done while building (palette, number format, labels, contrast) and expensive when retrofitted across a finished workbook.

## How to apply

Apply a small, repeatable formatting/accessibility pass to every view:

```
COLOR
  - Use a colorblind-safe palette (Tableau ships "Color Blind" 10).
  - Never let color be the ONLY channel: pair it with shape, label,
    position, or a text indicator (▲/▼, +/-) so meaning survives in B&W.
  - Diverging data -> diverging palette with a meaningful midpoint;
    sequential data -> single-hue ramp. Don't use a rainbow for ordered data.

NUMBERS & TEXT
  - Format measures at the source (currency, %, thousands) so every view
    inherits it — don't reformat per sheet.
  - Label what matters (min/max, latest, the answer), not every mark.
  - Ensure text/background contrast is high enough to read (aim WCAG AA).

STRUCTURE
  - Title states the takeaway, not just the dimension ("Sales fell 8% in Q3",
    not "Sales by Quarter").
  - Tooltips carry the detail so the canvas stays uncluttered.
  - Add a caption/tooltip alt-text path for screen-reader users where supported.
```

**Do:**
- Default to the **Color Blind** palette for any categorical color that carries meaning.
- Encode status with **shape or text plus color** (▲ green / ▼ red), never hue alone.
- Set number formats once on the field/data source so they propagate.

**Don't:**
- Use red-vs-green as the sole signal of good-vs-bad.
- Use a rainbow/spectral palette for ordered or sequential data.
- Bury the answer under labels on every mark — label the few that matter.

## Edge cases / when the rule does NOT apply

A purely exploratory analyst workbook (audience of one, never shared) can relax the full a11y pass — but anything client- or org-facing gets it. Some accessibility affordances (screen-reader semantics, full keyboard navigation) are partly a function of the publishing surface (Server/Cloud/embedded) and their current support level is volatile — confirm against the platform docs `[verify-at-build]` and seam embedding/a11y-on-platform questions to `tableau-admin`. Brand palettes sometimes conflict with colorblind-safety; when they do, add the redundant non-color channel rather than abandoning the brand.

## See also

- [`./viz-chart-type-follows-the-question.md`](./viz-chart-type-follows-the-question.md) — encoding accuracy and the question class
- [`./viz-axis-and-dual-axis-integrity.md`](./viz-axis-and-dual-axis-integrity.md) — axis labels and honest scales
- [`../agents/tableau-viz-engineer.md`](../agents/tableau-viz-engineer.md) — owns formatting & accessibility
- [`../agents/tableau-admin.md`](../agents/tableau-admin.md) — publishing-surface a11y support
- WCAG 2.1 AA contrast guidance; Tableau Help: "Color Blind palette" / "Build accessible views" `[verify-at-build]`

## Provenance

Codifies the viz-engineer's formatting/accessibility directive (step 7) from [`../agents/tableau-viz-engineer.md`](../agents/tableau-viz-engineer.md) and the "no color as the only channel" principle. Color-vision-deficiency prevalence and WCAG thresholds are external references `[unverified — training knowledge]`; Tableau palette/feature names re-verify `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
