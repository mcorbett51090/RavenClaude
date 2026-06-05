# Preconnect to critical origins and prefetch likely-next resources

**Status:** Pattern
**Domain:** LCP / performance
**Applies to:** `frontend-engineering`

---

## Why this exists

LCP (Largest Contentful Paint) is the Core Web Vital that measures when the main content appears. A significant fraction of poor LCP scores are caused by DNS lookups, TLS handshakes, and redirect chains to third-party origins (CDNs, font hosts, API domains) that happen sequentially after the HTML has loaded. Browser resource hints (`preconnect`, `prefetch`, `preload`) tell the browser to start those connections and fetches earlier, before the parser reaches the tags that need them. Used correctly they are free LCP improvements; used incorrectly they waste bandwidth.

## How to apply

```html
<!-- In <head>: preconnect to origins the page will definitely use -->
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link rel="preconnect" href="https://api.example.com" />

<!-- Preload the LCP image — the single most impactful LCP hint -->
<link
  rel="preload"
  as="image"
  href="/hero.webp"
  fetchpriority="high"
/>
```

```tsx
// Next.js: use next/link prefetch for likely-next routes
// (enabled by default when the link enters the viewport)
import Link from 'next/link';
<Link href="/dashboard" prefetch>Go to dashboard</Link>
```

**Do:**
- `preconnect` to every third-party origin used above the fold (fonts, analytics, API).
- `preload` the LCP image (the hero image, the above-the-fold product image) with `fetchpriority="high"`.
- Use `prefetch` for routes the user is likely to navigate to next (the primary CTA destination).
- Include `crossorigin` on font preconnects — fonts are fetched in CORS mode.

**Don't:**
- `preconnect` to origins that are rarely used — each preconnect holds a TCP+TLS slot for ~10s.
- `preload` a resource and never use it — the browser emits a warning and it wastes bandwidth.
- `preload` too many resources — it competes with critical path rendering; limit to 3–5 highest-priority items.

## Edge cases / when the rule does NOT apply

Fully server-rendered pages that ship no dynamic third-party scripts may not have third-party origins to preconnect to. Self-hosted fonts from the same origin do not need a `preconnect`.

## See also

- [`../agents/frontend-performance-engineer.md`](../agents/frontend-performance-engineer.md) — owns LCP and Core Web Vitals.
- [`./optimize-images-and-fonts.md`](./optimize-images-and-fonts.md) — image and font optimization pairs with preload hints.

## Provenance

Google web.dev LCP optimization guide, MDN resource hints documentation. Codifies `frontend-performance-engineer`'s LCP tuning discipline.

---

_Last reviewed: 2026-06-05 by `claude`_
