---
scenario_id: 2026-06-05-lcp-perf-budget-hero-image
contributed_at: 2026-06-05
plugin: web-design
product: generic
product_version: "unknown"
scope: likely-general
tags: [lcp, core-web-vitals, perf-budget, hero-image, preload, fonts]
confidence: high
reviewed: false
---

## Problem

A marketing site shipped green on a developer's Lighthouse run, then field data (CrUX / RUM at the 75th percentile) showed it failing LCP — ~3.9 s against the < 2.5 s "good" bar. The hero was a large above-the-fold image swapped in by a JS slideshow, and the brand headline used a custom web font. Stakeholders wanted "make the hero load faster" and assumed the fix was "compress the image." The page had no declared performance budget, so each marketing iteration had quietly added weight with no back-pressure.

## Constraints context

- **Performance has a budget** (constitution §3 #2) and the field bar is the gate: LCP < 2.5 s at the 75th percentile of real users [verify-at-use — Google web.dev Core Web Vitals; thresholds re-confirmed 2026-06-05, LCP/INP/CLS unchanged at 2.5 s / 200 ms / 0.1]. Lab Lighthouse on a fast laptop is a smoke test, not the grade.
- The LCP element was discovered **late**: its URL lived inside hydrated JS (the slideshow), so the browser's preload scanner never saw it in the initial HTML and couldn't start the fetch early.
- The brand would not drop the custom display font, so a font swap was reflowing the headline and competing for bandwidth with the hero.
- A marketing-site total-transfer ceiling was in play (§4 — page weight > 1.5 MB is a smell), but transfer size was not the actual LCP driver here.

## Attempts

- Tried: a blanket "optimize images" pass (compress + WebP/AVIF). Reduced transfer size but barely moved LCP — because the hero was *discovered late*, not *too big*. Compression doesn't fix a discovery-timing problem.
- Tried: adding `loading="lazy"` site-wide, including the hero. This made LCP **worse** — lazy-loading the LCP element delays the very thing the metric measures. Lazy-load is for below-the-fold, never the LCP element.
- Tried (the fixes that worked, attributed by cause):
  - **Discovery + priority:** moved the hero out of the JS slideshow into server-rendered markup, added `<link rel="preload">` for it, and set `fetchpriority="high"` so the browser starts the hero fetch immediately. LCP dropped under 2.5 s.
  - **Format + dimensions:** served AVIF/WebP with a responsive `srcset` and correct `width`/`height` so the right-sized asset loads and no reflow occurs.
  - **Font competition:** preconnected the font origin and set `font-display: optional` (or `swap` with a size-matched fallback) so the headline paints immediately and the font swap doesn't shift it.
- Tried (the durable fix): wrote a per-page **performance budget** and made it a CI gate so the regression can't silently creep back over the next marketing cycle.

## Resolution

**For LCP, fix *discovery and priority* before size.** The most common LCP bug is the LCP element hidden behind JS so the preload scanner never sees it. The order that worked:

1. **Read field data first, not lab.** Lighthouse green on a fast machine + red field data means your test device is too fast and conditions too clean. CrUX/RUM at p75 is what Google grades.
2. **Server-render the LCP element, `preload` it, `fetchpriority="high"`, never lazy-load it.** Discovery timing beats compression for the hero.
3. **Right-size + modern format** (AVIF/WebP + `srcset` + explicit dimensions) after discovery is fixed — and reserve space so fixing LCP doesn't introduce CLS.
4. **Tame the font:** preconnect + `font-display` so the display font neither blocks paint nor shifts the headline.
5. **Make the budget a CI gate, not a wiki page.** No back-pressure is *why* the page drifted from green to red.

**Action for the next engineer:** when a hero is "slow," pull field data, confirm whether the LCP element is *discovered late* (the usual culprit) before reaching for compression, and add the budget to CI in the same change. Cross-reference [`../best-practices/perf-protect-lcp-with-preload-and-priority.md`](../best-practices/perf-protect-lcp-with-preload-and-priority.md), [`../best-practices/perf-image-format-and-loading-discipline.md`](../best-practices/perf-image-format-and-loading-discipline.md), [`../best-practices/perf-font-loading-discipline.md`](../best-practices/perf-font-loading-discipline.md), [`../best-practices/budget-core-web-vitals-before-build.md`](../best-practices/budget-core-web-vitals-before-build.md), and the [`../skills/core-web-vitals-tuning/SKILL.md`](../skills/core-web-vitals-tuning/SKILL.md) fix-by-symptom map. The CWV pass/fail arithmetic is mechanizable in CI as a perf-budget gate — the `frontend-engineering` plugin ships `perf_budget.py` (`vitals` mode) for exactly this, and this plugin's own `scripts/contrast_ratio.py` covers the contrast side.

**Sources for the standards cited:** Google Core Web Vitals thresholds — LCP < 2.5 s, INP < 200 ms, CLS < 0.1 at the 75th percentile — https://web.dev/articles/vitals and https://web.dev/articles/defining-core-web-vitals-thresholds (retrieved 2026-06-05; thresholds confirmed unchanged for 2026, INP remains the most-failed). The thresholds are version-volatile — `[verify-at-use]`, re-confirm on the Researcher sweep.
