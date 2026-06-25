# Technical-SEO-engineering — best-practice docs

Named, citable rules for the `technical-seo-engineering` plugin's three agents. Each file is **one rule**, grounded in the plugin's knowledge bank and the agents' house opinions — read, applied, and cited as a whole.

These complement, and do not restate, the cross-cutting house opinions in the team constitution ([`../CLAUDE.md`](../CLAUDE.md)) or the automated smell checks in the advisory hook. They take one opinion each and make it a standalone, exception-documented rule.

---

## Index

_7 rules. Each file is one named, citable rule; read and apply it whole._

| Doc | Status | Use when |
|---|---|---|
| [`noindex-removes-disallow-hides.md`](./noindex-removes-disallow-hides.md) | Absolute rule | Deciding how to keep a page out of the index — `noindex` (crawlable) removes; `robots.txt Disallow` only stops crawling and the URL can still rank. Never confuse them. |
| [`one-canonical-signal-set.md`](./one-canonical-signal-set.md) | Absolute rule | Setting canonical / noindex / robots / redirects / sitemap on any URL — they must all agree; contradictory signals (disallow + canonical) are an own-goal. |
| [`never-block-a-page-you-also-canonicalize.md`](./never-block-a-page-you-also-canonicalize.md) | Absolute rule | Containing a faceted-nav / parameter trap — don't `Disallow` a URL you also `canonical`-tag; the engine can't read the tag on a blocked page. |
| [`render-what-you-want-indexed.md`](./render-what-you-want-indexed.md) | Absolute rule | Any JS-heavy / SPA site — verify the *rendered* HTML contains the content and links; CSR-only is a rendering gamble. Return a real 404 for soft 404s. |
| [`keep-the-sitemap-honest.md`](./keep-the-sitemap-honest.md) | Absolute rule | Generating or auditing an XML sitemap — list only canonical, indexable, 200-status URLs you want indexed; a dirty sitemap erodes trust in the whole file. |
| [`redirect-map-before-you-migrate.md`](./redirect-map-before-you-migrate.md) | Absolute rule | Any migration / replatform / URL restructure — enumerate the old surface and map every old URL to its best new URL *before* cutover; a migration is the highest-risk SEO event. |
| [`redirects-are-301-and-one-hop.md`](./redirects-are-301-and-one-hop.md) | Pattern (strong default; deviate only with a written reason) | Writing any redirect — permanent moves are 301, direct to the final URL, no chains/loops, never en masse to the homepage. |

---

## Companion files (not standalone rules, cited often)

- [`measure-core-web-vitals-in-the-field.md`](./measure-core-web-vitals-in-the-field.md) — judge CWV against field data at the 75th percentile, not a Lighthouse lab score.
- [`structured-data-matches-the-page.md`](./structured-data-matches-the-page.md) — structured data must reflect the visible page; valid markup is eligibility, not a guaranteed rich result.

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — technical-seo-engineering team constitution (house opinions, anti-patterns, Output Contracts, smell hook).
- [`../knowledge/technical-seo-engineering-decision-trees.md`](../knowledge/technical-seo-engineering-decision-trees.md) — the crawl-vs-index and noindex-vs-disallow-vs-canonical trees these rules lean on.
- [`../knowledge/technical-seo-engineering-reference-2026.md`](../knowledge/technical-seo-engineering-reference-2026.md) — the dated 2026 reference (CWV thresholds, Googlebot behavior, tooling).
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs and the `_TEMPLATE.md` these follow.
