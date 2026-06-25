---
name: plan-site-migration-redirects
description: "Plan a site migration (replatform, domain change, or URL restructure) without losing organic traffic — build a complete old->new 301 redirect map (one hop, no chains/loops), diff a pre-migration crawl against the new structure, stage the cutover, and set up Search Console + log-file monitoring to catch drops early. Reach for this for any migration or URL-restructure. Used by `technical-seo-lead` (primary)."
---

# Skill: plan-site-migration-redirects

> **Invoked by:** `technical-seo-lead` (primary).
>
> **When to invoke:** "we're replatforming / changing domains / restructuring URLs"; "how do we migrate without tanking SEO?"
>
> **Output:** a complete old→new redirect map, a pre/post crawl-diff plan, a staged cutover, and the monitoring to catch a drop in days, not months.

## Procedure

1. **Enumerate the old surface FIRST.** Crawl the live old site + pull every URL from Search Console (indexed/coverage), the XML sitemaps, analytics (top organic landing pages), and the server log. This is the source-of-truth inventory you must not lose. Build it *before* the new site is final.
2. **Map every old URL to its single best new URL.** One **301** per old URL, pointing directly at the final destination — **no chains** (A→B→C) and **no loops**. Where there's no 1:1 match, map to the nearest relevant page (not the homepage en masse, which Google treats as a soft 404).
3. **Diff old-vs-new.** List old URLs with no mapping (will 404 — decide redirect vs intentional 410) and new URLs that should exist but don't. Preserve high-value backlinked URLs especially.
4. **Carry the on-page signals across.** Titles, canonicals, hreflang, structured data, and internal links move with the page; the new sitemap lists only new canonical 200 URLs.
5. **Stage the cutover.** Verify redirects on staging; cut over; immediately submit the new sitemap and (for domain changes) use the Search Console Change of Address tool; keep the old redirects live indefinitely.
6. **Monitor for the drop.** Watch Search Console coverage + impressions, the server log for crawl of old→new, and crawl-error/soft-404 reports daily for the first weeks. A migration's damage shows up fast if you're watching the right signal.

## Worked example

> User: "Moving `blog.example.com/2021/05/post-title` to `example.com/learn/post-title`."

```
# redirect map (one 301 each, direct to final URL — no chain)
old                                              -> new                              code
blog.example.com/2021/05/post-title              -> example.com/learn/post-title     301
blog.example.com/category/seo/                    -> example.com/learn/?topic=seo     301
blog.example.com/tag/legacy-only/                 -> (no equivalent) 410 Gone
```

Then: new sitemap submitted, Change of Address filed, daily coverage watch.

## Guardrails

- Never redirect everything to the homepage — bulk homepage redirects are treated as soft 404s and lose the signal. (See [`../../best-practices/redirect-map-before-you-migrate.md`](../../best-practices/redirect-map-before-you-migrate.md).)
- Never use 302 for a permanent move (use 301), and never build redirect chains — each hop bleeds equity and crawl budget. (See [`../../best-practices/redirects-are-301-and-one-hop.md`](../../best-practices/redirects-are-301-and-one-hop.md).)
- Never remove the old redirects after launch — keep them as long as old links exist.
- A migration is the highest-risk SEO event — treat it like a database migration: rollback plan, monitoring, no big-bang without verification.
