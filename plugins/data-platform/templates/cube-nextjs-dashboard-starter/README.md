# Cube + Next.js + Tremor Raw dashboard starter (Case C)

**New at v0.2.0.** A real, runnable starter for `dashboard-builder`'s Case C (productized
SaaS) — Cube OSS semantic layer + Next.js App Router + local Tremor-Raw-style components +
Recharts + shadcn/ui, wired to this plugin's existing multi-tenant templates instead of
hand-derived per engagement. See the `@tremor/react` removal note below for why "Tremor Raw"
and not the npm package.

## What this is — and isn't

- **Is:** a walking-skeleton Next.js app with a Cube-backed dashboard page, a KPI card, a
  chart, and a server-side JWT-mint route wired to `../jwt-issuer.ts`'s pattern.
- **Isn't:** a competing dashboard *product* meant to replace Superset/Metabase/Cube Cloud.
  This scaffold still routes through `dashboard-builder`'s Case A/B/C/D decision tree — it
  exists so Case C doesn't get hand-assembled from scratch every engagement.

## Composes with (don't duplicate these — this scaffold consumes them)

| Existing template | Role here |
|---|---|
| [`../cube-schema-starter.yml`](../cube-schema-starter.yml) | The semantic layer this app queries. Drop into your Cube project's `schema/`. |
| [`../jwt-issuer.ts`](../jwt-issuer.ts) | The host-app JWT pattern `app/api/cube-token/route.ts` follows (audience: `"cube"`). |
| [`../rls-cross-tenant-test.sql`](../rls-cross-tenant-test.sql) | The DB-layer defense-in-depth test, if Cube connects to Postgres with a tenant-aware role. |
| [`../database-schema-starter.sql`](../database-schema-starter.sql) | The underlying Postgres schema `cube-schema-starter.yml`'s `fact_orders`/`dim_customer` expect. |
| [`../../skills/embed-csp-and-iframe-sandboxing/SKILL.md`](../../skills/embed-csp-and-iframe-sandboxing/SKILL.md) | This is a **no-iframe** pattern (direct REST calls from React to Cube) — the relevant CSP directive is `connect-src`, not `frame-ancestors`. See that skill's "Cube (with custom React UI)" section. |

## Quickstart

```bash
npm install
cp env.example .env.local   # fill in NEXT_PUBLIC_CUBE_API_URL, CUBE_API_ORIGIN, JWT_SIGNING_KEY (32+ bytes)
npm run dev
```

Requires a running Cube instance with `../cube-schema-starter.yml` loaded and a Postgres
database matching `../database-schema-starter.sql`. This starter does not stand up either —
`database-setup-guide` and `cube-schema-scaffolding` own that.

## Architecture

```
app/page.tsx              → server component, resolves tenant, renders <DashboardShell>
app/api/cube-token/route.ts → mints a short-lived Cube-audience JWT server-side
components/DashboardShell.tsx → CubeProvider + layout
components/KpiCard.tsx     → local ui/Card+Metric wired to a useCubeQuery measure
components/RevenueChart.tsx → Recharts AreaChart wired to a useCubeQuery time series
components/ui/             → local Tremor-Raw-style primitives (Card, Metric, Text, Flex,
                              BadgeDelta, Title, Subtitle, Grid, Col) — see the removal note
lib/cube-client.ts         → cubejs() client factory, reads the token from the API route
lib/session.ts             → SEAM: resolve the authenticated tenant_id — host-app-specific,
                              documented but not implemented (this scaffold has no auth
                              provider opinion; wire it to whatever the host app uses)
```

## Tenant isolation

Per data-platform CLAUDE.md §3 #3: for a semantic-layer-fronted stack, **the semantic layer
owns the scope rule** (`cube-schema-starter.yml`'s `access_policy` + `securityContext`); the
DB connection account should be tenant-blind. `lib/session.ts` is the seam that must resolve
a real, session-authenticated `tenant_id` — **never** trust a client-supplied tenant id.

## `@tremor/react` removed — local "Tremor Raw"-style components instead (P1-7, 2026-09-03)

This starter no longer depends on the `@tremor/react` npm package. Verified this session:
its registry line has had **no stable release since 2025-01-13** (`npm view @tremor/react
time.modified`) — there are unreleased `4.0.0-beta-tremor-v4.*` versions on npm, so "no
successor at all" would overstate it, but nothing stable has shipped in ~20 months, and the
vendor's own distribution model has moved to "Tremor Raw" (copy-paste components, no npm
package). Rather than keep tracking a frozen line, the ~5 primitives this starter actually
used (`Card`, `Metric`, `Text`, `Flex`, `BadgeDelta`, `Title`, `Subtitle`, `Grid`, `Col`) are
now small, local, MIT-equivalent components in [`components/ui/`](components/ui/) — matching
this plugin's OSS-first house opinion and this repo's own "seam-marked / small local
components over an unmaintained dependency" pattern. This is a dependency swap, not a
redesign: verified by direct render (all 9 primitives render identically-shaped HTML with no
errors) and by the production build (bundle size dropped, First Load JS for `/` went from
145 kB to 130 kB). If you'd rather keep tracking the frozen npm line, re-adding
`@tremor/react` and reverting the three `./ui` imports is a one-commit revert.

## What's verified vs. what's still open (read before treating this as field-proven)

- ✅ Code follows the pinned dependency versions below and reuses `jwt-issuer.ts`'s existing
  validated JWT pattern rather than inventing a new one.
- ✅ `ravenclaude-core/security-reviewer` reviewed the full seam set (this scaffold + the
  promoted embed components) and returned a **blocked** verdict with 4 concrete findings
  (a client-controlled tenant scope reaching an RLS clause, plus 3 related issues). All 4
  were fixed in the same change that shipped this scaffold — CSP `headers()`, `no-store` +
  rate-limiting on `/api/cube-token`, and the `NEXT_PUBLIC_CUBE_API_URL` naming fix below are
  part of that fix pass, not independent hardening.
- ✅ **P0-5 (2026-09-03, FORGE dashboard-top1pct)**: fixed two more confirmed defects. (1)
  `next.config.js`'s `headers()`-based CSP is evaluated ONCE at `next build` time and baked
  into `.next/routes-manifest.json` permanently — empirically confirmed this session (built
  with `CUBE_API_ORIGIN` unset, the manifest froze `connect-src` to `http://localhost:4000`
  forever, regardless of what was set at `next start` runtime). Moved the CSP to
  `middleware.ts` (runs per-request); the differential test plan.md called for was run: one
  built artifact, booted twice with two different `CUBE_API_ORIGIN` values, produced two
  different `connect-src` header values — confirmed live, not by inference. (2) Added a
  nonce-based `script-src`/`style-src` (Next.js's own documented CSP recipe, verified via
  Context7 2026-09-03) — no more implicit reliance on `'unsafe-inline'`. (3) The unbounded
  `requestLog` rate-limiter map now sweeps stale entries every 5 minutes; verified with a
  standalone simulated-time test (50k distinct users across 5 cycles never left the map
  holding more than the currently-active set). **One earlier FORGE-plan claim was directly
  disconfirmed and corrected, not silently accepted:** the plan asserted `JWT_SIGNING_KEY`
  gets inlined into the built bundle via `import.meta.env`. Empirically tested this session
  (a canary value set at build time does NOT appear anywhere in `dist/` — Next.js Route
  Handlers always read `process.env` at genuine runtime, no static-replace risk). The real,
  narrower, confirmed defect was different: nothing in `route.ts` used `import.meta.env` at
  all (that pattern only exists in the Astro starter).
- ✅ **P0-5 was re-reviewed by `ravenclaude-core/security-reviewer` (2026-09-03)** — returned
  **blocked**, 1 blocker + 5 concerns, all fixed in the same change:
  - **Blocker (real, would have broken the app):** a bare nonced `style-src` authorizes inline
    `<style>` *elements* only — it does NOT authorize inline `style=""` *attributes*, which is
    exactly what `RevenueChart.tsx` (line ~61, an unconditionally-rendered `<div style={{...}}>`)
    and Recharts' own SVG rendering emit at runtime. The original fix would have blocked every
    inline style attribute in this app and collapsed the chart to 0px height. Fixed with the
    correct CSP Level 3 directive split — `style-src-attr 'unsafe-inline'` (what Recharts
    actually needs) alongside a `style-src-elem 'self'` that's strictly tighter than a blanket
    line (Chromium honors the split; Firefox has no `*-attr`/`*-elem` support and falls back to
    the permissive `style-src`, so no regression there). Verified live: booted the built server
    and confirmed the response CSP header carries the correct triple.
  - **`CUBE_API_ORIGIN` CSP-directive-injection risk:** the value is interpolated raw into a
    header the browser parses as policy; CSP honors only the first occurrence of a directive, so
    an unvalidated value containing `;` could inject an early directive (e.g. a permissive
    `frame-ancestors`) that silently overrides the real one. Fixed with a `safeOrigin()`
    validator (parses via `URL`, requires an origin-only shape, falls back to the safe default
    on anything else) — verified live: `CUBE_API_ORIGIN="https://evil.com; frame-ancestors *"`
    correctly fell back to the safe default rather than reaching the header.
  - **Matcher was unanchored + dropped the whole CSP on excluded paths:** `api` (no trailing
    slash) matched `/apidashboard`/`/api-docs`, not just `/api/`; prefetch/API exclusion omitted
    the CSP header entirely rather than just the nonce. Fixed: the matcher now only excludes
    truly static assets; `/api/*` and prefetch requests still get a real, nonce-free baseline
    CSP (the middleware branches internally). Verified live: `/apidashboard` now correctly
    receives the full nonced CSP; `/api/cube-token` gets the baseline (no-nonce) CSP.
  - **Rate-limiter bounded the wrong axis:** the sweep correctly bounds the number of *keys*,
    but a caller already over the limit kept appending to its *own* timestamp array for the
    whole window (O(n²) CPU across a flood, unbounded per-key growth) — the sweep can't reclaim
    fresh-but-already-counted entries. Fixed: `isRateLimited` now returns before pushing once
    already over the ceiling.
  - Added `X-Content-Type-Options: nosniff` to all three `/api/cube-token` response paths.
  - **Named, not fixed (out of scope for this pass):** `MIN_SIGNING_KEY_BYTES` is checked via
    `String.length` (UTF-16 code units, not bytes — a 32-char hex string carries only 16 bytes
    of entropy); pre-existing, both starters, not introduced by this change.
  - Reviewer-verified CVE-2025-29927 (the Next.js `x-middleware-subrequest` middleware-bypass
    CVE) does **not** apply — this starter's pinned `next@14.2.35` is ≥ the patched 14.2.25.
  - ⛔ **If this app is deployed behind a reverse proxy/CDN**, verify the proxy does not strip
    or rewrite the `Content-Security-Policy` response header, and that it forwards the real
    client-visible origin — this middleware sets the header per-request but has no visibility
    into what a fronting layer does to it afterward.
- ✅ **P2-14 (2026-09-03, FORGE dashboard-top1pct): export/print added, then hardened by
  mandatory security review the same session.** `components/ExportBar.tsx` offers "Print / Save
  as PDF" (`window.print()`, no new server surface) and "Download CSV" (`app/api/export/route.ts`).
  Token minting and rate limiting are now **factored into shared modules** —
  `lib/mint-cube-token.ts` and `lib/rate-limiter.ts` — used by both `api/cube-token/route.ts` and
  `api/export/route.ts`, after security review found the export route's first draft (hand-
  duplicated from the token route, matching this scaffold's original convention) had *already*
  drifted: it was missing the rate limiter its cheaper sibling carries. The export route now has
  its own, tighter ceiling (5/min per user, vs. the token route's 30/min — an export runs a
  5000-row warehouse query, not a ~1ms HMAC sign).
  - **2 blockers found and fixed:** (1) CSV formula injection (CWE-1236) — `lib/csv.ts`'s
    `toCsvRow()` now prefixes any cell whose leading character is `=+-@\t\r` with a literal-text
    apostrophe; CSV quoting alone does **not** neutralize this, since Excel/Sheets/LibreOffice
    decide a cell is a formula from the leading character *after* the CSV parser has already
    stripped the quotes. (2) the missing rate limiter, above.
  - **6 concerns fixed:** raw Cube/Postgres error text is no longer echoed to the client (logged
    server-side with a correlation id instead); an explicit 401 branch for a null-ish session
    (defensive — the current `lib/session.ts` placeholder always throws, but a real
    `getServerSession()`-style wiring commonly returns `null`); `X-Content-Type-Options: nosniff`
    on every response path, not just the 200; a structured `dashboard.export` audit-log line on
    every successful export; the provenance block is now routed through `toCsvRow()` instead of
    raw string interpolation; a `# truncated: true` line when the 5000-row cap is hit.
  - Queries **row-level dimensional** data (`orders.id`/`order_date`/`customer_id`), a materially
    different shape than the dashboard's aggregate widgets — see the corresponding denial-test
    extension in `templates/cube-denial-test-harness/` (not yet run against live docker — same
    open item as below).
  - `npx tsc --noEmit` and `npm run build` both pass clean with the shared-lib refactor + all
    fixes present (confirmed this session, after the fixes — `/api/export` compiles as a dynamic
    route alongside `/api/cube-token`).
  - See `knowledge/dashboard-export-and-delivery-2026.md` for why a headless-render/scheduled-
    email mechanism is documented but not scaffolded (this sandbox cannot spawn headless
    Chromium).
- ⛔ **Not yet run against a live Cube instance.** No engagement has exercised this scaffold
  end-to-end yet — that's the "real-engagement validation" this plugin's promotion
  discipline names, and it's still open.
- ⛔ **The cross-boundary denial test is documented, not executed.** See
  [`test/cross-tenant-denial.md`](test/cross-tenant-denial.md) for the procedure; running it
  requires a live Cube + Postgres pair, which this scaffold does not provision.
- ⛔ **`npm audit` (run 2026-09-03, after the `@cubejs-client/*` 1.7.33 bump below) reports 2
  high-severity findings in `next@14.2.35`** (the latest patch on the pinned `^14.2.0` line) —
  DoS via Image Optimizer `remotePatterns`, HTTP request smuggling in rewrites, cache poisoning,
  SSRF in Server Actions, and more (full list: `npm audit` in this directory). **None of these
  are fixed within the 14.x line** — npm's own suggested fix is `next@16.3.4`, which it flags as
  a breaking change. That migration (App Router / Server Component behavior changes across two
  majors) has **not** been attempted in this pass; re-run `npm audit` before using this starter
  in a real engagement and budget for the Next.js major-version migration if the findings still
  apply.
- Pinned versions (re-verify before a new engagement — dependency drift is real, per this
  plugin's quarterly-refresh discipline): Next.js 14.2.x, React 18.3.x, `@cubejs-client/*`
  1.7.33 (bumped from 0.35.x — Cube's `access_policy` requires Cube Core >=1.2.0, and
  `@cubejs-client/react@1.7.33` hard-pins `@cubejs-client/core@1.7.33`), `recharts` 2.12.x.
  `@tremor/react` is no longer a dependency — see the section above.
  `package-lock.json` regenerated 2026-09-03 against these pins.

## Refresh triggers

- Cube >=1.2.0 major version bump (matches `cube-schema-starter.yml`'s own trigger — this is the floor
  `access_policy` itself requires, not an arbitrary target)
- `@cubejs-client/react` hook API changes
- A real engagement promotes this from "code-reviewed" to "field-proven" — update this
  README's status section, don't just delete the caveat
- `components/ui/`'s visual output should be re-diffed against Tremor's current look
  periodically — it was a snapshot of Tremor's styling at authoring time (2026-09-03), not a
  live-tracked dependency, so it will not automatically follow any future Tremor design changes
- Next.js App Router breaking changes
