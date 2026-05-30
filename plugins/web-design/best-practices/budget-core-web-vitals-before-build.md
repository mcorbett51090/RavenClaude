# Declare a Core Web Vitals budget before development starts

**Status:** Absolute rule — every page declares its weight + LCP / CLS / INP targets before any code is written.

**Domain:** Performance / Core Web Vitals

**Applies to:** `web-design`

---

## Why this exists

Optimizations without measurement are theater, and "we'll make it fast later" is how a marketing page ships at 1.5 MB+ with a 4-second LCP. A budget set up front turns performance into a contract that can be defended in CI rather than a subjective argument at launch. The field data is the reality check: **INP is the most-failed 2026 metric (~43% of sites fail)** because it measures the full interaction lifecycle, not a single first input. A budget makes that failure visible before it ships, not after CrUX reports it in production.

## How to apply

Set the three 2026 thresholds as field targets (CrUX / RUM at p75, not just a Lighthouse lab score), then enforce the asset-level corollaries that move them.

```
# Per-page performance budget (2026 thresholds — measure in the FIELD at p75)
LCP  < 2.5 s    # preload + fetchpriority="high" on the hero image; correct dimensions
INP  < 200 ms   # break up long tasks, scheduler.yield(), defer non-critical JS
CLS  < 0.1      # reserve space: width/height on images, size-adjust fonts, no late inserts

# Asset corollaries
JS bundle  <= 100 KB compressed (marketing)   # > 250 KB on a content site is a smell
Hero image <= 500 KB                           # AVIF/WebP, responsive srcset
Third-party scripts <= 5 total, <= 2 in the critical path
```

**Do:**
- Treat CrUX / RUM field data at p75 as the authoritative score; Lighthouse is a diagnostic forecast.
- Put `fetchpriority="high"` + `preload` on the LCP image — and never `loading="lazy"` on it.
- Give every `<img>` explicit `width`/`height` and use `font-display: optional` for non-critical display fonts to avoid CLS.

**Don't:**
- Cite "Lighthouse 100" as evidence of speed with no field data.
- Add a service worker "for performance" with no measured benefit.
- Animate `top`/`left`/`width`/`height` — use `transform` + `opacity`.

## Edge cases / when the rule does NOT apply

- **CLS > 0.1 ships only with a written justification** (house opinion #7) — e.g., a user-initiated expand that the user expects.
- **Internal tools / authenticated dashboards** can relax the marketing-site weight budget, but still declare *a* budget — "no budget" is the anti-pattern, not "a different number."
- **No field data yet (pre-launch)** — use lab (Lighthouse / WebPageTest) as an explicit fallback and note it; replace with CrUX/RUM once traffic exists.

## See also

- [`../knowledge/web-platform-capabilities-2026.md`](../knowledge/web-platform-capabilities-2026.md) — the 2026 CWV thresholds, INP-as-most-failed, `fetchpriority`, Speculation Rules, bfcache
- [`../agents/performance-engineer.md`](../agents/performance-engineer.md) — the agent that owns the budget
- [`./reach-for-semantic-html-before-aria.md`](./reach-for-semantic-html-before-aria.md)

## Provenance

Distilled from the `web-design` constitution house opinions #2, #7, and #11, the `performance-engineer` agent's CWV thresholds + fix-by-symptom map + anti-pattern list, and the Core Web Vitals table in `web-platform-capabilities-2026.md` (web.dev / Chrome for Developers, retrieved 2026-05-28).

---

_Last reviewed: 2026-05-30 by `claude`_
