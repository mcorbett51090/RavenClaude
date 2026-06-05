---
scenario_id: 2026-06-05-cls-lcp-perf-budget-regression
contributed_at: 2026-06-05
plugin: frontend-engineering
product: nextjs
product_version: "unknown"
scope: likely-general
tags: [cls, lcp, core-web-vitals, perf-budget, images, fonts]
confidence: high
reviewed: false
---

## Problem

A marketing-adjacent product landing page passed Core Web Vitals at launch, then quietly regressed over two quarters of feature work until field data (CrUX / RUM) showed it failing two of three vitals at the 75th percentile: LCP ~3.8s (good is < 2.5s) and CLS ~0.28 (good is < 0.1). Lab Lighthouse on a developer's fast machine still showed green, so nobody noticed until search-console flagged the URL group as "needs improvement." The team wanted to "make it fast again" without a clear sense of which of the dozen changes caused it.

## Constraints context

- Field thresholds used as the bar (Google's published "good" ranges, evaluated at the 75th percentile of real-user data): LCP < 2.5s, INP < 200ms, CLS < 0.1 [verify-at-use — Google web.dev Core Web Vitals; see source]. _(One unofficial 2026 source claimed Google tightened LCP to 2.0s in a March-2026 update; treated as `[unverified]` and the established 2.5s bar used as the gate.)_
- No perf budget was enforced in CI, so each feature added JS and a render-time element with no back-pressure.
- The LCP element was a hero image loaded by a JS carousel component (so the image URL wasn't in the initial HTML — the browser couldn't preload it).
- Three CLS sources: a web font swapping in late (FOUT shifting the headline), an ad/promo slot with no reserved height, and images with no `width`/`height` attributes.

## Attempts

- Tried: a blanket "optimize images" pass (compress + WebP). Helped transfer size but barely moved LCP, because the LCP image was *discovered late* (inside hydrated JS), not *too big*. Compression doesn't fix a discovery-timing problem.
- Tried: adding `loading="lazy"` to everything, including the hero. This made LCP *worse* — lazy-loading the LCP image delays the very element the metric measures. Lazy-load is for below-the-fold, never the LCP element.
- Tried (the fixes that worked, attributed by cause):
  - **LCP discovery:** moved the hero out of the JS carousel into server-rendered markup, set `fetchpriority="high"`, and added `<link rel="preload">` (via the framework's image primitive) so the browser starts the hero fetch immediately. LCP dropped under 2.5s.
  - **CLS from the font:** set `font-display: optional` (or `swap` with a size-adjusted fallback) and preconnected the font origin, so the headline doesn't reflow when the web font arrives.
  - **CLS from images/slots:** added explicit `width`/`height` (or `aspect-ratio`) to every image and reserved a fixed min-height for the promo slot, so async content lands in pre-allocated space.
- Tried (the durable fix): added a **bundle-and-vitals budget gate** so the regression can't silently come back — a per-route JS budget plus a CLS/LCP check against field data, failing the PR when a change blows the budget.

## Resolution

**Diagnose CWV by metric and by cause — don't "make it fast" in general.** The three vitals have different fixes and a fix for one can hurt another (lazy-loading helped CLS-adjacent transfer but broke LCP). The order that worked:

1. **Read field data first, not lab.** Lighthouse on a fast laptop is a smoke test; CrUX/RUM at the 75th percentile is the bar Google grades. A green lab score with red field data means your devices are too fast and your test conditions too clean.
2. **For LCP, fix *discovery and priority* before size.** The most common LCP bug is the LCP element being hidden behind JS so the preload scanner never sees it. Server-render it, `fetchpriority="high"`, preload it, and never lazy-load it.
3. **For CLS, reserve space for everything async** — images (`width`/`height`/`aspect-ratio`), fonts (`font-display` + size-matched fallback), and any injected slot (fixed min-height). CLS is almost always "content arrived and pushed things down."
4. **Make the budget a gate, not a guideline.** A perf budget that lives in a wiki regresses; one that fails CI holds. Lack of back-pressure is *why* it drifted from green to red over two quarters.

**Action for the next engineer:** when a page "got slow," pull field data and split the problem by vital. Don't apply LCP fixes to a CLS problem. And add the budget to CI in the same PR as the fix — otherwise you'll be back here next quarter.

Cross-reference: this is the field-note complement to [`../best-practices/the-bundle-is-a-budget.md`](../best-practices/the-bundle-is-a-budget.md), [`../best-practices/avoid-layout-shift-reserve-space-for-async-content.md`](../best-practices/avoid-layout-shift-reserve-space-for-async-content.md), and [`../best-practices/optimize-images-and-fonts.md`](../best-practices/optimize-images-and-fonts.md); the runnable budget gate is [`../scripts/perf_budget.py`](../scripts/perf_budget.py). Thresholds: Google Core Web Vitals (https://web.dev/articles/vitals, retrieved 2026-06-05) — LCP < 2.5s, INP < 200ms, CLS < 0.1 at the 75th percentile.
