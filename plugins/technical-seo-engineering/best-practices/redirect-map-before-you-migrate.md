# Build the redirect map before you migrate

**Status:** Absolute rule
**Domain:** Site migrations
**Applies to:** `technical-seo-engineering`

---

## Why this exists

A site migration — replatform, domain change, or URL restructure — is the **single highest-risk SEO event there is**. It moves every URL at once, and any old URL that 404s after cutover loses its accumulated ranking signals and any backlinks pointing at it. The damage is often invisible for weeks (until the engine re-crawls) and expensive to recover. The one thing that prevents it is a **complete old→new redirect map built before the cutover**, from an authoritative inventory of the old surface — not reconstructed afterward from the wreckage.

Treat a migration like a database migration: enumerate, map, stage, monitor, and keep a rollback path. Never big-bang it.

## How to apply

1. **Enumerate the old surface first** — crawl the live old site **plus** Search Console (indexed/coverage), the sitemaps, analytics (top organic landing pages), and the server log. Union them; this is the inventory you must not lose.
2. **Map every old URL to its single best new URL.** Prefer a 1:1 match; where none exists, map to the nearest relevant page — **not** the homepage en masse (treated as a soft 404).
3. **Decide the genuine no-equivalents** — redirect vs an intentional `410 Gone`.
4. **Carry on-page signals across** (titles, canonicals, hreflang, structured data, internal links); build the new sitemap from new canonical 200 URLs.
5. **Stage + monitor:** verify on staging, cut over, submit the new sitemap, file a Change of Address for a domain move, and watch Search Console coverage/impressions + the log **daily** for the first weeks.

**Don't:** start the map after launch; redirect everything to the homepage; drop high-value backlinked URLs; remove the old redirects later.

## Edge cases / when the rule does NOT apply

- **A genuinely retired section** with no relevant destination → `410 Gone` is correct (a deliberate signal), not a forced redirect.

## See also

- [`./redirects-are-301-and-one-hop.md`](./redirects-are-301-and-one-hop.md) — how to write the redirects the map produces.
- [`../skills/plan-site-migration-redirects/SKILL.md`](../skills/plan-site-migration-redirects/SKILL.md) — the full procedure.
- [`../templates/site-migration-redirect-map.md`](../templates/site-migration-redirect-map.md) — the deliverable.

## Provenance

Codifies the `technical-seo-lead` house opinion "a migration is the highest-risk SEO event — treat it like a database migration with a rollback plan." Grounded in Google Search Central site-move documentation, retrieved 2026-06-25 — re-verify before quoting.

---

_Last reviewed: 2026-06-25 by `claude`_
