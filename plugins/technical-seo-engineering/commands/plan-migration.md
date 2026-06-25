---
description: "Plan a site migration without losing rankings: enumerate the old surface, build a complete old->new 301 redirect map (one hop), diff old vs new, stage the cutover, and set up Search Console + log monitoring."
argument-hint: "[migration type + old structure + new structure + cutover date]"
---

You are running `/technical-seo-engineering:plan-migration`. Use `technical-seo-lead` + the `plan-site-migration-redirects` skill. A migration is the highest-risk SEO event — treat it like a database migration.

## Steps
1. Scope + risk: what's moving, cutover date, rollback plan, highest-value URLs to protect.
2. **Enumerate the old surface FIRST** — union of a live crawl, Search Console coverage, sitemaps, analytics top organic pages, and the server log.
3. Map every old URL to its single best new URL — one **301**, direct to the final URL, no chains/loops, never bulk-to-homepage; decide redirect vs `410` for no-equivalents.
4. Carry on-page signals across (titles, canonicals, hreflang, structured data, internal links); build the new sitemap from new canonical 200 URLs.
5. Stage + monitor: verify on staging, submit the new sitemap, file Change of Address (domain move), watch coverage/impressions + log daily for the first weeks; keep old redirects indefinitely.
6. Emit using `templates/site-migration-redirect-map.md` + the Structured Output block. Seams: render implementation → frontend-engineering; i18n routing → localization-i18n-engineering.
