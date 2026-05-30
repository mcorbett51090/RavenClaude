# Build responsive type and space mobile-first, fluid where it earns its keep

**Status:** Pattern — design narrowest first and scale up (house opinion #3); use fluid `clamp()` scales for type and space instead of stacking breakpoint overrides.

**Domain:** Responsive / Layout

**Applies to:** `web-design`

---

## Why this exists

"Mobile-first or it's not done" (house opinion #3) is a design order, not a viewport: start at the narrowest layout and expand up, so the default cascade is the small screen and `min-width` queries add complexity only where the space allows it. The `max-width`-cascade-down habit inverts this and ships desktop assumptions to phones. Fluid type/space (`clamp()`) then removes most of the breakpoint-juggling: one expression interpolates smoothly between a min and a max, so headings and rhythm scale with the viewport instead of jumping at arbitrary widths. Modern CSS makes the component-level version of this cleaner still — **container queries** let a component respond to its own parent's width, not the viewport.

## How to apply

Author base styles for mobile, layer `min-width` queries (in `em` so user zoom works), and express type/space as `clamp(min, fluid, max)` with the ends as tokens.

```css
:root {
  /* Fluid type: min 1rem at small screens → max 1.25rem at large; ends are tokens */
  --font-body: clamp(1rem, 0.95rem + 0.4vw, 1.25rem);
  --font-h1:   clamp(2rem, 1.5rem + 3vw, 3.5rem);
  --space-section: clamp(3rem, 2rem + 6vw, 8rem);
}
body { font-size: var(--font-body); }
h1   { font-size: var(--font-h1); }

/* Mobile-first: base = small screen; min-width (in em) adds the desktop layout */
.grid { display: grid; gap: var(--space-4); }       /* 1 column by default */
@media (min-width: 48em) {                            /* em → respects user zoom */
  .grid { grid-template-columns: repeat(2, 1fr); }
}

/* Component-level: respond to the PARENT's width, not the viewport */
.card-wrap { container-type: inline-size; }
@container (min-width: 30em) { .card { grid-template-columns: auto 1fr; } }
```

**Do:**
- Write base styles for the narrowest screen; expand up with `min-width`.
- Use `em`/`rem` for breakpoints and type so user zoom and font-size preferences work.
- Reach for **container queries** when a component must adapt to its slot, not the page.

**Don't:**
- Design in a 1440 desktop frame and "scale down" (the `ux-designer` flags this).
- Use `px` for typography breakpoints — it breaks user zoom (`frontend-implementer` anti-pattern).
- Let a fluid `clamp()` shrink text below ~1rem body or grow it past readable line lengths (cap with the max).

## Edge cases / when the rule does NOT apply

- **Fixed-chrome UI** (a toolbar, a data-dense table) may have a genuine minimum width where below it you switch layout wholesale rather than fluidly scale.
- **Container queries need a sized container** — a `container-type` on a zero-height parent does nothing; verify Baseline for the target audience first.
- **Line length** is the real constraint for body text — cap measure with `max-inline-size: 65ch` regardless of fluid font scaling.

## See also

- [`./visual-design-tokens-not-hardcoded-values.md`](./visual-design-tokens-not-hardcoded-values.md) — `clamp()` ends are tokens
- [`./content-readability-and-hierarchy.md`](./content-readability-and-hierarchy.md) — measure + scale serve readability
- [`../knowledge/modern-css-2026.md`](../knowledge/modern-css-2026.md) — container queries, logical properties, `clamp()`
- [`../agents/frontend-implementer.md`](../agents/frontend-implementer.md) (fluid type/space, container queries), [`../agents/visual-designer.md`](../agents/visual-designer.md) (the scales)

## Provenance

Distilled from house opinion #3 (mobile-first), the `frontend-implementer` responsive surface (fluid type/space, container queries, `em` breakpoints) and its `px`-typography-breakpoint anti-pattern, the `ux-designer` "designed in 1440 and scaled down" anti-pattern, and the container-query / logical-property guidance in `modern-css-2026.md` (retrieved 2026-05-28).

---

_Last reviewed: 2026-05-30 by `claude`_
