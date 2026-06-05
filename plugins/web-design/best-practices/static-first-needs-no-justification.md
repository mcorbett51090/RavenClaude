# Static-First Is the Default — Every Deviation Needs a Written Reason

**Status:** Absolute rule
**Domain:** Web Design — Architecture / rendering strategy
**Applies to:** `web-design`

---

## Why this exists

Server-Side Rendering (SSR) and Client-Side Rendering (CSR) both cost more than static: SSR adds server compute per request, cold-start latency risk, and a runtime infrastructure dependency; CSR adds JavaScript parsing, a render-blocking bundle, and a degraded SEO/AEO surface. Static generation (SSG) produces a file the CDN serves directly — fastest delivery, highest reliability, no server to scale, best caching. House opinion #9 states the preference order: **SSG > SSR > CSR**. Without the "written reason" gate, teams default to SSR because they're familiar with it or because "the site might need dynamic content someday" — and ship unnecessarily complex infrastructure for a 5-page marketing site.

## How to apply

**The gate question (applied to every page/route):**

> "What, specifically, requires this page to be rendered at request time (SSR) or in the browser (CSR) rather than at build time (SSG)?"

**Acceptable written reasons to deviate from SSG:**

| Rendering | Acceptable reason | Not acceptable |
|---|---|---|
| SSR | Personalized content or auth-gated fresh data where SEO matters; per-request pricing or inventory | "We might need it later"; the framework defaults to SSR |
| SSR (ISR) | Content that changes between deploys without a full rebuild (large catalog, CMS-driven) | "The content changes occasionally" — a daily rebuild handles this |
| CSR | App behind auth where SEO is irrelevant | "The page has interactive components" — interactivity ≠ CSR required |

**Rendered-at-build checklist (does your page qualify for SSG?):**

- [ ] The content is the same for every visitor (or nearly so)
- [ ] The content does not need to be fresh at the moment of each request
- [ ] The page does not require server-side user authentication for its primary content
- [ ] Rebuilding + deploying when content changes is acceptable (modern CI can do this in minutes)

**Document the reason in the code:**

```typescript
// pages/pricing.tsx  — SSR is used here because pricing is fetched
// from an external API that returns per-user negotiated rates.
// This cannot be pre-rendered at build time.
export async function getServerSideProps(ctx) { … }
```

**Do:**
- Default to `getStaticProps` / `generateStaticParams` / Astro's SSG for every new route.
- Revisit SSR routes regularly — a route that started with per-user data may now have a cacheable path.
- Use ISR (Incremental Static Regeneration) as the middle ground when the content changes but not per-request.

**Don't:**
- Add SSR "just in case" or because it's the default export in a framework template.
- Treat "has API calls" as a reason for SSR — API calls can happen at build time.
- Choose CSR for any page where SEO or AEO citation matters.

## Edge cases / when the rule does NOT apply

- **Authenticated app pages** where SEO is genuinely irrelevant: CSR is acceptable, with a written note. The rule still applies — "authenticated, no SEO need" is the acceptable written reason.
- **Real-time data surfaces** (live scores, live auctions, live inventory under 10 units): SSR or a hybrid with streaming is correct; the real-time freshness requirement is the written reason.

## See also

- [`../agents/web-architect.md`](../agents/web-architect.md) — makes the rendering-strategy decision for each route
- [`./frontend-progressive-enhancement.md`](./frontend-progressive-enhancement.md) — the companion principle: even SSR pages start as meaningful HTML

## Provenance

Codifies house opinion #9 ("Static-first — pre-render where possible; CSR needs a reason") from `CLAUDE.md` §3. Rendering strategy guidance from `modern-web-stacks-2026.md` in this plugin's knowledge bank. _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
