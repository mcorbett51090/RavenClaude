# About this starter

## What Case A is, and isn't

This is `dashboard-builder`'s **Case A (portfolio)** shape: a single-owner marketing-site
dashboard showing your own case-study outcomes to prospective clients — not a per-client or
per-tenant deliverable. See `../../best-practices/single-tenant-document-the-assumption.md`.

**Single-tenant by construction, explicitly documented (not silently assumed):** this starter
has no `tenant_id` column anywhere, no multi-tenant scoping, and no RLS/`access_policy` layer
— there is exactly one viewer of this data (the site owner publishing their own portfolio) and
exactly one dataset. If a future engagement needs this pattern to serve **per-client**
dashboards (each client sees only their own case studies), that is a different shape entirely
— Case B or C, not Case A — and needs the tenant-isolation discipline `data-platform`'s house
rules require (`CLAUDE.md` §3 #3), which this starter deliberately does not implement.

## What changed in Evidence.dev since this plugin's last review (2026-09-03)

This plugin's knowledge bank and `dashboard-builder.md`'s Case A guidance were last verified
2026-05-21. Re-verified building this starter (2026-09-03) and found real drift, corrected
rather than silently carried forward:

- **Pricing changed.** The old "Team $15/user/mo, Pro $25/user/mo" claim is gone — current
  Evidence Cloud is Team at **$2,500/month flat, unlimited users** (no per-user pricing, no
  Pro tier), Enterprise custom. Embedding/white-labelling remains Enterprise-only. The MIT OSS
  license claim is still accurate (confirmed against the repo's own LICENSE file).
- **The CLI changed.** The old `npm run dev` / `npm run build` workflow is explicitly
  deprecated in Evidence's own current project template, in favor of a standalone `evidence`/
  `evd` CLI binary (`evidence init`, `evidence dev`, `evidence serve`, `evidence build`).
- **The deployment model changed, and this is the load-bearing one.** Evidence's own migration
  guide states plainly: legacy Evidence ran build-time SQL against DuckDB-WASM in the browser
  and produced a fully static site; **current Evidence has no build step — queries re-run
  server-side on every page load** against a direct connector. `evidence serve` is described as
  "similar to `evidence dev` but hardened for production" — i.e. a **long-running server
  process**, not a one-time static export. This starter still uses DuckDB as its direct
  connector (a genuinely local `.duckdb` file, not a live remote warehouse — see
  `sources/portfolio_demo/connection.yaml`), which keeps it cheap and dependency-free, but "just
  deploy static HTML to Vercel/Netlify" is no longer an accurate description of how this runs
  in production. Budget for a small always-on Node process, not a pure static-hosting bill.
- **The page syntax changed.** Current Evidence pages use Markdoc-style `{% component %}` tags
  (`{% big_value %}`, `{% line_chart %}`, `{% table %}`) rather than the older Svelte-component
  `<Import />` style. This starter's pages use the current syntax throughout.

⛔ **Honest limit on this starter's own verification:** the `.duckdb` fixture file
(`sources/portfolio_demo/portfolio_demo.duckdb`) was generated and read back successfully with
Python's `duckdb` package (real, verified — not assumed). The page syntax and connector shape
were verified against Evidence's own current documentation and its official
`evidence-dev/template` repository (fetched directly, not recalled from training data). What
was **not** verified: actually running `evidence dev`/`evidence build` end-to-end against this
starter — the current CLI installs via a `curl | sh` installer script this session did not
execute (a legitimate, documented install path for the tool, but running an arbitrary
installer script is exactly the kind of action this repo's own guardrails ask to be careful
about, and no sandboxed way to verify it safely was available here). Run `evidence dev` against
this starter once, for real, before trusting it end-to-end.
