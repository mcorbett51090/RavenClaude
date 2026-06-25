# Site-migration redirect map — <project / migration name>

> Fill this in **before** the cutover. A migration is the highest-risk SEO event — the
> redirect map, built from an authoritative inventory of the old surface, is what keeps
> the organic traffic. Traverse the drop-triage / signal trees and the migration skill first.

**Author:** <name> · **Date:** <YYYY-MM-DD> · **Migration type:** <replatform / domain change / URL restructure>

## 1. Scope & risk
- **What's moving:** <domain / CMS / URL structure / all of the above>
- **Cutover date:** <YYYY-MM-DD> · **Rollback plan:** <how we revert if coverage craters>
- **Highest-value URLs to protect:** <top organic landing pages / most-linked URLs>

## 2. Old-surface inventory (the union — built BEFORE cutover)
- [ ] Crawl of the live old site
- [ ] Search Console indexed/coverage URLs
- [ ] Old XML sitemap(s)
- [ ] Analytics top organic landing pages
- [ ] Server access log (what the bot actually fetches)
- **Total old URLs enumerated:** <N>

## 3. Redirect map (one 301 each, direct to final URL — no chains/loops)

| Old URL | New URL | Code | Notes |
|---|---|---|---|
| <old/url-1> | <new/url-1> | 301 | 1:1 match |
| <old/url-2> | <new/nearest-relevant> | 301 | no exact match → nearest relevant page |
| <old/retired> | (none) | 410 | deliberately retired, no equivalent |

- **Old URLs with no mapping (will 404):** <list — decide redirect vs 410>
- **Chains/loops checked + flattened:** <yes/no>
- **Bulk-to-homepage redirects:** <none — confirmed (they're soft 404s)>

## 4. On-page signals carried across
- [ ] Titles / meta · [ ] canonicals · [ ] hreflang · [ ] structured data · [ ] internal links
- **New sitemap:** built from new canonical 200 URLs only

## 5. Cutover & monitoring
- [ ] Redirects verified on staging
- [ ] New sitemap submitted in Search Console
- [ ] Change of Address filed (domain move)
- [ ] Daily watch: coverage + impressions + crawl-error/soft-404 reports + server log (first weeks)
- **Old redirects retained:** indefinitely (as long as old links exist)

## 6. Seams
- **Rendering/SSR implementation of the new site** → `frontend-engineering`.
- **Content/keyword changes bundled into the migration** → `marketing-operations`.
- **hreflang/locale routing on the new site** → `localization-i18n-engineering`.

---
_Plus the ravenclaude-core Structured Output block._
