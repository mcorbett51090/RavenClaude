# technical-seo-engineering

> The **technical-SEO engineering** team for Claude Code — the engineering of *crawlability, indexation, and search-rendering*. Three specialists who answer the questions a generic web or frontend engineer can't safely answer: **how do we migrate without losing rankings?**, **canonicalize, noindex, or block these URLs?**, **why isn't our JS site getting indexed?**, **which Core Web Vital is failing the ranking bar?** This is **technical SEO, not content marketing.**

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## What it does

| You ask | It returns |
|---|---|
| "We're replatforming — how do we not tank SEO?" | A complete old→new 301 redirect map (one hop), a crawl-diff, a staged cutover, and Search Console + log monitoring |
| "Should these filtered/duplicate pages be canonicalized, noindexed, or blocked?" | The right signal per URL class from the decision tree — and a warning when two signals contradict (disallow + canonical can't even be read) |
| "Organic traffic dropped — why?" | A layer-isolating triage (crawl / render / index / rank) from Search Console coverage + the server log, before any fix |
| "Googlebot is crawling a million filter URLs" / "our SPA isn't indexed" | A crawl-budget containment plan, and a rendering diagnosis (CSR vs SSR/SSG/dynamic, soft-404 fix) |
| "Our Core Web Vitals are failing" / "add Product structured data" | A field-data-first LCP/INP/CLS fix at its real cause, or valid JSON-LD with the required properties + validation |

**Rules it never breaks:** *noindex ≠ robots-disallow*, *one consistent canonical signal set per URL*, *render what you want indexed*, and *build the redirect map before you migrate*.

## What's inside

- **3 agents** — `technical-seo-lead` (migration strategy, canonicalization policy, Search Console + log measurement, drop triage, routing), `crawl-indexation-engineer` (robots.txt, sitemaps, crawl budget, faceted-nav traps, JS rendering, soft-404s), `core-web-vitals-engineer` (LCP/INP/CLS as ranking inputs, structured data / rich results).
- **5 skills** — `audit-crawlability`, `plan-site-migration-redirects`, `implement-structured-data`, `diagnose-indexation-drop`, `optimize-core-web-vitals`.
- **2 knowledge files** — a decision-tree bank (crawl-vs-index drop triage + noindex-vs-disallow-vs-canonical, as Mermaid trees) and a dated 2026 reference (CWV thresholds, Googlebot rendering behavior, tooling — re-verify before quoting).
- **3 templates** — site-migration redirect map, technical-SEO audit report, structured-data spec.
- **9 best-practice docs** — 7 named rules + 2 companions (noindex-vs-disallow, one-canonical-signal-set, never-block-what-you-canonicalize, render-what-you-want-indexed, keep-the-sitemap-honest, redirect-map-before-you-migrate, redirects-are-301-and-one-hop, measure-CWV-in-the-field, structured-data-matches-the-page).
- **3 commands** — `/audit-technical-seo`, `/plan-migration`, `/diagnose-traffic-drop`.
- **1 advisory hook** — `flag-seo-smells.sh` (disallow + noindex/canonical contradiction, redirect chain / 302-for-permanent, soft-404, FID-instead-of-INP).

## How it seams with adjacent plugins

```
technical-seo-engineering    ->  the engineering of crawl / index / render (robots, sitemaps, canonical, rendering, CWV, migrations, schema)
performance-engineering      ->  deep runtime/app performance beyond the CWV ranking inputs
frontend-engineering         ->  the render-implementation code (SSR wiring, hydration, components)
marketing-operations         ->  content strategy, keyword research, link/PR campaigns
localization-i18n-engineering ->  hreflang / locale-routing engineering plumbing
```

This is **technical** SEO — the crawl/index/render engineering — not content or keyword marketing.

## Tooling stance

Google Search Console + the server access log are the ground truth for what the bot did; CrUX / the Search Console CWV report (field data, 75th percentile) is the ranking input, with Lighthouse as a diagnostic. JSON-LD is the structured-data format. All numeric thresholds and engine behaviors carry retrieval dates — re-verify before pinning in a client deliverable. See [`knowledge/technical-seo-engineering-reference-2026.md`](knowledge/technical-seo-engineering-reference-2026.md).

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install technical-seo-engineering@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
