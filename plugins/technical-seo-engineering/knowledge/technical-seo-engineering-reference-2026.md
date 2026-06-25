# Technical SEO Engineering — 2026 Reference

> **Last reviewed:** 2026-06-25 · **Confidence:** Medium — this file collects the **volatile** facts of technical SEO (numeric thresholds, search-engine rendering behavior, tool names). All of it moves. **Re-verify any specific number, behavior, or tool name against the primary source before quoting it in a client deliverable.** The decision trees in [`technical-seo-engineering-decision-trees.md`](technical-seo-engineering-decision-trees.md) carry the durable principles; this file carries the perishable specifics.

---

## Core Web Vitals thresholds (re-verify before quoting)

Page Experience ranks on **field data at the 75th percentile** of real users over a ~28-day window (CrUX), not a single lab run. The three metrics and their "good" thresholds **as understood at this review date** — confirm against [web.dev/vitals](https://web.dev/articles/vitals) and Google Search Central before quoting:

| Metric | Measures | "Good" (75th pct) | Notes |
|---|---|---|---|
| **LCP** (Largest Contentful Paint) | Loading | ≤ 2.5 s | Time to render the largest in-viewport element |
| **INP** (Interaction to Next Paint) | Interactivity | ≤ 200 ms | **Replaced FID in March 2024** — quoting FID is now wrong |
| **CLS** (Cumulative Layout Shift) | Visual stability | ≤ 0.1 | Unitless; lower is better |

> `[unverified — volatile]` The exact threshold values and even *which* metrics count have changed before (FID→INP). Treat the table as a prompt to go check the current spec, not as a citation.

---

## Googlebot crawling & rendering behavior (re-verify)

- **Two-wave / deferred rendering.** Googlebot crawls the HTML, then renders JavaScript in a separate, resource-budgeted pass (a headless evergreen Chromium). Content that only appears after client-side hydration may be indexed late or not at all — **verify the rendered HTML**, not view-source. `[unverified — behavior evolves]`
- **Rendering strategy preference for indexability:** SSR / SSG / pre-rendering put the content in the initial response (most reliable). **Dynamic rendering** (serving rendered HTML to bots) is a workaround/stopgap, not a long-term recommendation. CSR-only is the riskiest.
- **Soft 404:** an HTTP 200 response whose body says "not found"/"no results." Return a real **404 or 410** so the engine deindexes it correctly.
- **`noindex` requires crawlability.** A page blocked by `robots.txt` is never fetched, so a `noindex` on it is never seen — the URL can still rank URL-only. To deindex: allow crawl + serve `noindex` (meta or `X-Robots-Tag`).
- **`rel=next/prev` for pagination is deprecated** (Google announced it no longer uses it). Each paginated page should self-canonicalize; ensure linked items are reachable.
- **Mobile-first indexing** is the default — the mobile rendering is what's indexed.

---

## Robots / sitemap mechanics (durable, but confirm syntax)

- **robots.txt** controls crawling only; it is public and not a security/privacy control. Don't block the CSS/JS needed to render.
- **XML sitemap** lists only canonical, indexable, HTTP-200 URLs you want indexed — no redirects, 404s, `noindex`, or disallowed URLs. Reference it in robots.txt and submit in Search Console. Limits (per file) are large but bounded; split and use a sitemap index for big sites. `[unverified — confirm current limits]`
- **hreflang** (return-tag reciprocity required) for international/locale targeting — the engineering of the plumbing is a `localization-i18n-engineering` seam; the SEO *intent* and validation live here.

---

## Structured data (re-verify the supported-type catalog)

- **JSON-LD** is Google's recommended format. Markup must match the **visible** page.
- Valid markup confers **eligibility**, not a guaranteed rich result — the engine decides.
- The catalog of **supported rich-result types** and their **required vs recommended** properties changes; confirm against [Google's structured-data docs](https://developers.google.com/search/docs/appearance/structured-data) and validate with the **Rich Results Test** + the **Schema Markup Validator**. `[unverified — catalog changes]`

---

## Measurement & tooling (names move; verify)

| Use | Tool(s) at this review date |
|---|---|
| What the bot crawled/indexed; coverage; URL Inspection; CWV report; Change of Address | **Google Search Console** (ground truth) |
| Field CWV data | **CrUX** (Chrome UX Report) / Search Console CWV report |
| Lab CWV diagnosis | **Lighthouse** / PageSpeed Insights (diagnostic, not the ranking input) |
| Crawl simulation / site audit | Screaming Frog, Sitebulb, and similar crawlers `[unverified — vendor]` |
| Log-file analysis | log analyzers / the raw server access log (true bot behavior) |
| Structured-data validation | Rich Results Test, Schema Markup Validator |

> Bing Webmaster Tools and IndexNow are the equivalent surfaces for Bing — confirm before advising a Bing-specific workflow. `[unverified — vendor]`

---

## Provenance

- Google Search Central documentation (crawling, rendering, robots, sitemaps, structured data, migrations).
- web.dev / Chrome team Core Web Vitals documentation (thresholds, the FID→INP change).
- schema.org for the vocabulary; Google's rich-result catalog for eligibility.

> Everything numeric or behavioral here is `[unverified — volatile]` until re-confirmed against the primary source at use-time. Cite the retrieval date when you quote it.

---

_Last reviewed: 2026-06-25 by `claude`_
