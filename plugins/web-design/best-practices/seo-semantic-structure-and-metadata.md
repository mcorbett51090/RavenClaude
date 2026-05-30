# Make the page discoverable: semantic structure, complete metadata, valid schema

**Status:** Pattern — every shippable page has a title, meta description, canonical, OG/Twitter cards, a clean heading structure, and validating schema where it earns citations. SEO and a11y are one surface (house opinion #10).

**Domain:** SEO / AEO

**Applies to:** `web-design`

---

## Why this exists

Discoverability now spans two surfaces: classic search rank *and* citation inside AI-synthesized answers (AI Overviews, ChatGPT, Perplexity, Gemini, Claude). Both read the **rendered HTML** — its heading structure, link text, and structured data — which is exactly the semantic structure accessibility needs, so SEO + a11y converge (house opinion #10). The recurring failures are mechanical and the hook flags several: a page with no `<title>` or `<meta description>`, a `noindex` accidentally shipped to production, broken/missing OG cards on a shareable page, heading-level skips, schema that doesn't validate. AEO adds a layer on top of (not instead of) solid technical SEO: answer-ready structure + a connected entity graph earn the citation.

## How to apply

Ship the metadata baseline on every page, keep one clean heading tree, and add JSON-LD schema that validates — `FAQPage` is the highest-impact type for AI citation.

```html
<head>
  <title>Core Web Vitals budgets — Web Design Field Guide</title>
  <meta name="description" content="How to set and enforce LCP, INP, and CLS budgets before you build." />
  <link rel="canonical" href="https://example.com/guides/cwv-budgets" />
  <meta property="og:title" content="Core Web Vitals budgets" />
  <meta property="og:description" content="Set LCP/INP/CLS budgets before build." />
  <meta property="og:image" content="https://example.com/og/cwv.png" />
  <meta name="twitter:card" content="summary_large_image" />
</head>
<script type="application/ld+json">
{ "@context": "https://schema.org", "@type": "FAQPage",
  "mainEntity": [{ "@type": "Question", "name": "What is a good LCP?",
    "acceptedAnswer": { "@type": "Answer", "text": "Under 2.5 seconds at field p75." }}] }
</script>
```

**Do:**
- Give every page a unique `<title>` + `<meta description>`, a `canonical`, and OG/Twitter cards if it's shareable.
- Keep one `<h1>` and a clean heading tree (no level skips); write descriptive link text (serves a11y too).
- Add JSON-LD schema that validates; build a *connected* entity graph (`Organization` → `Person` → `sameAs`) — a lone block doesn't earn citations. Lead with answer-ready structure (see readability doc).

**Don't:**
- Ship `<meta name="robots" content="noindex">` to production by accident (the hook flags this), or a `robots.txt` that disallows `/`.
- Leave canonical missing on key pages, or let trailing-slash/case inconsistency split a URL into duplicates.
- Oversell `llms.txt` — adoption is uneven and engines don't uniformly honor it as of 2026 [verify-at-build — `llms.txt` adoption]; treat it as low-cost, low-certainty hygiene.

## Edge cases / when the rule does NOT apply

- **Intentionally non-indexed pages** (staging, thank-you, gated content) *should* carry `noindex` — the anti-pattern is the *accidental* one on a page you want indexed.
- **Finance / regulatory content** in metadata or schema (claims, disclosures) routes through `regulatory-compliance` / `finance` before shipping.
- **AEO tactics are emergent** — lead clients with the durable moves (strong SEO foundation, answer-ready structure, real entity authority, E-E-A-T) and measure the rest rather than guaranteeing it.

## See also

- [`./content-readability-and-hierarchy.md`](./content-readability-and-hierarchy.md) — answer-ready structure that gets extracted
- [`./frontend-progressive-enhancement.md`](./frontend-progressive-enhancement.md) — crawlers/answer engines read rendered HTML, not post-hydration content
- [`./reach-for-semantic-html-before-aria.md`](./reach-for-semantic-html-before-aria.md) — semantic structure is the shared a11y + SEO surface
- [`../knowledge/answer-engine-optimization-2026.md`](../knowledge/answer-engine-optimization-2026.md) — AEO/GEO tactics, entity graph, `llms.txt` caveat
- [`../agents/web-architect.md`](../agents/web-architect.md) (technical SEO), [`../agents/content-strategist.md`](../agents/content-strategist.md) (content SEO/AEO)

## Provenance

Distilled from house opinion #10 (SEO + a11y converge), the `web-architect` technical-SEO surface + anti-patterns (robots/sitemap/canonical/trailing-slash/schema-validation), the `check-web-anti-patterns.sh` title/description/`noindex` checks, and the AEO tactics + honest caveat in `answer-engine-optimization-2026.md` (retrieved 2026-05-28).

---

_Last reviewed: 2026-05-30 by `claude`_
