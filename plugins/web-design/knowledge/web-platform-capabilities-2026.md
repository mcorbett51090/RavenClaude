# Web platform capabilities & Core Web Vitals (2026)

**Last reviewed:** 2026-05-28 · **Confidence:** medium-high — the web platform ships continuously; this is the dated freshness anchor for the web-design plugin. Re-verify thresholds + Baseline on the Researcher sweep. Sources: web.dev / MDN / Chrome for Developers (retrieval-dated).
**Owner:** `performance-engineer` + `web-architect` (complements the `core-web-vitals-tuning` + `third-party-script-hygiene` skills).

## Core Web Vitals (2026 thresholds)
| Metric | Measures | "Good" | Notes |
|---|---|---|---|
| **LCP** (Largest Contentful Paint) | loading | **< 2.5 s** | optimize the hero image/font; `fetchpriority="high"` on the LCP image; preconnect |
| **INP** (Interaction to Next Paint) | responsiveness | **< 200 ms** | **replaced FID**. Per the HTTP Archive Web Almanac 2025, INP's mobile "good" rate is **77%** — LCP (62% good) is the most-failed CWV on mobile *overall*; INP is the weakest metric specifically on JS-heavy/high-traffic sites (top-1,000 mobile sites: 63% good). Measures the *full* interaction lifecycle. Fix: break up long tasks, `scheduler.yield()` where supported (guard for Safari, which doesn't ship it — fall back to `setTimeout`), defer non-critical JS, avoid heavy event handlers |
| **CLS** (Cumulative Layout Shift) | visual stability | **< 0.1** | reserve space for images/fonts/ads/embeds; `size` on fonts; no inserting content above existing content |

Measure **field** (CrUX / RUM) not just lab (Lighthouse). Web Almanac 2025 mobile "good" rates: LCP 62%, INP 77%, CLS 81% — LCP is the metric most sites fail; watch INP closely on interactive/JS-heavy pages (house opinion #2: every page has a budget).

## Newly-usable platform features (reach for the platform first)
- **Speculation Rules API** — declarative `prefetch`/`prerender` of likely-next pages for near-instant navigation; supports eagerness + document rules; **"prerender until script"** (Chrome 144, Jan 2026) prerenders HTML + subresources but pauses JS at the first blocking script. The modern replacement for hand-rolled hover-prefetch.
- **bfcache** (back/forward cache) — instant back/forward; don't break it (no `unload` handlers, mind `Cache-Control: no-store`). Test in DevTools.
- **`fetchpriority`** + **priority hints** — raise the LCP image, lower below-the-fold; pair with `loading="lazy"` and responsive `srcset`/`<picture>`.
- **Native `<dialog>`** (via `.showModal()`) + the **Popover API** (`popover` attribute) — accessible modals/tooltips/toasts without a JS library. These are **not interchangeable**: `<dialog>.showModal()` is the only one that traps focus and makes the rest of the page inert; the Popover API is **always non-modal** (per MDN) — light-dismiss + Esc-returns-focus, but no focus trap and no `role`/keyboard menu semantics. A menu still needs the APG menu pattern or an accessible primitive (Radix / React Aria / Fluent v9). Prefer these over a bespoke component for what they actually cover.
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
