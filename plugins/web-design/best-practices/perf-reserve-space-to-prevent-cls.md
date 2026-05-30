# Reserve space for everything that loads late (no layout shift after first paint)

**Status:** Absolute rule — every element that arrives after first paint (image, font, ad, embed, injected banner) has its space reserved before it lands. CLS > 0.1 ships only with a written justification (house opinion #7).

**Domain:** Performance / Core Web Vitals

**Applies to:** `web-design`

---

## Why this exists

Cumulative Layout Shift measures content jumping under the user — the "I tapped the wrong button because it moved" failure. The 2026 "good" bar is **< 0.1** at field p75 [verify-at-build — CLS threshold]. Almost every shift comes from late-arriving content that wasn't given a reserved box: an `<img>` with no dimensions, a web font swapping in at a different metric than its fallback, a late ad/embed/cookie-banner pushing content down. The fix is always the same shape — reserve the space up front — and it is cheap if done before build, expensive if retrofitted after launch.

## How to apply

Give every late-loading element a known size before it loads: explicit dimensions or `aspect-ratio` for media, metric-matched font fallbacks, and reserved containers for ads/embeds.

```html
<!-- Image: width/height (or aspect-ratio) reserves the box before bytes arrive -->
<img src="card.avif" width="640" height="360" alt="..." style="aspect-ratio: 16 / 9; width: 100%; height: auto;" />

<!-- Embed/ad slot: reserve the height so the injected iframe doesn't shove content -->
<div class="ad-slot" style="min-block-size: 250px;"></div>
```

```css
/* Font: match the fallback's metrics so the swap doesn't reflow text */
@font-face {
  font-family: "Brand";
  src: url("/brand.woff2") format("woff2");
  font-display: optional;          /* no swap for non-critical display fonts → zero CLS */
  size-adjust: 102%;               /* align fallback metrics to the web font */
}
```

**Do:**
- Set `width`/`height` or `aspect-ratio` on every image and video.
- Use `font-display: optional` for non-critical display fonts (or `size-adjust` / `ascent-override` to match the fallback) so the swap causes no reflow.
- Reserve a fixed-height container for ads, embeds, and async banners.

**Don't:**
- Insert content *above* existing content after paint (a notification bar pushing the page down).
- Animate layout properties (`top`/`left`/`width`/`height`) — animate `transform`/`opacity` (compositor-only, no reflow).
- Lazy-load above-the-fold media without a reserved box.

## Edge cases / when the rule does NOT apply

- **User-initiated expansion** (an accordion the user opened, "load more" they clicked) is expected motion and excluded from CLS — but only if it's genuinely user-triggered.
- **CLS > 0.1 with written justification** (house opinion #7) — rare, and the justification is the deliverable, not a shrug.
- **Skeleton screens** that match the final layout's dimensions are the right pattern for content that will appear.

## See also

- [`./perf-protect-lcp-with-preload-and-priority.md`](./perf-protect-lcp-with-preload-and-priority.md) — image dimensions serve both LCP and CLS
- [`./perf-font-loading-discipline.md`](./perf-font-loading-discipline.md) — font swap is a top CLS source
- [`../knowledge/web-design-decision-trees.md`](../knowledge/web-design-decision-trees.md) — "Which CWV is failing → which fix" tree
- [`../agents/performance-engineer.md`](../agents/performance-engineer.md) — CLS fix-by-symptom map

## Provenance

Distilled from the `performance-engineer` agent's CLS fix-by-symptom map (image without dimensions, font swap, late ad/embed, animated dimensions) and house opinion #7 ("no layout shift after first paint; CLS > 0.1 ships only with justification"); `size-adjust`/`font-display` from `web-platform-capabilities-2026.md` and `modern-css-2026.md` (retrieved 2026-05-28).

---

_Last reviewed: 2026-05-30 by `claude`_
