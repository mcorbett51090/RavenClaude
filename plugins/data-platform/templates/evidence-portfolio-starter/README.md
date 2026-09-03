# Evidence.dev portfolio starter (Case A)

**New (FORGE dashboard-top1pct P1-11, 2026-09-03).** Closes a self-acknowledged gap this
plugin's own value-add table named as HIGH-priority and unfunded: Case C had two full app
starters, Case A had a single markdown page template with no runnable project.

## What this is

A minimal, real, three-page Evidence.dev project — `home.md` (overview KPIs + a traffic
trend), `case-studies.md` (a full before/after detail table + a bar chart), `about.md`
(methodology + the single-tenant assumption, documented explicitly). All data comes from a
committed, synthetic `sources/portfolio_demo/portfolio_demo.duckdb` fixture — no real client
data, no live warehouse dependency.

## ⛔ Read `pages/about.md` before assuming this matches your existing Evidence knowledge

Evidence.dev's own CLI, pricing, page syntax, and deployment model have all changed materially
since this plugin's prior 2026-05-21 review — re-verified building this starter, corrected
here rather than silently carried forward. The single most consequential change: **current
Evidence has no build step and re-runs SQL server-side on every page load** — this is a
lightweight always-on server (`evidence serve`), not a pure static-HTML export the way the
plugin's older Case A framing assumed. Full detail, with sources, in `pages/about.md`.

## Quickstart

```bash
# Evidence's current CLI installs via a one-line installer (verified against
# docs.evidence.dev 2026-09-03) — read it before running it, same as any
# curl|sh installer:
#   macOS/Linux: curl -fsSL https://evidence.studio/install.sh | sh
#   Windows:     irm https://evidence.studio/install.ps1 | iex
evidence dev      # local dev server against this dir's committed .duckdb fixture
evidence serve    # production-hardened self-host mode (a running process, not a static export)
```

## What's verified vs. what's still open

- ✅ The `.duckdb` fixture is real and was verified this session — generated with Python's
  `duckdb` package, closed, reopened read-only, and queried successfully (6 case-study rows,
  8 months of pageviews).
- ✅ `evidence.config.yaml`, `theme.yaml`, `sources/*/connection.yaml`'s shape, and the
  Markdoc `{% component %}` page syntax were verified against Evidence's own current
  documentation and its official `evidence-dev/template` repository (fetched live this
  session), not recalled from training data or assumed unchanged.
- ⛔ **Not yet run end-to-end against a live `evidence dev`/`evidence build`.** The current CLI
  installs via a `curl | sh` script this session did not execute — running an arbitrary
  installer wasn't something to do without more care than a template-authoring pass warrants.
  Run it once, for real, before trusting this starter in an engagement.
- ⛔ **`P0-4`'s CI build tier does not yet cover this starter** — it was scoped to the two
  Case C app starters (Next.js/Astro). Adding Evidence to that CI tier is a named follow-up,
  not done here (it would need the same `curl | sh` CLI install inside a GitHub Actions step,
  which deserves its own review before landing in CI).
- ⛔ **`dashboard-architecture-audit` has not been dogfooded against this starter** (`P1-10`
  only covered the two Case C starters). A reasonable next step, not done in this pass.

## Refresh triggers

- Evidence CLI major version bump, or a further deployment-model change (re-verify against
  `pages/about.md`'s "what changed" section — that section itself needs re-checking, not just
  trusted forever)
- Pricing changes (this plugin's own quarterly-refresh discipline, `CLAUDE.md` §3 #9)
- A real engagement promotes this from "doc-verified, fixture-verified" to "CLI-run-verified"
