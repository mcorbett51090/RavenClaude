# Cube + Astro dashboard starter (islands)

**New.** A real, runnable starter for the *actual* common shape of a dashboard engagement on
this stack: a mostly-static site (Astro) with one or more Cube-backed dashboard islands —
not a whole dedicated SaaS app. See [`../cube-nextjs-dashboard-starter/`](../cube-nextjs-dashboard-starter/)
for the Case C "productized SaaS" shape instead; the two are not interchangeable, and
`dashboard-builder` should pick between them by asking which shape the engagement actually is
(mostly-static-with-widgets vs. a dedicated always-interactive app) rather than by framework
preference alone. See the reasoning in `dashboard-builder.md`'s Case A/B routing.

## Why Astro here, honestly

Astro is static-by-default: a page ships zero JS unless you explicitly mark a component as an
island (`client:load`/`client:visible`/etc.). For a site that's mostly marketing/content pages
with a KPI section or an embedded chart, that's a real advantage over an all-client SPA — the
non-dashboard pages pay nothing for the dashboard's dependencies. It is a **worse** fit than
Next.js for a fully logged-in, always-interactive, multi-tenant SaaS product — don't reach for
this starter for that shape; use the Next.js one.

## What's reused vs. new

`KpiCard.tsx` and `RevenueChart.tsx` are copied from the Next.js starter **unchanged** — they're
plain React using Tremor/Recharts/`useCubeQuery`, with no Next.js dependency. `lib/cube-client.ts`
and `lib/session.ts` carry the same patterns (including the same security fixes: no client-side
tenant resolution, token caching with real short-circuit refresh). What's new is Astro-specific:
the page/layout shape, the API endpoint (`src/pages/api/cube-token.ts`, Astro's own request/
response contract instead of Next's Route Handler), and CSP delivery via middleware instead of
`next.config.js`'s `headers()`.

## Requires SSR — this is not a fully static site

The `/api/cube-token` endpoint has to run server-side per-request (it reads the caller's
session and mints a short-lived JWT) — Astro's static output mode can't do that. This starter
sets `output: 'server'` with the **Node adapter** (`@astrojs/node`, standalone mode) as the
documented default. If your actual deployment target is Vercel/Cloudflare/Netlify, swap the
adapter in `astro.config.mjs` — the API route code itself is adapter-agnostic (Astro's
`APIRoute` contract), only the adapter package + `astro.config.mjs` line changes.

⛔ **CSP caveat, stated honestly:** `src/middleware.ts` sets the CSP header on every SSR
response. If your host serves any of this site's assets directly from a CDN/edge cache outside
the SSR runtime (common for `output: 'server'` static fallback pages), those responses won't
pass through the middleware and need the header set at the CDN/host config level too —
middleware alone does not cover every response path on every adapter.

## Quickstart

```bash
npm install
cp env.example .env   # fill in PUBLIC_CUBE_API_URL, CUBE_API_ORIGIN, JWT_SIGNING_KEY (32+ bytes)
npm run dev
```

Requires a running Cube instance with [`../cube-schema-starter.yml`](../cube-schema-starter.yml)
loaded, same as the Next.js starter.

## Architecture

```
astro.config.mjs           → react + tailwind integrations, output:'server', @astrojs/node adapter
src/middleware.ts          → CSP header on every SSR response (see caveat above)
src/pages/index.astro      → the page; mounts <DashboardIsland client:load />
src/pages/api/cube-token.ts → Astro APIRoute: resolves session, mints a short-lived Cube JWT
src/components/DashboardIsland.tsx → CubeProvider + KPI grid + chart (the actual island)
src/components/KpiCard.tsx        → copied unchanged from the Next.js starter
src/components/RevenueChart.tsx   → copied unchanged from the Next.js starter
src/lib/cube-client.ts     → same pattern as the Next.js starter (token cached, real refresh)
src/lib/session.ts         → same documented seam — resolve the real tenant server-side
```

## Tenant isolation

Identical discipline to the Next.js starter (data-platform CLAUDE.md §3 #3): the semantic
layer (`cube-schema-starter.yml`'s `access_policy`) is the load-bearing tenant control.
`src/lib/session.ts` is the seam that must resolve a real, session-authenticated `tenant_id` —
never trust anything client-supplied.

## What's verified vs. what's still open

- ✅ `KpiCard.tsx`/`RevenueChart.tsx`/the security patterns in `cube-client.ts` and the token
  endpoint are the same ones `security-reviewer` already reviewed (post-fix) on the Next.js
  starter — same no-client-tenant-input rule, same rate-limit + `no-store` pattern.
- ⛔ **The Astro-specific plumbing (the API endpoint's Astro shape, the middleware CSP delivery,
  the adapter choice) has NOT itself been through a security review pass.** The patterns are
  carried over deliberately, but the port hasn't been independently re-checked — treat this the
  same as the Next.js starter's own "reviewed, not yet re-confirmed after fixes" status, one
  level further removed (this port happened after that review, not before it).
- ⛔ Not yet run against a live Cube instance. Not yet used in a real engagement.
- Pinned at authoring time (re-verify before use): Astro 4.x, `@astrojs/react` ^3, `@astrojs/node`
  ^8, `@astrojs/tailwind` ^5, same `@cubejs-client/*`/`@tremor/react`/`recharts` versions as the
  Next.js starter.

## Refresh triggers

- Astro major version bump (content collections / islands API changes)
- A real engagement promotes the Astro-specific plumbing from "carried-over pattern" to
  "independently reviewed"
- Cube 0.36+ major version bump (matches `cube-schema-starter.yml`'s own trigger)
