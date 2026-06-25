# Never block in robots.txt a page you also canonicalize

**Status:** Absolute rule
**Domain:** Faceted navigation & duplicate-content handling
**Applies to:** `technical-seo-engineering`

---

## Why this exists

When containing a faceted-navigation or URL-parameter crawl trap, the instinct is to do *everything at once*: `Disallow` the parameter **and** add a `rel=canonical` pointing the refinement back to the base page. This cancels itself out. A `Disallow`ed URL is **never crawled**, so the engine **never reads the `canonical` tag** — the consolidation signal you carefully added is invisible. You get the worst of both: the page isn't consolidated (the canonical didn't apply) *and* it may still rank URL-only (because `Disallow` doesn't deindex).

`canonical` and `Disallow` are mutually exclusive on the same URL by mechanism, not by policy. Pick one based on the goal.

## How to apply

Decide per facet/parameter class from the decision tree:

- **Refinement with no unique demand → `canonical`** to the base page. Keep it **crawlable** so the tag is read. Don't `Disallow` it.
- **Pure noise (sort, session, tracking params) → `Disallow`.** Don't bother with a canonical (it can't be read). Accept it may rank URL-only (it rarely does for these).
- **Facet with genuine search demand → index it** (self-canonical, in the sitemap), don't suppress it at all.

```
# DON'T — contradictory:
#   robots.txt: Disallow: /shoes?color=red
#   page:       <link rel="canonical" href="/shoes/">   (never read!)

# DO — consolidate a refinement (crawlable + canonical):
#   robots.txt: (no Disallow)
#   page:       <link rel="canonical" href="/shoes/">

# DO — kill noise (Disallow only, no canonical):
#   robots.txt: Disallow: /*?*sort=
```

**Do / Don't** — as above; the litmus test is "does the bot need to *read* this page for my chosen signal to work?" If yes (`canonical`/`noindex`), it must stay crawlable.

## Edge cases / when the rule does NOT apply

- **Massive parameter spaces** where crawl budget is the dominant concern may justify `Disallow` *instead of* canonical — accept that consolidation then relies on link/sitemap signals, not the canonical tag.

## See also

- [`./noindex-removes-disallow-hides.md`](./noindex-removes-disallow-hides.md)
- [`./one-canonical-signal-set.md`](./one-canonical-signal-set.md)
- [`../skills/audit-crawlability/SKILL.md`](../skills/audit-crawlability/SKILL.md)

## Provenance

Codifies the `crawl-indexation-engineer` house opinion on faceted-nav containment. The advisory hook flags disallow + canonical on the same path. Grounded in Google Search Central faceted-navigation / canonicalization guidance, retrieved 2026-06-25 — re-verify before quoting.

---

_Last reviewed: 2026-06-25 by `claude`_
