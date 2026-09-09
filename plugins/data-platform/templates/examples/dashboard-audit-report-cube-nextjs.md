# Dashboard architecture/story/guidance audit — cube-nextjs-dashboard-starter

**Date:** 2026-09-03 · **Audited by:** `dashboard-architecture-audit` (invoked via
dashboard-builder build gate, run retroactively as FORGE dashboard-top1pct P1-10's first
worked example — see the honest-scope note below)
**Pages/views enumerated:** 1 — `/` (`app/page.tsx` → `components/DashboardShell.tsx`). This
starter ships exactly one route; there is no second page to enumerate, not an incomplete scan.

⛔ **Honest scope note on "how this page was seen":** `visual-feedback-loop`'s screenshot
mechanism (`chrome-devtools-mcp` / Playwright) could not run in the session that produced this
report — launching a headless browser failed with a sandbox-level spawn error (`spawn Unknown
system error -88`), confirmed as an environment limitation, not a missing download (Chromium
itself was present on disk). This audit uses the skill's own documented fallback: a structural
layout read of `DashboardShell.tsx`/`KpiCard.tsx`/`RevenueChart.tsx`'s actual JSX tree, cross-
checked against the CSS classes and conditional-render branches in the source. Findings below
are grounded in what the code will render, not a guess — but a live screenshot would still be
the stronger evidence, and re-running this audit with a working browser is a named follow-up,
not assumed unnecessary.

## Executive summary

The dashboard answers one clear question ("how is the business doing on revenue/orders/
customers, right now") with a defensible depth ladder (3 KPI tiles → 1 trend chart), and after
P1-8's provenance/accessibility fixes it no longer hides its own data-freshness or comparison
basis. Its biggest structural problem is that it's a **single, flat page with no depth beyond
one chart** — there's a KPI tier and a trend tier, but no third tier a user could drill into
(a breakdown table, a segment view), so "click to investigate a concerning number" has nowhere
to go. That's expected and acceptable for a *starter* (it exists to be extended per engagement,
not to be a finished product) but is named here as the primary finding rather than glossed
over, per the skill's own "cite evidence, don't grade on a curve for what a starter is" stance.

## Priority summary

| Priority | Count | Meaning |
|---|---|---|
| P0 | 0 | Breaks the dashboard's core job — the user can't find or act on the key information |
| P1 | 1 | Significant structure/narrative/guidance gap |
| P2 | 2 | Worth fixing |
| P3 | 0 open (1 fixed this session) | Polish |

## Cross-page coherence (dashboard-level, not per-page)

- **Overall arc:** N/A — one page, no cross-page arc to assess. Named explicitly rather than
  silently skipped: a future engagement that adds a second page (a customer-detail drill-down,
  say) should re-run this section, not assume single-page coherence transfers.
- **Navigation discoverability:** N/A, same reason.
- **Continuity:** N/A, same reason.

## Per-page findings

### `/` (DashboardShell)

**Structure / information architecture**

| Priority | Finding | Evidence | Fix |
|---|---|---|---|
| P1 | No third tier below the KPI/trend layer — a user who sees a concerning revenue trend has nowhere to drill into (no breakdown-by-segment, no order-level table). | `DashboardShell.tsx`: the entire page is a `Grid` of 3 `KpiCard`s + one `RevenueChart`, no third widget/route. | Add a "view details" affordance on `RevenueChart` (even a placeholder route/anchor for a real engagement to fill in) so the depth ladder has a named next step, not just an implied one. |
| P2 | All three KPI tiles are visually identical weight — no single dominant metric establishes a primary-KPI hierarchy. | `DashboardShell.tsx`'s `Grid numItemsMd={3}` gives `Total revenue`/`Orders`/`Unique customers` equal `Col numColSpanMd={1}` sizing. | If a real engagement knows which metric matters most to this tenant, give it a wider column (e.g. `numColSpanMd={2}` more paired with a smaller secondary tile) rather than three equal tiles. |
| P3 | Chart-type consistency is trivially satisfied (only one chart exists), so this dimension has nothing to score against yet. | `RevenueChart.tsx` is the only chart component. | No fix needed now; re-check when a second chart is added to a real engagement (verify revenue trends elsewhere in the app also use an area chart, not an inconsistent bar chart for the same metric shape). |

**Narrative / storytelling**

| Priority | Finding | Evidence | Fix |
|---|---|---|---|
| P2 | The page has a title ("Dashboard") that names nothing specific — it doesn't say what question this view answers. | `DashboardShell.tsx`: `<Title>Dashboard</Title>`. | For a real engagement, rename to something specific ("Revenue Overview", "Q3 Performance") — the generic placeholder is fine for a starter but should be flagged to the engagement team as a required rename, not silently kept. |
| — (resolved by P1-8) | ~~KPI values were bare numbers with no comparison baseline.~~ Now fixed: each `KpiCard` shows `deltaPct` against an explicit `comparisonLabel` ("vs prior 30 days") and both the current and comparison date ranges appear in the footer. | `KpiCard.tsx`: `comparisonDateRange`/`comparisonLabel` props, footer `Text` rendering `source: {measure} · {dateRange} · {comparisonLabel}`. | Already fixed — listed here as a positive finding, not a gap, since the audit rubric explicitly asks for provenance/comparison-baseline evidence and this is exactly what P1-8 closed. |

**User guidance / process orientation**

| Priority | Finding | Evidence | Fix |
|---|---|---|---|
| — (fixed this session) | ~~No explicit empty/zero-data state design~~ — a tenant with genuinely zero orders saw three `"—"` placeholder tiles identical to the loading state, no explanatory text. | `KpiCard.tsx`: `{isLoading \|\| value === undefined ? "—" : formatValue(value)}` conflated loading and genuinely-zero. | **Fixed:** added an `isZero` branch rendering "No data yet for this period — check back once activity starts, or widen the date range." distinct from the `"—"` loading placeholder. |

## Out-of-lane findings (named, not re-scored here)

| Finding | Lane | Route to |
|---|---|---|---|
| WCAG 2.2 AA coverage (aria-live, chart aria-label + table fallback, error icon+text) | accessibility | Already fixed in P1-8 — see `best-practices/dashboard-meet-the-accessibility-floor.md`. Not re-scored here; this audit's "guidance" dimension only checks whether status is signaled *sensibly*, not the mechanical WCAG conformance itself. |
| Tenant isolation / `access_policy` correctness | security | `P1-9`'s cross-tenant denial harness — this audit's rubric explicitly carries no tenant-isolation criterion (see `dashboard-architecture-audit/SKILL.md`'s scope table). |
| Chart bundle size / render performance | performance | `dashboard-performance-tuning` skill — not assessed here. |

## Fixes applied this session (Last-Mile — automatable ones, not just a list)

| Finding | What was done |
|---|---|
| Empty/zero-data state design (was P3) | Fixed directly — see the struck-through row above. This was genuinely automatable (no engagement-specific decision needed) so it was fixed rather than just listed, per this skill's own "not just a list handed back" Last-Mile discipline. Verified: `npm run typecheck` + `npm run build` both clean after the change. |
| Findings P1-8 already resolved (provenance, WCAG 2.2 AA) | Not re-fixed here (already done in the prior phase) — marked resolved-by-reference above rather than duplicated. |

## Fixes NOT applied (and why)

| Finding | Why deferred |
|---|---|
| No third depth-ladder tier (P1) | Requires a real engagement's actual segment/breakdown data model — a starter has no opinion on what a tenant's "drill into revenue" view should contain. |
| Generic page title ("Dashboard") (P2) | Same reason — the real title is engagement-specific. |
| No dominant-KPI sizing (P2) | Same reason — which metric is "primary" is a per-engagement product decision, not something a starter should hard-code. |
