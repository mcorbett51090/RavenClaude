# Keep the XML sitemap honest

**Status:** Absolute rule
**Domain:** Crawl & indexation
**Applies to:** `technical-seo-engineering`

---

## Why this exists

An XML sitemap is a **recommendation** to the search engine about which URLs you consider worth indexing. It is a trust signal: when it's accurate, the engine leans on it to discover and prioritize your pages. When it's full of redirects, 404s, `noindex` pages, non-canonical duplicates, or robots-disallowed URLs, the engine learns the file is unreliable and **discounts the whole sitemap** — including the good URLs. A dishonest sitemap is worse than no sitemap, because it wastes crawl budget and erodes trust.

The rule is simple: the sitemap lists **only URLs you would be happy to see indexed** — canonical, indexable, HTTP-200.

## How to apply

Every URL in the sitemap must be:

- **Canonical** (self-referencing canonical; not a duplicate that points elsewhere)
- **Indexable** (no `noindex`)
- **HTTP 200** (no redirects, no 404s/410s, no 5xx)
- **Not robots-disallowed**

**Do:**
- Generate the sitemap from the set of canonical, indexable, 200 URLs — programmatically, so it stays honest as the site changes.
- Reference it in `robots.txt` (`Sitemap:`) and submit it in Search Console.
- Split large sites into multiple sitemaps under a sitemap index; keep within the per-file limits.

**Don't:**
- Include redirected URLs (the new URL belongs there instead), 404s, `noindex`, non-canonical, or disallowed URLs.
- Hand-maintain a sitemap that drifts out of sync with the live site.
- Treat sitemap inclusion as a ranking lever — it aids discovery, not ranking.

## Edge cases / when the rule does NOT apply

- **News/video/image sitemaps** have their own required fields — follow the specific spec, but the honesty rule still holds.
- **Brand-new URLs** can be added to nudge discovery — but only once they return 200 and are canonical.

## See also

- [`../skills/audit-crawlability/SKILL.md`](../skills/audit-crawlability/SKILL.md) — the sitemap-validation step.
- [`./one-canonical-signal-set.md`](./one-canonical-signal-set.md) — sitemap inclusion as one of the five signals.

## Provenance

Codifies the house opinion "a sitemap is a recommendation, not a command — and a dishonest one is worse than none." The advisory hook flags a sitemap that references obviously non-200 URLs. Grounded in the sitemaps.org protocol and Google Search Central sitemap guidance, retrieved 2026-06-25 — re-verify before quoting.

---

_Last reviewed: 2026-06-25 by `claude`_
