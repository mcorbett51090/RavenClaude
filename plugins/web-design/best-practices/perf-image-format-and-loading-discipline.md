# Serve modern image formats responsively, and load them by position

**Status:** Pattern — strong default for every raster image: modern format, responsive `srcset`, dimensioned, and a loading strategy chosen by the image's position relative to the fold.

**Domain:** Performance / Images

**Applies to:** `web-design`

---

## Why this exists

Images are the heaviest part of most pages, and the wrong format or a single oversized source is the most common reason a page blows its weight budget (the hook flags rasters > 500 KB). AVIF and WebP cut bytes dramatically over JPEG/PNG at equal quality; responsive `srcset` stops a phone from downloading a 1600px desktop hero. Just as important is *when* each image loads: the LCP image must load eagerly and early, while below-the-fold images should defer so they don't compete with it. Getting format and loading right is the difference between a 1.5 MB page and a 400 KB one with identical visuals.

## How to apply

Use `<picture>` (or `srcset`) to offer a modern format with a fallback, give every image responsive sources + explicit dimensions, and pick the loading strategy from position.

```html
<!-- Modern format with fallback; responsive sources; dimensioned to prevent CLS -->
<picture>
  <source type="image/avif" srcset="card-400.avif 400w, card-800.avif 800w" sizes="(max-width: 600px) 100vw, 400px" />
  <source type="image/webp" srcset="card-400.webp 400w, card-800.webp 800w" sizes="(max-width: 600px) 100vw, 400px" />
  <img src="card-800.jpg" width="800" height="450"
       loading="lazy" decoding="async" alt="Team reviewing a roadmap on a shared screen" />
</picture>
```

**Do:**
- Prefer AVIF, then WebP, with a JPEG/PNG fallback in the `<img src>`.
- Give every image `width`/`height` (or `aspect-ratio`) and a `sizes` attribute matched to its rendered width.
- Use `loading="lazy"` + `decoding="async"` below the fold; eager + `fetchpriority="high"` for the LCP image.
- Serve through an image CDN so format/size negotiation isn't a build-time guess.

**Don't:**
- Ship one giant source and scale it with CSS (the device still downloads the full file).
- `loading="lazy"` the LCP/hero image (see [`./perf-protect-lcp-with-preload-and-priority.md`](./perf-protect-lcp-with-preload-and-priority.md)).
- Use a JPEG where a clean PNG/SVG is smaller (logos, flat UI, line art → SVG).

## Edge cases / when the rule does NOT apply

- **Logos / icons / flat illustrations** — SVG beats any raster (sharp at every DPR, tiny, themeable with `currentColor`).
- **Transparency + photographic detail** — AVIF/WebP both handle alpha; reach for PNG only when a target lacks support.
- **Decorative images** still need `alt=""` (empty, not omitted) — a missing `alt` is an a11y failure the hook flags.

## See also

- [`./perf-protect-lcp-with-preload-and-priority.md`](./perf-protect-lcp-with-preload-and-priority.md) — the inverse rule for the one image above the fold
- [`./perf-reserve-space-to-prevent-cls.md`](./perf-reserve-space-to-prevent-cls.md) — dimensions prevent the shift
- [`../knowledge/web-design-decision-trees.md`](../knowledge/web-design-decision-trees.md) — "Image format & loading choice" tree
- [`../agents/performance-engineer.md`](../agents/performance-engineer.md) (image optimization), [`../agents/visual-designer.md`](../agents/visual-designer.md) (asset choice)

## Provenance

Distilled from the `performance-engineer` agent's image-optimization surface (AVIF/WebP, `<picture>` + `srcset`, `loading="lazy"` except LCP, `fetchpriority`, `decoding="async"`) and the images section of `web-platform-capabilities-2026.md` (the hook flags > 500 KB rasters; retrieved 2026-05-28).

---

_Last reviewed: 2026-05-30 by `claude`_
