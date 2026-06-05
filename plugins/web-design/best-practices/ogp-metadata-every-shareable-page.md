# Every Shareable Page Has OGP and Twitter Card Metadata

**Status:** Absolute rule
**Domain:** Web Design — SEO / social sharing
**Applies to:** `web-design`

---

## Why this exists

A shared link without Open Graph Protocol (OGP) metadata renders as a raw URL in every social platform, messaging app, and Slack workspace. A link with OGP renders as a card — title, description, image — that earns clicks and builds trust. The anti-pattern "broken or missing OG / Twitter Card metadata for a sharable site" is in `CLAUDE.md` §4 because it is a visible quality gap that affects every share of the page, forever, until it's fixed. On a marketing or content site, this is a conversion-relevant omission.

## How to apply

**Minimum OGP + Twitter Card meta block (every shareable page):**

```html
<!-- Open Graph (used by Facebook, LinkedIn, Slack, iMessage, Discord, WhatsApp) -->
<meta property="og:title" content="Page Title — Site Name">
<meta property="og:description" content="A 1–2 sentence description of this page's content.">
<meta property="og:image" content="https://example.com/images/og/page-slug.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:url" content="https://example.com/page-slug">
<meta property="og:type" content="website">  <!-- or "article" for blog posts -->
<meta property="og:site_name" content="Site Name">

<!-- Twitter Card (used by X/Twitter) -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Page Title — Site Name">
<meta name="twitter:description" content="A 1–2 sentence description.">
<meta name="twitter:image" content="https://example.com/images/og/page-slug.png">
```

**OGP image spec:**
- Size: **1200 × 630 px** (the canonical OGP image size for `summary_large_image`)
- Format: JPEG or PNG; keep it under 1 MB
- Content: legible at thumbnail size; no tiny text
- Safe zone: keep important content within the center **900 × 500 px** (platforms may crop the edges)

**Validation tools:**
- Meta Inspector / opengraph.xyz — check the rendered card before shipping
- Facebook Sharing Debugger — verify Facebook/LinkedIn rendering
- Card Validator (developer.twitter.com) — verify Twitter Card

**Do:**
- Generate unique OGP images per page for high-value content (blog posts, landing pages); a global fallback OGP image is acceptable for utility pages.
- Keep `og:description` under 200 characters — longer values are truncated on most platforms.
- Include an absolute URL in `og:url` and `og:image` — relative URLs break on some parsers.

**Don't:**
- Use the same `og:image` for every page without a per-page override strategy for key content.
- Leave `og:image` pointing to a development URL that is not publicly accessible.
- Forget to update `og:url` when a page is moved (use a redirect + canonical together).

## Edge cases / when the rule does NOT apply

- **Auth-gated pages** that are not publicly shareable: OGP metadata is not useful because the shared link will redirect to a login page. Include a generic site-level OGP fallback only.
- **Pages with `<meta name="robots" content="noindex">`**: verify intentionality — a page that shouldn't be indexed probably also shouldn't be shared publicly, and the OGP metadata would mislead.

## See also

- [`../agents/web-architect.md`](../agents/web-architect.md) — owns technical SEO including OGP/Twitter Card implementation
- [`./seo-semantic-structure-and-metadata.md`](./seo-semantic-structure-and-metadata.md) — the companion rule covering the full SEO metadata surface

## Provenance

Codifies the anti-pattern "Pages with broken or missing OG / Twitter Card metadata for a sharable site" from `CLAUDE.md` §4. OGP specification: ogp.me. Twitter Card spec: developer.twitter.com/en/docs/twitter-for-websites/cards. _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
