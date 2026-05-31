---
description: Tune Core Web Vitals against a declared budget measured in the field — protect the LCP element with preload + fetchpriority (never lazy-load it), keep INP under 200ms by breaking up long tasks, and prevent CLS by reserving space for everything that loads late.
argument-hint: "[the page + symptom, e.g. 'the homepage feels laggy on tap' or a URL]"
---

# Tune Core Web Vitals

You are running `/web-design:tune-core-web-vitals`. Diagnose and fix the Core Web Vitals for the page the user described (`$ARGUMENTS`), following this plugin's `performance-engineer` discipline. Optimizations without measurement are theater — measure in the field at p75, then fix at the lowest-cost layer.

## When to use this

A slow-page diagnosis, a pre-launch performance gate, or a CrUX/RUM field-data regression. Not for a page with no declared budget — set the budget first (step 1 does this).

## Steps

1. **Declare a budget and measure in the field** (`budget-core-web-vitals-before-build`): set the 2026 thresholds as field targets at p75 — LCP < 2.5s, INP < 200ms, CLS < 0.1 — plus asset corollaries (JS <= 100KB compressed for marketing, hero <= 500KB, <= 5 third-party scripts). CrUX/RUM is authoritative; Lighthouse is a diagnostic forecast, not proof of speed. INP is the most-failed 2026 metric (~43% of sites).
2. **Protect the LCP element** (`perf-protect-lcp-with-preload-and-priority`): preload the hero with `fetchpriority="high"`, give it explicit `width`/`height`, and never `loading="lazy"` it. If the LCP is text over a background, preload the font instead. Don't render the hero via client-side JS that resolves after hydration.
3. **Keep INP under 200ms by breaking up long tasks** (`perf-keep-inp-under-200ms`): find long main-thread tasks (DevTools / long-animation-frames API / web-vitals attribution), paint a pending state *before* the heavy work, then `scheduler.yield()` and process in chunks; defer/async non-critical JS; move one unavoidable heavy computation to a Web Worker.
4. **Reserve space to prevent CLS** (`perf-reserve-space-to-prevent-cls`): explicit dimensions or `aspect-ratio` on every late-arriving image/embed/ad, metric-matched font fallbacks (`size-adjust`), and no content inserted *above* existing content after paint. Animate `transform`/`opacity`, never layout properties.
5. **Serve images and fonts with discipline** (`perf-image-format-and-loading-discipline`, `perf-font-loading-discipline`): AVIF/WebP with fallback + responsive `srcset` + `sizes`; lazy + `decoding="async"` below the fold; one variable text font preloaded with `font-display: swap`, decorative faces `optional`, two display fonts max.

## Guardrails

- CLS > 0.1 ships only with a written justification (the justification is the deliverable, not a shrug); user-initiated expansion is excluded from CLS.
- Don't cite "Lighthouse 100" as evidence of speed with no field data, and don't add a service worker "for performance" with no measured benefit.
- Report the budget delta for every change (`Perf / a11y budget impact:` line); third-party scripts are debt — catalogue them.
