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
plain React using the local `components/ui/` primitives (see the `@tremor/react` removal note
below), Recharts, and `useCubeQuery`, with no Next.js dependency. `lib/cube-client.ts`
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

## `@tremor/react` removed — local "Tremor Raw"-style components instead (P1-7, 2026-09-03)

Same fix and same reasoning as the Next.js starter (see its README for the full detail):
`@tremor/react`'s registry line has had no stable release since 2025-01-13, and the vendor's
own distribution model has moved to copy-paste components. The same
[`src/components/ui/`](src/components/ui/) primitives are ported here unchanged (plain React,
no framework coupling — matches this starter's existing "copied unchanged" pattern for
`KpiCard.tsx`/`RevenueChart.tsx`). Verified: production build succeeds, and the
`DashboardIsland` client bundle dropped from 916.85 kB to 483.17 kB — `@tremor/react` was the
majority of that chunk's weight, and removing it also resolves the "chunks larger than 500 kB"
build warning P0-4's probe recorded as an open, non-blocking finding.

## What's verified vs. what's still open

- ✅ `KpiCard.tsx`/`RevenueChart.tsx`/the security patterns in `cube-client.ts` and the token
  endpoint are the same ones `security-reviewer` already reviewed (post-fix) on the Next.js
  starter — same no-client-tenant-input rule, same rate-limit + `no-store` pattern.
- ✅ **P0-5 (2026-09-03, FORGE dashboard-top1pct)**: fixed three confirmed defects, each
  empirically verified, not inferred. (1) `src/pages/api/cube-token.ts` read
  `JWT_SIGNING_KEY`/`JWT_ISSUER`/`JWT_KEY_VERSION` via `import.meta.env.X`. Tested directly
  this session: a canary `JWT_SIGNING_KEY` value set at build time does **not** appear
  anywhere in `dist/` (Astro compiled that specific bare read to a genuine `process.env`
  runtime read in this Vite version) — but `JWT_ISSUER`/`JWT_KEY_VERSION`'s
  `import.meta.env.X || "<fallback>"` pattern **did** get frozen: built without those vars
  set, the compiled output showed the literal fallback string baked in permanently, with no
  runtime override possible short of a rebuild. Same defect, confirmed in `src/middleware.ts`'s
  `CUBE_API_ORIGIN` read. All four reads switched to bare `process.env.X` (which Vite's
  static-replace plugin does not touch at all, unlike `import.meta.env.*`) — rebuilt without
  the vars set and confirmed the compiled output now reads `process.env.X || "<fallback>"` as
  a live expression, not a frozen literal. (2) Added `style-src 'self' 'unsafe-inline'` — a
  documented, scoped relaxation, not an oversight: Astro's native CSP support (hash-based)
  doesn't exist in the pinned 4.x line (confirmed by inspecting the installed
  `astro@4.16.19`'s own config types — no `csp` field at all, an Astro 5.9+ feature), and
  Recharts renders SVG chart elements with inline `style="..."` attributes at runtime, which
  a hash can't cover anyway. `script-src 'self'` needed no relaxation — Astro islands
  hydrate via an external `<script type="module" src="...">`, not inline. (3) The unbounded
  `requestLog` rate-limiter map now sweeps stale entries every 5 minutes, same fix and same
  standalone-simulated-time verification as the Next.js starter.
- ✅ **P0-5 was re-reviewed by `ravenclaude-core/security-reviewer` (2026-09-03)** — returned
  **blocked** (shared review with the Next.js starter — same diff class, both starters), fixed
  in the same change:
  - **Tightened `style-src` beyond the blanket relaxation:** the original `'unsafe-inline'`
    permits both inline `<style>` *elements* and `style=""` *attributes*; Recharts only needs
    the latter. Split into `style-src 'self' 'unsafe-inline'` (kept permissive only because
    Astro 4.x has no hash mechanism to tighten it further) + `style-src-attr 'unsafe-inline'`
    (what's actually needed) — strictly tighter than before.
  - **`CUBE_API_ORIGIN` CSP-directive-injection risk:** same finding and same `safeOrigin()`
    fix as the Next.js starter — the value is interpolated raw into a header the browser parses
    as policy; an unvalidated value containing `;` could inject an early directive. Verified via
    `URL`-based validation with a safe fallback on anything malformed.
  - **Rate-limiter bounded the wrong axis:** same finding and same fix as the Next.js starter —
    `isRateLimited` now returns before pushing once already over the ceiling, closing the
    per-key unbounded-array growth the sweep alone couldn't reach.
  - Added `X-Content-Type-Options: nosniff` to all `/api/cube-token` response paths.
  - **`astro.config.mjs`'s adapter-portability claim went stale**: the P0-5 `process.env` fix
    makes "swap only the adapter line" false for Workers-class targets (Cloudflare has no
    `process.env` without `nodejs_compat`, and even then it isn't populated from Worker
    bindings) — updated the comment; not a code change, since adding an `import.meta.env`
    fallback would reintroduce the freeze bug this pass fixed.
  - Added `@types/node` as an explicit `devDependency` (it was previously arriving only
    transitively via `@types/jsonwebtoken` — worked, but the fix's compile-time viability
    shouldn't rest on an incidental transitive dependency).
- ⛔ **This CSP relocation leans harder on `src/middleware.ts`, and this starter's own pinned
  line carries an unfixed middleware-bypass advisory** (see the `npm audit` finding below — a
  middleware auth-bypass via URL encoding on `@astrojs/node@8.3.x`). Impact is bounded here
  (nothing puts *authorization* in middleware — the session check stays in `index.astro`; CSP
  is defense-in-depth, not an authz gate), but a middleware bypass now strips three CSP
  directives instead of one. If you deploy behind a reverse proxy/CDN, also verify the fronting
  layer doesn't strip or rewrite the `Content-Security-Policy` header — this middleware has no
  visibility into what happens to it downstream, per the CSP caveat above.
- ✅ **P2-14 (2026-09-03, FORGE dashboard-top1pct): export/print added, then hardened by
  mandatory security review the same session.** Identical mechanism and identical fix set to the
  Next.js starter (`components/ExportBar.tsx`, rendered inside `DashboardIsland.tsx` since it's
  genuinely interactive, unlike the static `Title`/`Subtitle` that stay outside the island):
  `window.print()` for print/PDF, `src/pages/api/export.ts` for CSV. Token minting and rate
  limiting are factored into `src/lib/mint-cube-token.ts` and `src/lib/rate-limiter.ts`, shared
  with `api/cube-token.ts` — security review found the export route's first draft had already
  lost the rate limiter its cheaper sibling carries; it now has its own, tighter 5/min ceiling.
  `src/lib/csv.ts`'s `toCsvRow()` guards against CSV formula injection (CWE-1236, a blocker —
  quoting alone does not neutralize a leading `=+-@\t\r`); errors are logged server-side with a
  correlation id rather than echoed to the client; every response carries
  `X-Content-Type-Options: nosniff`; a `dashboard.export` audit line is emitted on success; the
  provenance block is escaped through `toCsvRow()`; a `# truncated: true` line appears at the
  5000-row cap. `npx astro build` passes clean with the shared-lib refactor + all fixes present
  (confirmed this session, after the fixes — `dist/server/pages/api/export.astro.mjs` exists in
  the build output); a plain `tsc --noEmit` on these files reports no new errors beyond this
  starter's pre-existing Astro-global false positives (see the CSP section above for that
  caveat's full explanation). The corresponding denial-test extension is in
  `templates/cube-denial-test-harness/` (not yet run against live docker — same open item as
  below).
- ✅ **P2-15 (2026-09-03, FORGE dashboard-top1pct): locale + timezone threading added.** Identical
  mechanism to the Next.js starter: `src/lib/locale.ts`'s `resolveLocaleContext(session)` resolves
  `{locale, timezone}` from the session (tenant-configured fork — see
  `knowledge/dashboard-timezone-decision-2026.md`), falling back to `en-US`/`UTC`.
  `src/components/LocaleProvider.tsx` threads the pair to `KpiCard.tsx`/`RevenueChart.tsx` via
  context (`DashboardIsland.tsx` wraps its content in `<LocaleProvider>`, since `locale`/`timezone`
  reach it as `client:load` island props from `index.astro`'s server-resolved frontmatter — both
  must stay plain, JSON-serializable strings for Astro's hydration to carry them across). Both
  widgets pass an explicit `timezone` on their Cube query object and name it in the provenance
  footer. Same honest correction as the Next.js starter's README: `plan.md`'s literal
  `grep -rn '"en-US"'` still returns 1 hit here — `src/lib/locale.ts`'s named default fallback
  constant, not a hard-coded formatting call; `audit-gates.sh` Gate 270 checks the substantive
  requirement instead. `npx astro build` passes clean with the locale threading present.
- ⛔ Not yet run against a live Cube instance. Not yet used in a real engagement.
- ⛔ **`npm audit` (run 2026-09-03, after the `@cubejs-client/*` 1.7.33 bump + `@astrojs/check`
  addition below) reports 6 findings (3 high, 3 moderate)** against the pinned `astro@4.15.x` /
  `@astrojs/node@8.3.x` line — reflected XSS via server islands, middleware auth bypass via URL
  encoding, host-header SSRF, a `libvips`/`sharp` CVE chain, and more (full list: `npm audit` in
  this directory). **None of these are fixed within the 4.x line** — npm's suggested fix is
  `astro@7.3.0` / `@astrojs/node@11.1.5`, both flagged as breaking changes. That migration has
  **not** been attempted in this pass (Astro's server-output/adapter contract has moved across
  three majors); re-run `npm audit` before using this starter in a real engagement.
- Pinned at authoring time (re-verify before use): Astro 4.x, `@astrojs/react` ^3, `@astrojs/node`
  ^8, `@astrojs/tailwind` ^5, `@cubejs-client/*` 1.7.33 (bumped from 0.35.x — see the Next.js
  starter's README for why), same `recharts` version as the Next.js starter. `@tremor/react` is
  no longer a dependency — see the section above. `package-lock.json` regenerated 2026-09-03
  against these pins.

## Refresh triggers

- Astro major version bump (content collections / islands API changes)
- A real engagement promotes the Astro-specific plumbing from "carried-over pattern" to
  "independently reviewed"
- Cube >=1.2.0 major version bump (matches `cube-schema-starter.yml`'s own trigger — this is the floor
  `access_policy` itself requires, not an arbitrary target)
- `components/ui/`'s visual output should be re-diffed against Tremor's current look
  periodically — it is a styling snapshot, not a live-tracked dependency
