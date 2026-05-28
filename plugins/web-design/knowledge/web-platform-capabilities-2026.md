# Web platform capabilities & Core Web Vitals (2026)

**Last reviewed:** 2026-05-28 · **Confidence:** medium-high — the web platform ships continuously; this is the dated freshness anchor for the web-design plugin. Re-verify thresholds + Baseline on the Researcher sweep. Sources: web.dev / MDN / Chrome for Developers (retrieval-dated).
**Owner:** `performance-engineer` + `web-architect` (complements the `core-web-vitals-tuning` + `third-party-script-hygiene` skills).

## Core Web Vitals (2026 thresholds)
| Metric | Measures | "Good" | Notes |
|---|---|---|---|
| **LCP** (Largest Contentful Paint) | loading | **< 2.5 s** | optimize the hero image/font; `fetchpriority="high"` on the LCP image; preconnect |
| **INP** (Interaction to Next Paint) | responsiveness | **< 200 ms** | **replaced FID**; the **most-failed** CWV in 2026 (~43% of sites fail). Measures the *full* interaction lifecycle. Fix: break up long tasks, `scheduler.yield()`, defer non-critical JS, avoid heavy event handlers |
| **CLS** (Cumulative Layout Shift) | visual stability | **< 0.1** | reserve space for images/fonts/ads/embeds; `size` on fonts; no inserting content above existing content |

Measure **field** (CrUX / RUM) not just lab (Lighthouse). INP is where most 2026 effort goes (house opinion #2: every page has a budget).

## Newly-usable platform features (reach for the platform first)
- **Speculation Rules API** — declarative `prefetch`/`prerender` of likely-next pages for near-instant navigation; supports eagerness + document rules; **"prerender until script"** (Chrome 144, Jan 2026) prerenders HTML + subresources but pauses JS at the first blocking script. The modern replacement for hand-rolled hover-prefetch.
- **bfcache** (back/forward cache) — instant back/forward; don't break it (no `unload` handlers, mind `Cache-Control: no-store`). Test in DevTools.
- **`fetchpriority`** + **priority hints** — raise the LCP image, lower below-the-fold; pair with `loading="lazy"` and responsive `srcset`/`<picture>`.
- **Native `<dialog>`** + the **Popover API** (`popover` attribute) — accessible modals/menus/tooltips without a JS library (keyboard + focus handled). Prefer over a bespoke component.
- **View Transitions API** — see [`modern-css-2026.md`](modern-css-2026.md); gate on `prefers-reduced-motion`.
- **Web Components / custom elements** — framework-agnostic encapsulation for design-system primitives shared across stacks.

## Images, fonts, third-party
- Modern formats (AVIF/WebP), responsive `srcset`, `width`/`height` to prevent CLS, lazy-load below the fold (house opinion #7; the hook flags >500 KB rasters).
- Self-host or `preload` critical fonts; `font-display: swap`; subset.
- **Third-party scripts are debt** (house opinion #11): inventory, budget, lazy/`async`, consent-gate; they're the top INP + privacy cost. (See the `third-party-script-hygiene` skill.)

## Accessibility (WCAG 2.2 + the law)
WCAG 2.2 AA is the floor (house opinion #1). Note the **European Accessibility Act** (enforcement from June 2025) makes a11y a legal requirement for many consumer products in the EU — a business reason, not just a quality one. Use the ARIA Authoring Practices Guide (APG) patterns; honor `forced-colors` + `prefers-reduced-motion`. (See the `accessibility-review` skill.)

## Sources (retrieved 2026-05-28)
web.dev (CWV thresholds, INP), MDN (Speculation Rules API, Popover API, `<dialog>`, bfcache, `fetchpriority`), Chrome for Developers (speculation rules, prerender-until-script). Re-verify thresholds + Baseline on the Researcher sweep.
