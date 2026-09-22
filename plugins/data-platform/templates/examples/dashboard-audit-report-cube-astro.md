# Dashboard architecture/story/guidance audit — cube-astro-dashboard-starter

**Date:** 2026-09-03 · **Audited by:** `dashboard-architecture-audit` (invoked via
dashboard-builder build gate, run retroactively as FORGE dashboard-top1pct P1-10's second
worked example)
**Pages/views enumerated:** 1 — `/` (`src/pages/index.astro` → `DashboardLayout.astro` →
`DashboardIsland.tsx`). Same single-route shape as the Next.js starter; not an incomplete scan.

⛔ **Same honest scope note as the Next.js starter's audit report** (see
`dashboard-audit-report-cube-nextjs.md`): a live screenshot could not be captured in this
session (headless-browser spawn blocked at the sandbox level), so this audit uses the skill's
documented structural-read fallback against the actual `.astro`/`.tsx` source. Re-running with
a working browser is a named follow-up.

## Executive summary

Same core shape and same core strength as the Next.js starter (one clear question, a
defensible 2-tier depth ladder, provenance/accessibility now fixed by P1-8) — the two starters
share `KpiCard.tsx`/`RevenueChart.tsx` almost verbatim, so most findings below mirror the
Next.js report rather than duplicate independent analysis of identical code. The one genuinely
**Astro-specific** structural finding this audit surfaced (not present in the Next.js audit,
because Next.js's App Router has no equivalent islands/static split to get wrong) has been
**fixed as part of this same audit pass**: the entire dashboard — including the purely static
"Dashboard" title and tenant-label text — previously shipped inside one `client:load` island,
when Astro's own architecture lets the static shell stay server-rendered and only the
data-fetching KPI/chart widgets hydrate. Not a functional bug, but exactly the kind of
structural decision this audit exists to catch: the starter's own README argues Astro's value
proposition is "pages that ship zero JS unless explicitly marked," and this page's own static
text wasn't getting that benefit until this fix.

## Priority summary

| Priority | Count | Meaning |
|---|---|---|
| P0 | 0 | Breaks the dashboard's core job — the user can't find or act on the key information |
| P1 | 1 open (1 fixed this session) | Significant structure/narrative/guidance gap |
| P2 | 2 | Worth fixing |
| P3 | 0 open (1 fixed this session) | Polish |

## Cross-page coherence (dashboard-level, not per-page)

N/A — one page, same as the Next.js starter. Named explicitly rather than silently skipped.

## Per-page findings

### `/` (DashboardIsland)

**Structure / information architecture**

| Priority | Finding | Evidence | Fix |
|---|---|---|---|
| — (fixed this session) | ~~The static "Dashboard" title and tenant label shipped inside the same `client:load` island as the data-fetching widgets~~, forfeiting Astro's own zero-JS-by-default value proposition for genuinely static content. | `index.astro` (before fix): `<DashboardIsland client:load tenantLabel={...} />` wrapped `Title`/`Subtitle` (static text) and the KPI/chart widgets in one island boundary. | **Fixed:** moved `Title`/`Subtitle` to `index.astro`'s own server-rendered markup (no `client:*` directive — Astro renders a framework component with none to static HTML at zero JS cost); `DashboardIsland` now wraps only the `Grid`/`RevenueChart`. Verified in the actual build output: `dist/server/pages/index.astro.mjs` shows `Title`/`Subtitle` rendered via `renderComponent` with no hydration metadata, while only `DashboardIsland` carries `"client:load": true` — not just a code-looks-right claim, the compiled output was inspected directly. |
| P1 | Same as the Next.js starter: no third depth-ladder tier below KPI/trend. | `DashboardIsland.tsx`: identical `Grid` of 3 `KpiCard`s + one `RevenueChart` shape as `DashboardShell.tsx`. | Same fix as the Next.js report — engagement-specific, not fixable generically in a starter. |
| P2 | Same as the Next.js starter: all three KPI tiles equal visual weight, no dominant-KPI hierarchy. | `DashboardIsland.tsx`'s `Grid numItemsMd={3}`, identical to `DashboardShell.tsx`. | Same fix as the Next.js report. |

**Narrative / storytelling**

| Priority | Finding | Evidence | Fix |
|---|---|---|---|
| P2 | Same as the Next.js starter: generic page title. | `DashboardLayout.astro`: `const { title = "Dashboard" }`; `index.astro` passes `title="Dashboard"` explicitly, not overridden. | Same fix as the Next.js report — engagement-specific rename. |
| — (resolved by P1-8) | Same provenance fix as the Next.js starter — `KpiCard.tsx` is shared/copied, so the comparison-baseline fix applies identically here. | `KpiCard.tsx` (copied), same `comparisonLabel`/footer text. | Already fixed — positive finding, not a gap. |

**User guidance / process orientation**

| Priority | Finding | Evidence | Fix |
|---|---|---|---|
| — (fixed this session) | Same as the Next.js starter: no distinct empty/zero-data state. | `KpiCard.tsx` (copied), identical `isLoading \|\| value === undefined ? "—"` branch. | **Fixed** — same change as the Next.js report, `KpiCard.tsx` re-copied with the fix. |

## Out-of-lane findings (named, not re-scored here)

| Finding | Lane | Route to |
|---|---|---|
| WCAG 2.2 AA coverage | accessibility | Already fixed in P1-8 (shared component code) — not re-scored here. |
| Tenant isolation / `access_policy` correctness | security | `P1-9`'s cross-tenant denial harness — out of this rubric's scope. |
| The `client:load` vs `client:visible` hydration-timing choice for a below-the-fold placement | performance | `dashboard-performance-tuning` skill, not this audit's structure/narrative/guidance lane — named here as the *architecture* placement issue (should this content be an island at all, and how much of it), which IS this audit's lane; the *timing directive choice* once it's correctly scoped is `dashboard-performance-tuning`'s. |

## Fixes applied this session (Last-Mile — automatable ones, not just a list)

| Finding | What was done |
|---|---|
| Static title/subtitle inside the `client:load` island (was P1) | Fixed directly — see the struck-through row above. Genuinely automatable (a pure architecture improvement, no engagement-specific decision needed), so fixed rather than just listed. Verified via the compiled build output, not just the source. |
| Empty/zero-data state design (was P3) | Fixed directly, same change as the Next.js starter. |
| Findings P1-8 already resolved (provenance, WCAG 2.2 AA) | Not re-fixed here — marked resolved-by-reference above. |

## Fixes NOT applied (and why)

| Finding | Why deferred |
|---|---|
| No third depth-ladder tier (P1) | Same as the Next.js report — engagement-specific data model needed. |
| Generic page title (P2) | Same as the Next.js report. |
| No dominant-KPI sizing (P2) | Same as the Next.js report. |
