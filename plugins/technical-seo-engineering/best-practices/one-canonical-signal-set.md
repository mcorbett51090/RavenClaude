# Keep one consistent canonicalization signal set per URL

**Status:** Absolute rule
**Domain:** Crawl & indexation control
**Applies to:** `technical-seo-engineering`

---

## Why this exists

A single URL emits **five** indexing signals: `rel=canonical`, the `robots` meta / `X-Robots-Tag` (`index`/`noindex`), the `robots.txt` rule (crawlable / disallowed), the redirect status (200 vs 3xx), and its presence in the XML sitemap. The engine reconciles all of them — and when they **contradict**, the result is unpredictable: the engine picks a canonical you didn't intend, ignores a directive it can't read, or quietly drops the page. Most "why is Google indexing the wrong version?" bugs are a contradictory signal set, not an algorithm mystery.

The signals must tell **one consistent story** about each URL: *index this one, consolidate these to it, don't index those, and the sitemap lists only the keepers.*

## How to apply

For every URL, confirm the five signals agree:

| Signal | For a page you WANT indexed | For a duplicate to consolidate | For a page to deindex |
|---|---|---|---|
| `rel=canonical` | self | → the chosen canonical | self (or the canonical) |
| robots meta | `index` (default) | `index` | `noindex` |
| robots.txt | crawlable | crawlable | **crawlable** (so noindex is read) |
| status | 200 | 200 | 200 |
| in sitemap | yes | no | no |

**Do:**
- Make a canonical-target URL self-canonical, indexable, 200, and in the sitemap.
- Make a consolidated duplicate canonical *to* the target — and keep it crawlable so the tag is read.
- Audit the whole set together; a signal is only correct relative to the others.

**Don't:**
- `Disallow` a URL that also carries a `canonical` or `noindex` (the tag is never read).
- `noindex` a page you also canonicalize *to* (you're telling the engine to drop your chosen version).
- List a non-canonical, `noindex`, redirected, or disallowed URL in the sitemap.

## Edge cases / when the rule does NOT apply

- **Cross-domain canonicals** (syndication) are legitimate — both URLs stay crawlable.
- **Paginated series** self-canonicalize per page (don't canonical page 2..N to page 1); that's consistent, not contradictory.

## See also

- [`./noindex-removes-disallow-hides.md`](./noindex-removes-disallow-hides.md)
- [`./never-block-a-page-you-also-canonicalize.md`](./never-block-a-page-you-also-canonicalize.md)
- [`../knowledge/technical-seo-engineering-decision-trees.md`](../knowledge/technical-seo-engineering-decision-trees.md)

## Provenance

Codifies the house opinion "one canonical signal set per URL." The advisory hook flags the classic contradiction (disallow + canonical/noindex on one path). Grounded in Google Search Central canonicalization documentation, retrieved 2026-06-25 — re-verify before quoting.

---

_Last reviewed: 2026-06-25 by `claude`_
