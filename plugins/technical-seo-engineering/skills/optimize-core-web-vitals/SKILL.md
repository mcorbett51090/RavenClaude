---
name: optimize-core-web-vitals
description: "Diagnose and fix Core Web Vitals as a ranking input — start from FIELD data (CrUX / Search Console at the 75th percentile), not a Lighthouse lab score; find which of LCP/INP/CLS fails the threshold; and apply the fix at the metric's real cause. Defers deep runtime profiling to performance-engineering. Reach for this when CWV are failing or flagged in Search Console. Used by `core-web-vitals-engineer` (primary)."
---

# Skill: optimize-core-web-vitals

> **Invoked by:** `core-web-vitals-engineer` (primary).
>
> **When to invoke:** "our Core Web Vitals are failing"; "Search Console flags our URLs"; "Lighthouse is green but we're still flagged."
>
> **Output:** a field-data-first diagnosis of which Vital fails, at its real cause, with the highest-leverage fix — and the seam to `performance-engineering` for deep work.

## Procedure

1. **Read FIELD data first.** Page Experience ranks on ~28-day field data (CrUX) at the **75th percentile** of real users — use the Search Console Core Web Vitals report / CrUX, NOT a single Lighthouse run. Lab data is a diagnostic for *reproducing*, not the ranking input.
2. **Identify the failing metric.** **LCP** (loading; good ≤ the LCP threshold), **INP** (interactivity; replaced FID), **CLS** (visual stability). Fix the one(s) failing the threshold, not all three by reflex.
3. **Fix at the real cause:**
   - **LCP** — make the LCP element discoverable early (no lazy-load on the hero, `fetchpriority=high`, preload), cut server response time (TTFB), and avoid render-blocking resources.
   - **INP** — break up long tasks, reduce main-thread JS, defer non-critical work, yield to the main thread on interaction.
   - **CLS** — set explicit width/height (or `aspect-ratio`) on media, reserve space for late-injected/ad content, use `font-display` to avoid layout-shifting swaps.
4. **Re-measure against field data.** A lab improvement isn't a win until the field 75th-percentile crosses the threshold (and CrUX is a trailing 28-day window — give it time).
5. **Hand off deep work.** If the fix becomes bundle-splitting strategy, backend latency, or a runtime-profiling project, that's `performance-engineering` — this skill tunes CWV *as a ranking input*.

## Worked example

> User: "Lighthouse scores 95 but Search Console says our LCP is poor on mobile."

- Lab (desktop-ish, fast) ≠ field (real mobile users at p75). Trust the field signal.
- CrUX shows mobile LCP failing → inspect the LCP element: the hero image is `loading="lazy"` and not preloaded.
- Fix: remove lazy-load on the LCP image, add `<link rel="preload" as="image" fetchpriority="high">`, confirm TTFB is reasonable. Re-check the Search Console report over the next CrUX window.

## Guardrails

- Never declare CWV "fixed" from a green Lighthouse score — judge against field data at the 75th percentile. (See [`../../best-practices/measure-core-web-vitals-in-the-field.md`](../../best-practices/measure-core-web-vitals-in-the-field.md).)
- Never quote FID — it's been replaced by INP; using FID dates the analysis and the threshold.
- Re-verify the current CWV thresholds and metric set before quoting numbers — they change (see [`../../knowledge/technical-seo-engineering-reference-2026.md`](../../knowledge/technical-seo-engineering-reference-2026.md)).
- Deep runtime perf beyond the ranking input → `performance-engineering`.
