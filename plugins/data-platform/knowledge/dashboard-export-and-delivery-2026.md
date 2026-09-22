> **Last reviewed:** 2026-09-03. Sources: `@react-pdf/renderer` and `puppeteer`/`playwright`
> project docs (package landscape, not vendor pricing — lower re-verification urgency), this
> plugin's own `templates/cube-nextjs-dashboard-starter` and `templates/cube-astro-dashboard-starter`
> implementations (FORGE dashboard-top1pct P2-14). Refresh when: (a) either starter's export
> mechanism changes, (b) a client engagement needs scheduled/emailed delivery and this file's
> "not yet built" disposition on that mechanism needs revisiting, (c) a materially better
> browser-print-to-PDF or headless-render library emerges.

# Dashboard export and delivery — three mechanisms, one tenant-scope discipline

Export and scheduled delivery are consistently the single most-requested feature on any
client-facing dashboard, and this plugin had **zero** coverage of it before P2-14 (confirmed via
a positive-controlled sweep — see
[`best-practices/export-runs-under-the-viewer-scope-never-a-service-identity.md`](../best-practices/export-runs-under-the-viewer-scope-never-a-service-identity.md)
for the exact probe and finding). This file covers the three real mechanisms, their tradeoffs, and
which one each starter implements.

## The tenant-scope invariant, restated once

Every mechanism below runs the export query through the **same** tenant-scoped identity as the
interactive dashboard — never a service identity, never a broader credential reached for because
it happened to be in the server's environment. See the best-practice file linked above; it is not
repeated per-mechanism below.

## Mechanism 1 — Browser print CSS (implemented in both starters)

The user hits a native `window.print()` (or the browser's own "Save as PDF" in the print dialog);
a `@media print` stylesheet hides app chrome (nav, buttons, the export bar itself) and lets the
widgets + their provenance footers render as the printable content.

**Tradeoffs:**

- **Zero new server surface, zero new dependency, zero new tenant-isolation hazard** — the
  rendered content is exactly what's already on screen, already fetched through the viewer's own
  tenant-scoped Cube token. There is no separate "export path" to accidentally leak through.
- **Fidelity is browser-dependent** — page breaks, font substitution, and chart-canvas rendering
  in print mode vary across browsers. Acceptable for an internal or lightly-branded deliverable;
  not pixel-perfect enough for a polished client-facing PDF brand asset.
- **No server-side generation** — can't be scheduled, can't be emailed, requires the viewer to be
  looking at the dashboard at the moment of export.

**This is the default for both starters** — lowest complexity, lowest risk, and it's the
mechanism most dashboards actually need (a user wants "what I'm looking at, on paper or as a
PDF," not a separately-branded report).

## Mechanism 2 — Native/server-side data export (implemented in both starters, CSV)

A server route (`/api/export` in the Next.js starter, `src/pages/api/export.ts` in the Astro one)
derives the tenant from the same server-verified session `/api/cube-token` uses, mints (or
reuses) a tenant-scoped Cube token the same way, queries Cube for **row-level, dimensional** data
(not just the dashboard's aggregate measures — see the best-practice file for why that's a
materially different query shape needing its own denial test), and streams it back as CSV with a
provenance header block (source measure, date range, as-of timestamp) as the first few rows.

**Tradeoffs:**

- **Genuinely portable** — a CSV opens in any spreadsheet tool, feeds a client's own BI tool, or
  gets attached to an email. This is the mechanism a data-literate client stakeholder actually
  wants, more often than a PDF.
- **Real server-side tenant-isolation surface** — this is the one mechanism in this file with an
  actual denial-testable attack surface, which is why `templates/cube-denial-test-harness/` was
  extended (P2-14) with an export-path test rather than trusting the dashboard's existing test to
  cover it.
- **No visual/branded output** — a CSV is data, not a report. Doesn't satisfy "email the exec a
  PDF" asks on its own.

## Mechanism 3 — Headless-browser server render (documented, not implemented)

A server process (Puppeteer/Playwright, or a hosted rendering service) loads the dashboard as a
real browser would, screenshots or prints it to PDF, and returns/emails the result. This is what a
"scheduled emailed report" ultimately requires, since mechanism 1 needs an active viewer and
mechanism 2 produces data, not a branded document.

**Why this is documented but not scaffolded into either starter, honestly:** this same FORGE run
(P0-4, P1-10) hit a hard sandbox limitation — headless Chromium cannot be spawned in this
development environment (`spawn Unknown system error -88`, confirmed via a direct launch attempt,
not inferred). Scaffolding a headless-render export route without ever being able to run it once
in this environment would be shipping an unverified, security-sensitive server surface — worse
than not shipping it. **This is a named, dated follow-up**, not a silently-implied gap: a future
session with a working headless-browser runtime (or a hosted rendering API) should implement this
mechanism, reusing the same tenant-scoped-session → tenant-scoped-token pattern mechanism 2
already establishes, and extend the denial harness again for whatever query shape the rendered
report actually issues.

**Scheduled/emailed delivery** (a cron-triggered render + an email-send step) is the same
open follow-up, layered on top of mechanism 3 — not attempted separately, since it has no
foundation to build on without mechanism 3 existing first.

## Recommended default by engagement shape

| Need | Mechanism |
|---|---|
| "Let me print/save what I'm looking at" | Mechanism 1 (browser print CSS) — ship it, it's free |
| "Give me the raw numbers to work with" | Mechanism 2 (CSV export) — ship it, tenant-scope it, denial-test it |
| "Email me a branded PDF every Monday" | Mechanism 3 — named follow-up, needs a headless-render-capable environment before it can be built and verified, not just built |

## Related

- [`best-practices/export-runs-under-the-viewer-scope-never-a-service-identity.md`](../best-practices/export-runs-under-the-viewer-scope-never-a-service-identity.md) —
  the tenant-scope rule every mechanism above must satisfy.
- [`templates/cube-denial-test-harness/`](../templates/cube-denial-test-harness/) — the executable
  denial test, now covering both the dashboard's aggregate-query shape (P1-9) and the export's
  dimensional-query shape (P2-14).
- [`dashboard-set-data-freshness-slas.md`](../best-practices/dashboard-set-data-freshness-slas.md) —
  the provenance/as-of discipline every export's output must carry.
