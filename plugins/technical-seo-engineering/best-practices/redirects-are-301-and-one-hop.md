# Redirects are 301 and one hop

**Status:** Pattern (strong default; deviate only with a written reason)
**Domain:** Redirects & migrations
**Applies to:** `technical-seo-engineering`

---

## Why this exists

How you write a redirect changes what the search engine does with it:

- **301 (permanent)** tells the engine the move is permanent — consolidate the old URL's signals onto the new one. **302 (temporary)** tells it to keep the *old* URL indexed. Using a 302 for a permanent move strands the equity on a URL that no longer exists.
- **Redirect chains** (A→B→C) and **loops** waste crawl budget, bleed signal at each hop, and risk the engine giving up before the final URL. Every redirect should point **directly at the final destination**.
- **Bulk redirects to the homepage** are treated as **soft 404s** — the engine sees that you didn't have a real equivalent and discounts them, losing the signal anyway.

## How to apply

```
# DO — permanent, direct, one hop
/old-product            -> /products/new-name          301

# DON'T — temporary code for a permanent move
/old-product            -> /products/new-name          302

# DON'T — a chain (flatten it to one hop to the final URL)
/a -> /b (301);  /b -> /c (301)     # rewrite /a -> /c (301) directly

# DON'T — everything to the homepage (soft-404 signal)
/old-product            -> /                            301
```

**Do:** use 301 for permanent moves; point directly at the final URL; flatten any chain to a single hop; map to the nearest *relevant* page when there's no exact match.

**Don't:** use 302 for a permanent move; build chains/loops; redirect en masse to the homepage; leave the old redirects only "for a while" (keep them as long as old links exist).

## Edge cases / when the rule does NOT apply

- **Genuinely temporary** moves (A/B test, maintenance, seasonal) correctly use 302/307.
- **`410 Gone`** is the right answer for a deliberately retired page with no equivalent — not a redirect.

## See also

- [`./redirect-map-before-you-migrate.md`](./redirect-map-before-you-migrate.md)
- [`../skills/plan-site-migration-redirects/SKILL.md`](../skills/plan-site-migration-redirects/SKILL.md)

## Provenance

Codifies the migration house opinions on redirect hygiene. Grounded in Google Search Central redirect / site-move guidance, retrieved 2026-06-25 — re-verify before quoting.

---

_Last reviewed: 2026-06-25 by `claude`_
