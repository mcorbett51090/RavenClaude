---
description: "Run a crawl/render/index-first technical-SEO audit: robots.txt, sitemap honesty, crawl-budget waste, canonicalization, rendering/soft-404s, Core Web Vitals (field), and structured data — grounded in evidence."
argument-hint: "[site URL + what you have access to: Search Console / server log / staging]"
---

You are running `/technical-seo-engineering:audit-technical-seo`. Use `crawl-indexation-engineer` (lead) with `core-web-vitals-engineer` for the page-experience section, coordinated by `technical-seo-lead`.

## Steps
1. Traverse the crawl-vs-index tree in `knowledge/technical-seo-engineering-decision-trees.md` — isolate by layer, don't keyword-match symptoms.
2. **Crawl layer:** robots.txt over-blocking / blocked CSS-JS, HTTP-status sweep, crawl-budget waste (parameters, faceted nav, infinite spaces from the log), reachability/orphans.
3. **Index layer:** sitemap honesty (canonical/indexable/200 only), declared vs chosen canonical, noindex/disallow contradictions (the `audit-crawlability` skill).
4. **Render layer:** rendering strategy, rendered-HTML content check, soft-404s.
5. **Page experience:** Core Web Vitals from FIELD data at the 75th percentile (not Lighthouse alone) + structured-data validity/match (`optimize-core-web-vitals`, `implement-structured-data`).
6. Emit using `templates/technical-seo-audit-report.md` with prioritized findings + the Structured Output block. Hand off seams: deep perf → performance-engineering; render code → frontend-engineering; content → marketing-operations.
