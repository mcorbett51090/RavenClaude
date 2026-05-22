---
name: seo-technical-audit
description: Technical SEO sweep — crawlability, indexability, schema markup, sitemaps, OG / Twitter Card metadata, hreflang, structured data. Used by `web-architect` (primary, technical) + `content-strategist` (content-SEO).
---

# Skill: seo-technical-audit

**Purpose:** Technical SEO sweep — crawlability, indexability, structured data, social-share metadata, internationalization. Used by `web-architect` (technical) + `content-strategist` (content-side).

## When to use

- Pre-launch verification
- Search ranking regression
- Migration / re-platform readiness
- Annual / quarterly review cycle
- New section / language launch

## The 7 areas

### 1. Crawlability

- `robots.txt` present at root, valid syntax
- `robots.txt` doesn't accidentally block `/` or critical paths
- `sitemap.xml` referenced from `robots.txt`
- Sitemap accurate — every URL returns 200, no 404s in sitemap
- `sitemap.xml` includes `<lastmod>` for cache-aware crawlers
- No infinite-redirect loops; no 30x chains > 1 hop
- No `<meta name="robots" content="noindex">` on key pages (the hook catches this for HTML files)

### 2. Indexability

- Canonical URLs declared on every page (or canonicalized at the server / CDN level via 301)
- Trailing-slash decision made + enforced (one or the other, consistently)
- Case-sensitivity: lowercase URLs enforced; mixed-case redirect-or-404
- No duplicate content across URLs (UTM-only variants, faceted-nav variants)
- Pagination uses `rel="next"` / `rel="prev"` (deprecated by Google but still respected by some crawlers; consistent UX matters)
- Hash-based URLs only for in-page anchors; never for primary navigation

### 3. URL structure + IA

- Short, readable URLs (`/blog/topic` > `/post.php?id=42`)
- URLs reflect IA (a page at `/blog/foo` is a child of `/blog`)
- Avoid stop-words / dates in primary URLs unless intentional
- Locale prefix consistent (`/en/`, `/de/`, etc.) if multi-language

### 4. Structured data (Schema.org)

- Schema.org JSON-LD in `<head>` (not Microdata or RDFa — JSON-LD is the preferred format)
- Validates against schema.org and Google Rich Results Test
- Match the page's actual content (no spam-typing)
- Common types used appropriately:
  - `Organization` (homepage, about)
  - `WebSite` (homepage with sitelinks search box)
  - `BreadcrumbList` (every page below root)
  - `Article` / `BlogPosting` (blog content)
  - `Product` (e-commerce)
  - `FAQPage` (FAQ content; sparingly — Google has narrowed eligibility)
  - `LocalBusiness` (locations)
  - `Person` (author bios)

### 5. Social share (OG + Twitter Card)

- `<meta property="og:title">`, `og:description`, `og:image`, `og:url`, `og:type`
- `<meta name="twitter:card" content="summary_large_image">`, `twitter:title`, `twitter:description`, `twitter:image`
- OG image: 1200×630 minimum, < 5 MB, branded consistently
- Twitter image: same as OG image is fine if it fits
- Validate via Twitter Card Validator + Facebook Sharing Debugger

### 6. Internationalization

- `<html lang="...">` on every page (locale code, e.g., `en-US`)
- `hreflang` tags on multilingual pages, including self-reference
- `hreflang` is bidirectional (page A → page B; page B → page A)
- `x-default` declared
- Language switcher in nav (not just IP-based redirect)

### 7. Performance × SEO

- Core Web Vitals pass (LCP / CLS / INP) — see [`./core-web-vitals-tuning.md`](./core-web-vitals-tuning.md)
- HTTPS everywhere
- Mobile-friendly (Google's mobile-friendliness test passes)
- Page-experience signals on (CWV is the load-bearing one)

## Output

| Area | Score (✅ / ⚠️ / 🔴) | Findings | Severity (P0 / P1 / P2) |
|---|---|---|---|

Plus:
- **Top 5 fixes** ranked by leverage
- **Index-coverage report** (Google Search Console pull: indexed / excluded / errors)
- **Recommendation:** clean / targeted-fixes / comprehensive-remediation

## Severity guide

- **P0** — issue blocks indexability of critical pages (robots disallow, noindex, broken canonical)
- **P1** — issue degrades ranking signal (missing structured data on monetizable pages, broken hreflang)
- **P2** — improvable; not currently hurting ranking

## Tools

- **Google Search Console** — index coverage, performance reports, sitemaps, manual actions
- **Google Rich Results Test** — structured-data validation
- **Schema.org validator** — schema.org-side validation
- **Twitter Card Validator** + **Facebook Sharing Debugger** — social share
- **Screaming Frog** / **Sitebulb** — crawler simulation
- **Ahrefs / Semrush / Moz** — for backlink + keyword data (out of scope for technical audit; content-side)

## Anti-patterns the audit catches

- `robots.txt` accidentally `Disallow: /` (kills indexing)
- Canonical URL pointing to itself + a different page (loop)
- Trailing-slash inconsistency (Google sees `/about` and `/about/` as separate pages)
- OG image missing → bare URL on social share
- `lang` attribute missing or wrong on `<html>`
- `hreflang` declared one-way (A → B without B → A)
- FAQ schema used on pages without actual FAQ structure
- Structured data that doesn't match visible content (spam pattern; risks manual action)
- Multiple H1s per page (technically allowed in HTML5; still confusing for some crawlers)
- Duplicate title tags across pages

## See also

- Template: [`../templates/seo-audit-report.md`](../templates/seo-audit-report.md)
- Skill: [`./core-web-vitals-tuning.md`](./core-web-vitals-tuning.md)
- Agent: [`../agents/web-architect.md`](../agents/web-architect.md)
- Agent: [`../agents/content-strategist.md`](../agents/content-strategist.md)
