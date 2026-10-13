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
<meta property="og:title" content="Page Title">  <!-- short + specific; NO site name (Apple TN3156) — og:site_name carries it -->
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
- Size: **1200 × 630 px** (the canonical OGP image size for `summary_large_image`). Apple's floor for Messages is **≥ 900 px wide**; 1200 × 630 is enough there too (see § Messages).
- Format: JPEG or PNG (not SVG; an animated GIF shows its first frame in Messages); keep it under 1 MB
- Content: **graphical — keep words out of the image** and in `og:title` / `og:site_name` (Apple's rule for Messages, below). If a platform-specific variant genuinely needs text, keep it large and inside the safe zone.
- Safe zone: keep important content within the center **900 × 500 px** (platforms may crop the edges)

### Messages (iMessage) — Apple TN3156

Apple's own rules for rich link previews in Messages are [TN3156 — Create rich previews for Messages](https://developer.apple.com/documentation/technotes/tn3156-create-rich-previews-for-messages) (republished 2024-04-30; formerly TN2444). Quoted where it decides something:

- **No text in the image.** *"Avoid text in preview images. Images may be displayed at varying sizes depending on context and device, potentially making text unreadable. For best results, keep the image graphical and use other metadata tags for text. Text provided via metadata is also accessible for people using VoiceOver."* Messages draws `og:title` in its own caption **under** the image, never on it — so "who / what" belongs in `og:title`, where it is crisp at any size, read aloud, and correct in any script.
- **`og:title` is short and specific, with no site branding.** *"Do not put the site name or other branding in the og:title… Use og:site_name for the site name instead."* A `"Page · Site"` suffix produced by a layout's default title is exactly what this forbids — give shareable pages an explicit `og:title`.
- **Metadata must be in the served HTML.** *"Link previews do not follow meta redirects, nor run JavaScript"*; server-side redirects are followed. A client-rendered SPA head gets no preview.
- **Same metadata for every user agent.** Messages fetches with a user agent that contains an old `Safari/601` string plus `facebookexternalhit` and `Twitterbot` (measured, [Netlify forum](https://answers.netlify.com/t/cant-get-open-graph-previews-working-in-imessage-with-netlify-prerendering/87487)); a "browser not supported" gate or bot rule that serves it a different page breaks the preview (an Apple engineer traced one stale preview to exactly that — [forum 735324](https://developer.apple.com/forums/thread/735324)).
- **Sizes:** image ≥ 900 px wide; under 150 px it "may be ignored or presented as icons"; a square icon ≥ 108 px (`apple-touch-icon` is used when there is no good image); the page ≤ 1 MB and all its preview resources ≤ 10 MB. 1200 × 630 is sufficient — an Apple WebKit engineer answered "1200 x 628 should be plenty big" to a claim that 2400 × 1256 is needed ([forum 742322](https://developer.apple.com/forums/thread/742322)); treat "2400 × 1256 for full width" as folklore.
- **Aspect ratio and cropping are undocumented.** Apple says nothing about portrait or tall images and no credible measurement exists. A portrait image is a bet: keep the subject **centred and small enough to survive a centre crop to 1:1 and to 1.91:1**, and test on a device before relying on it.
- **The sender's device builds the preview** and sends it inside the message; a preview already sent never changes (measured — [Mysk](https://mysk.blog/2020/10/25/link-previews/)). Fix the tags before people share, and change the image URL (`?v=<hash of what the pixels depend on>`) when the image changes.
- **Image and icon URLs must return real image bytes.** A 404, or an HTML fallback served with 200, gives no image — check the image URL itself, not just the page.

**Per-entity images (cards, profiles, products).** Render the picture from the entity's *visual* fields only (colours, photo, logo) and key its URL on a hash of those; put the name and other text in `og:title` / `og:image:alt`. Renaming then never invalidates an image, no personal text sits in a URL or cache key, and the preview satisfies TN3156. Worked example: RavenPower's hosted-card `og.png` (2026-10-13) moved from names painted under a photo-and-logo pair to the pair alone with `og:title` = "Name · Company", once TN3156 was read.

**Validation tools:**
- Meta Inspector / opengraph.xyz — check the rendered card before shipping
- Facebook Sharing Debugger — verify Facebook/LinkedIn rendering
- Card Validator (developer.twitter.com) — verify Twitter Card
- Messages has no validator: send the link to yourself from a real device (the preview is built on the sender's phone), and `curl -A` the page with the Messages user agent above to confirm it gets the same `<head>`

**Do:**
- Generate unique OGP images per page for high-value content (blog posts, landing pages); a global fallback OGP image is acceptable for utility pages.
- Keep `og:description` under 200 characters — longer values are truncated on most platforms.
- Include an absolute URL in `og:url` and `og:image` — relative URLs break on some parsers.

**Don't:**
- Use the same `og:image` for every page without a per-page override strategy for key content.
- Leave `og:image` pointing to a development URL that is not publicly accessible.
- Resolve `og:image` against the canonical production origin on a **preview** deployment when the previewed content exists only there — the image URL then points at a host that does not have it.
- Paint the page title, a person's name or other copy into `og:image` for Messages (TN3156) — use `og:title`.
- Forget to update `og:url` when a page is moved (use a redirect + canonical together).

## Edge cases / when the rule does NOT apply

- **Auth-gated pages** that are not publicly shareable: OGP metadata is not useful because the shared link will redirect to a login page. Include a generic site-level OGP fallback only.
- **Pages with `<meta name="robots" content="noindex">`**: verify intentionality — a page that shouldn't be indexed probably also shouldn't be shared publicly, and the OGP metadata would mislead.

## See also

- [`../agents/web-architect.md`](../agents/web-architect.md) — owns technical SEO including OGP/Twitter Card implementation
- [`./seo-semantic-structure-and-metadata.md`](./seo-semantic-structure-and-metadata.md) — the companion rule covering the full SEO metadata surface

## Provenance

Codifies the anti-pattern "Pages with broken or missing OG / Twitter Card metadata for a sharable site" from `CLAUDE.md` §4. OGP specification: ogp.me. Twitter Card spec: developer.twitter.com/en/docs/twitter-for-websites/cards. Messages: Apple TN3156 (fetched 2026-10-13 from the DocC JSON at `developer.apple.com/tutorials/data/documentation/technotes/tn3156-create-rich-previews-for-messages.json`). _Last reviewed: 2026-10-13._

---

_Last reviewed: 2026-10-13 by `claude` — added § Messages from Apple TN3156 and device-measured sources._
