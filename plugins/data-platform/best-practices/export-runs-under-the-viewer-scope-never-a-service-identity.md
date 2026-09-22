# Export always runs under the viewer's own tenant scope, never a service identity

**Status:** Absolute rule
**Domain:** Dashboard export / print / scheduled delivery
**Applies to:** `data-platform`

---

## Why this exists

Confirmed directly against this plugin (FORGE dashboard-top1pct P2-14, 2026-09-03): a positive
control (`grep -rl "tenant_id"` returning 53 files) proved the probe could see the tree, then a
targeted sweep for PDF/print/scheduled-delivery-shaped terms found **zero** files implementing a
dashboard PDF/print export or scheduled/emailed delivery mechanism — the seven raw string hits
were all false positives (connector rate-limit docs, contract-document PDFs, an unrelated
Chili-Piper CSV feature, a stray mention inside a Salesforce-pricing footnote). Export is also the
single most-requested feature on any client-facing dashboard, and every one of this plugin's
existing enforcement layers (Postgres RLS, Cube `access_policy`, DAX roles) assumes the query runs
**as the interactively authenticated viewer**. An export route breaks that assumption by
construction: it typically runs server-side, on a schedule or on a button click, and the easiest
implementation reaches for whatever database credential or API secret is already sitting in the
server's environment — which is very often a broad, unscoped **service identity**, because that's
the credential that was there to reach for. The failure mode this rule exists to prevent: a
server-rendered PDF (or a CSV download, or an emailed report) minted with an unscoped connection
returns every tenant's data to one tenant's export button. Nothing about that failure is visible
in a screenshot or a manual click-through — the export "looks done" and silently leaks.

## How to apply

- **The export route derives its tenant scope from the same server-verified session the
  interactive dashboard uses** — never from a request parameter, a query string, or a form field.
  Mirror the existing `/api/cube-token` pattern exactly: `getSession()` (or the stack's
  equivalent) is the only source of `tenant_id`, and the route accepts no tenant-shaped input.
- **The export route mints (or reuses) a short-lived, tenant-scoped token the same way the
  interactive dashboard does** — it queries Cube (or the semantic layer in play) through the
  *same* `access_policy` / RLS / DAX-role enforcement path as every other read, not a bypass
  route that talks to the warehouse directly with a broader credential. If the export needs a
  wider read (e.g., row-level detail the dashboard's aggregate queries never request), that
  widened *shape* of the query still runs under the same narrowed *identity*.
- **A dimensional, row-level export is a materially different query shape than the dashboard's
  aggregate widgets, and needs its own denial test** — an `access_policy` block correctly scoping
  a `measures`-only query can still leak on a `dimensions`-only query if the policy's filter
  wasn't written to cover every query shape the cube can produce. Don't assume the dashboard's
  existing denial test (per `deny-test-every-stack.md`) covers the export path; extend it.
- **The "service identity" failure mode is specifically what to test for, not just avoid**: mint
  a token that omits the tenant claim entirely (the shape a rushed export implementation reaches
  for when someone hard-codes "just use the app's own Cube API secret") and assert the semantic
  layer denies it — errors, or returns nothing — rather than silently serving unscoped data.
- **Every generated export carries the same provenance this plugin already requires on-screen**
  (see `dashboard-set-data-freshness-slas.md` and the accessibility floor's provenance-footer
  discipline): the source measure, the date range, the comparison baseline, and an as-of
  timestamp. An export that strips provenance on the way out is a worse citation surface than the
  dashboard it came from, not a better one — a PDF or CSV travels further from its source and is
  more likely to be quoted without context.
- **Mechanism choice is a tradeoff, not a single right answer** — see
  [`knowledge/dashboard-export-and-delivery-2026.md`](../knowledge/dashboard-export-and-delivery-2026.md)
  for the three mechanisms (browser print CSS, headless-browser server render, native BI export)
  and when each is warranted. This rule applies to all three: whichever mechanism is chosen, the
  tenant-scope discipline above is non-negotiable.

## What "good" looks like

- The export endpoint's code path is traceable to the same `getSession()` → tenant-scoped-token →
  semantic-layer-query chain as the interactive dashboard, with no branch that swaps in a broader
  credential.
- A cross-boundary denial test exists for the export's specific query shape (row-level/dimensional,
  not just the dashboard's aggregate shape), and it **fails** when the export route is mutated to
  use an unscoped/service identity — proving the test can actually catch the regression it exists
  to catch, not just pass by construction.
- The rendered export (PDF, CSV, or emailed report) carries the same provenance footer the
  on-screen widget does.

## Related

- [`enforce-tenant-isolation-closest-to-data.md`](./enforce-tenant-isolation-closest-to-data.md) —
  the foundational invariant this rule is a specific application of.
- [`deny-test-every-stack.md`](./deny-test-every-stack.md) — the general denial-test requirement;
  this rule is the reason export needs its *own* test, not a reuse of the dashboard's.
- [`issue-short-lived-jwts-for-embeds.md`](./issue-short-lived-jwts-for-embeds.md) — the token
  discipline the export route's token minting must follow.
- [`knowledge/dashboard-export-and-delivery-2026.md`](../knowledge/dashboard-export-and-delivery-2026.md) —
  the three export mechanisms and their tradeoffs.
