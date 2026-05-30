# Protect the LCP element with preload + priority, never lazy-load it

**Status:** Absolute rule — the Largest Contentful Paint element is preloaded, priority-hinted, correctly sized, and never deferred. Lazy-loading the LCP image is a bug.

**Domain:** Performance / Core Web Vitals

**Applies to:** `web-design`

---

## Why this exists

LCP is the loading metric users feel as "is it there yet," with a 2026 "good" threshold of **< 2.5 s** at field p75 [verify-at-build — CWV thresholds]. The single most common LCP regression is also the cheapest to fix: the hero image is discovered late (it's referenced deep in CSS or hydrated by JS), under-prioritized by the browser's default heuristics, or — worst — carries `loading="lazy"`, which actively *defers* the one image that defines the score. Three attributes on one element routinely move LCP by whole seconds, and they cost no design change.

## How to apply

Identify the LCP element (usually the hero image or H1 over a background), then preload it, raise its fetch priority, give it explicit dimensions, and forbid lazy-loading on it.

```html
<!-- In <head>: discover the hero before the parser reaches the <img> -->
<link rel="preload" as="image" href="/hero.avif" fetchpriority="high"
      imagesrcset="/hero-800.avif 800w, /hero-1600.avif 1600w" imagesizes="100vw" />

<!-- The element itself: eager, high-priority, dimensioned (dimensions also prevent CLS) -->
<img src="/hero-1600.avif" srcset="/hero-800.avif 800w, /hero-1600.avif 1600w"
     sizes="100vw" width="1600" height="900"
     fetchpriority="high" decoding="async" alt="Product dashboard showing the live metrics view" />
```

**Do:**
- Put `fetchpriority="high"` + a `<link rel="preload" as="image">` on the LCP image; `preconnect` to its origin if it's on an image CDN.
- Give the LCP image explicit `width`/`height` (or an `aspect-ratio` box) so it reserves space.
- If the LCP is text over a background, preload the **font** that text uses.

**Don't:**
- Put `loading="lazy"` on anything above the fold — it defers the LCP candidate.
- Render the hero via client-side JS that only resolves after hydration.
- Lower-prioritize the hero by burying its URL in a background-image deep in a late stylesheet.

## Edge cases / when the rule does NOT apply

- **The LCP element varies by viewport** (a different hero on mobile vs desktop) — preload conditionally with `media` on the `<link>`, or you'll preload an image you don't paint.
- **First-party inline SVG / CSS gradient hero** — no preload needed; there's no separate resource to discover. Focus on font and render-blocking CSS instead.
- **Below-the-fold images** are the inverse case: `loading="lazy"` + lower priority is correct there.

## See also

- [`./budget-core-web-vitals-before-build.md`](./budget-core-web-vitals-before-build.md) — the budget LCP lives inside
- [`./perf-image-format-and-loading-discipline.md`](./perf-image-format-and-loading-discipline.md) — format + responsive sizing for the same image
- [`../knowledge/web-design-decision-trees.md`](../knowledge/web-design-decision-trees.md) — "Which CWV is failing → which fix" tree
- [`../knowledge/web-platform-capabilities-2026.md`](../knowledge/web-platform-capabilities-2026.md) — `fetchpriority`, priority hints, LCP thresholds
- [`../agents/performance-engineer.md`](../agents/performance-engineer.md) — owns the LCP fix-by-symptom map

## Provenance

Distilled from the `performance-engineer` agent's LCP fix-by-symptom map and opinions ("LCP image gets `fetchpriority="high"` + `preload` + correct dimensions"; "`loading="lazy"` is not for above-the-fold images") and the `fetchpriority` / CWV section of `web-platform-capabilities-2026.md` (web.dev / Chrome for Developers, retrieved 2026-05-28).

---

_Last reviewed: 2026-05-30 by `claude`_
