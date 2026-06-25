# `noindex` removes a page; `robots.txt Disallow` only stops crawling — never confuse them

**Status:** Absolute rule
**Domain:** Crawl & indexation control
**Applies to:** `technical-seo-engineering`

---

## Why this exists

These two directives are the most-confused pair in technical SEO, and confusing them produces the **opposite** of the intended effect:

- **`robots.txt Disallow`** controls **crawling**. A disallowed URL is never fetched — so the engine never reads anything *on* the page, including a `noindex` tag. The URL can **still appear in search results** (URL-only, no snippet) because the engine knows it exists from links pointing at it. People reach for `Disallow` to "hide" a page; it does not deindex and it is not a privacy control (robots.txt is public).
- **`noindex`** (a meta tag or `X-Robots-Tag` header) controls **indexing** and **removes** the page from the index — but **only if the page is crawlable**, because the engine has to fetch the page to see the tag.

The fatal combination is `Disallow` **plus** `noindex` on the same URL: the bot can't crawl it, so it never sees the `noindex`, so the page is **not** deindexed and can keep ranking URL-only.

## How to apply

```
# DELIST a page from the index — ALLOW the crawl, serve noindex:
#   robots.txt: (no Disallow for this path)
#   on the page: <meta name="robots" content="noindex">
#   or header:   X-Robots-Tag: noindex

# SAVE CRAWL BUDGET on noise you don't need indexed — Disallow, accept it may rank URL-only:
#   robots.txt: Disallow: /*?*sessionid=
```

**Do:**
- To remove a page from the index: allow the crawl and serve `noindex` (then optionally `Disallow` later, *after* it's dropped).
- Use `Disallow` to stop wasted crawling of noise you don't need indexed.
- Use the URL Removals tool for an urgent temporary hide.

**Don't:**
- `Disallow` a page expecting it to leave the index — it can still rank URL-only.
- Put `noindex` on a URL you also `Disallow` — the tag is never read.
- Treat robots.txt as a privacy/security control — it's public and advisory.

## Edge cases / when the rule does NOT apply

- **Truly private content** belongs behind authentication, not either directive.
- **An already-indexed page you want gone fast:** serve `noindex`, keep it crawlable until it drops out, *then* you may `Disallow` to save budget.

## See also

- [`../knowledge/technical-seo-engineering-decision-trees.md`](../knowledge/technical-seo-engineering-decision-trees.md) — the noindex-vs-disallow-vs-canonical tree.
- [`./never-block-a-page-you-also-canonicalize.md`](./never-block-a-page-you-also-canonicalize.md) — the sibling own-goal.
- [`../skills/audit-crawlability/SKILL.md`](../skills/audit-crawlability/SKILL.md).

## Provenance

Codifies the team house opinion "if you block it in robots.txt, you can't also control its indexing." The advisory hook [`../hooks/flag-seo-smells.sh`](../hooks/flag-seo-smells.sh) flags `noindex` on a path that is also `Disallow`ed. Grounded in Google Search Central robots/noindex documentation, retrieved 2026-06-25 — re-verify before quoting.

---

_Last reviewed: 2026-06-25 by `claude`_
