# Cube + Next.js + Tremor dashboard starter (Case C)

**New at v0.2.0.** A real, runnable starter for `dashboard-builder`'s Case C (productized
SaaS) — Cube OSS semantic layer + Next.js App Router + Tremor + Recharts + shadcn/ui, wired
to this plugin's existing multi-tenant templates instead of hand-derived per engagement.

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
components/KpiCard.tsx     → Tremor Card/Metric wired to a useCubeQuery measure
components/RevenueChart.tsx → Recharts AreaChart wired to a useCubeQuery time series
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

## What's verified vs. what's still open (read before treating this as field-proven)

- ✅ Code follows the pinned dependency versions below and reuses `jwt-issuer.ts`'s existing
  validated JWT pattern rather than inventing a new one.
- ✅ `ravenclaude-core/security-reviewer` reviewed the full seam set (this scaffold + the
  promoted embed components) and returned a **blocked** verdict with 4 concrete findings
  (a client-controlled tenant scope reaching an RLS clause, plus 3 related issues). All 4
  were fixed in the same change that shipped this scaffold — CSP `headers()`, `no-store` +
  rate-limiting on `/api/cube-token`, and the `NEXT_PUBLIC_CUBE_API_URL` naming fix below are
  part of that fix pass, not independent hardening.
- ⛔ **The fixes have NOT been re-reviewed.** The reviewer's own recommended merge path was
  "rewrite, then re-submit for re-review" — the rewrite happened; the re-review has not. Don't
  treat this as a clean bill of security health until that happens.
- ⛔ **Not yet run against a live Cube instance.** No engagement has exercised this scaffold
  end-to-end yet — that's the "real-engagement validation" this plugin's promotion
  discipline names, and it's still open.
- ⛔ **The cross-boundary denial test is documented, not executed.** See
  [`test/cross-tenant-denial.md`](test/cross-tenant-denial.md) for the procedure; running it
  requires a live Cube + Postgres pair, which this scaffold does not provision.
- Pinned versions (re-verify before a new engagement — dependency drift is real, per this
  plugin's quarterly-refresh discipline): Next.js 14.2.x, React 18.3.x, `@cubejs-client/*`
  0.35.x, `@tremor/react` 3.14.x, `recharts` 2.12.x.

## Refresh triggers

- Cube 0.36+ major version bump (matches `cube-schema-starter.yml`'s own trigger)
- `@cubejs-client/react` hook API changes
- A real engagement promotes this from "code-reviewed" to "field-proven" — update this
  README's status section, don't just delete the caveat
- Tremor / Next.js App Router breaking changes
