# Technical SEO audit — <site / property>

> A crawl/render/index-first audit. Isolate the layer before recommending a fix; ground
> every finding in evidence (robots.txt, rendered HTML, Search Console, server log).
> Traverse the crawl-vs-index decision tree first.

**Author:** <name> · **Date:** <YYYY-MM-DD> · **Property:** <domain> · **Search Console access:** <yes/no> · **Server log access:** <yes/no>

## 1. Crawl layer — can the bot reach what it should?
- **robots.txt:** <directives; over-blocking? CSS/JS blocked? sitemap referenced?>
- **HTTP status sweep:** <404s / 5xx / unexpected redirects>
- **Crawl-budget waste:** <parameters / faceted nav / infinite spaces seen in the log>
- **Reachability:** <orphan pages; depth>

## 2. Index layer — is the right version indexed?
- **Sitemap honesty:** <only canonical/indexable/200 URLs? offenders listed>
- **Canonicalization:** <declared vs Google's chosen canonical (URL Inspection); contradictions>
- **noindex / disallow consistency:** <any disallow + canonical/noindex contradictions?>
- **Coverage:** <Search Console excluded reasons + counts>

## 3. Render layer — is the content indexable?
- **Rendering strategy:** <CSR / SSR / SSG / dynamic>
- **Rendered HTML check:** <does it contain the content + internal links?>
- **Soft 404s:** <200-status "not found" pages — list>

## 4. Page experience & rich results (ranking inputs)
- **Core Web Vitals (FIELD, 75th pct):** LCP <…> · INP <…> · CLS <…> · <which fails>
- **Structured data:** <types present, validation status, mismatches with the visible page>

## 5. Internationalization (if applicable)
- **hreflang:** <present? reciprocal return tags? → engineering plumbing = localization-i18n-engineering>

## 6. Prioritized findings

| # | Layer | Finding | Severity | Fix | Owner/seam |
|---|---|---|---|---|---|
| 1 | crawl | <…> | high | <…> | crawl-indexation-engineer |
| 2 | index | <…> | med | <…> | technical-seo-lead |
| 3 | CWV | <…> | low | <…> | core-web-vitals-engineer / performance-engineering |

## 7. Seams handed off
- **Deep runtime perf** → `performance-engineering` · **render code** → `frontend-engineering` · **content/keywords** → `marketing-operations` · **i18n plumbing** → `localization-i18n-engineering`.

---
_Plus the ravenclaude-core Structured Output block._
