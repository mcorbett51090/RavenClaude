---
name: audit-crawlability
description: "Audit what a search engine can and can't crawl and index — check robots.txt for over-blocking, verify the XML sitemap lists only canonical/indexable/200 URLs, test internal-link reachability, and find crawl-budget waste (URL parameters, faceted nav, infinite spaces). Reach for this when asked to audit crawlability/indexability or when a drop points at the crawl layer. Used by `crawl-indexation-engineer` (primary)."
---

# Skill: audit-crawlability

> **Invoked by:** `crawl-indexation-engineer` (primary). Also consulted by `technical-seo-lead` when a traffic-drop triage isolates a crawl problem.
>
> **When to invoke:** "audit our robots.txt / sitemap / crawlability"; "is the bot reaching our money pages?"; "we're wasting crawl budget."
>
> **Output:** a crawlability audit — robots.txt directives checked for over-blocking, an honest sitemap, internal-link reachability, and named crawl-budget waste, each with a fix.

## Procedure

1. **Read robots.txt for over-blocking.** Confirm no `Disallow` rule blocks pages you want indexed (and that you are NOT trying to deindex via `Disallow` — that strands the `noindex`). Confirm the sitemap is referenced. Check that CSS/JS needed to render are not blocked.
2. **Validate the XML sitemap.** Every URL must be: canonical, indexable (no `noindex`), HTTP 200 (no redirects/404s), and not robots-disallowed. List only URLs you *want* indexed. Check it's referenced in robots.txt and submitted in Search Console.
3. **Test reachability (internal linking).** Run a crawl from the homepage; flag orphan pages (in the sitemap but not internally linked) and pages buried too deep. The bot follows links — unlinked is effectively invisible.
4. **Find crawl-budget waste.** From the server log and a crawl, identify URL parameters, faceted-nav combinations, session IDs, calendar/infinite spaces, and duplicate paths the bot is fetching. Decide per class: index / canonicalize / disallow (see the decision tree).
5. **Confirm signal consistency.** No URL should be both disallowed *and* carry a canonical/noindex tag — the engine can't read a tag on a blocked page (the hook flags this).

## Worked example

> User: "Googlebot is hammering `/search?color=&size=&sort=` URLs and our products aren't all indexed."

- The log shows the crawler spending budget on faceted permutations → a combinatorial trap.
- These facets have no unique search demand → **canonicalize** refinements to the base category and **disallow** the sort/pagination-only parameters; do NOT do both on the same URL.

```
# robots.txt — stop crawling pure sort/session permutations (no canonical tag on these)
User-agent: *
Disallow: /*?*sort=
Disallow: /*?*sessionid=

Sitemap: https://example.com/sitemap.xml
```

```html
<!-- on an indexable color refinement that should consolidate to the base category -->
<link rel="canonical" href="https://example.com/shoes/" />
```

Then confirm the product pages are internally linked and present in the sitemap.

## Guardrails

- Never `Disallow` a URL in robots.txt to remove it from the index — it can still rank URL-only, and any `noindex` on it is never read. To deindex: allow crawl + serve `noindex`. (See [`../../best-practices/noindex-removes-disallow-hides.md`](../../best-practices/noindex-removes-disallow-hides.md).)
- Never list redirects, 404s, non-canonical, or `noindex` URLs in the sitemap. (See [`../../best-practices/keep-the-sitemap-honest.md`](../../best-practices/keep-the-sitemap-honest.md).)
- Never block the CSS/JS the page needs to render — the engine then sees an unstyled/empty page.
