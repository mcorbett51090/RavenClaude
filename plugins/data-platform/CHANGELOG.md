# Changelog — data-platform

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.26.0] — 2026-09-03

### Added

- **P1-11** — closed a self-acknowledged HIGH-priority gap that had survived several releases:
  Case C had two full runnable app starters, Case A had a single markdown page template. New
  `templates/evidence-portfolio-starter/`: a real, three-page Evidence.dev project against a
  **committed, genuinely verified `.duckdb` fixture** (generated and read back successfully
  with Python's `duckdb` package this session — not assumed).
  - **A major, unexpected finding surfaced re-verifying Evidence.dev before building on it**
    (this plugin's prior knowledge was dated 2026-05-21): pricing changed (the old
    "$15/user/mo, $25/user/mo, Team/Pro" tiers are gone — current is Team $2,500/month flat
    unlimited users, no Pro tier, Enterprise custom; MIT license confirmed still accurate),
    the CLI changed (npm scripts are explicitly deprecated in Evidence's own current template
    in favor of a standalone `evidence`/`evd` binary), the page syntax changed (Markdoc
    `{% component %}` tags replaced the older Svelte-import style), and — the load-bearing
    one — **the deployment model changed**: current Evidence has no build step and re-runs
    SQL server-side on every page load (`evidence serve` is a long-running process, "similar
    to evidence dev but hardened for production"), not the old build-once static-HTML-export
    model this plugin's Case A framing assumed. Corrected `agents/dashboard-builder.md`'s
    stale pricing claim and documented the full finding, with sources, in the scaffold's own
    `pages/about.md` rather than silently building on the outdated assumption.
  - Baked in the plugin's own invariants: provenance (the SQL block itself is the citable
    source for every number), an explicit "as of" note, and an explicit single-tenant-by-
    construction documentation per `best-practices/single-tenant-document-the-assumption.md`.
  - Added a **stack-case coverage matrix** to `CLAUDE.md` §9a — Case A/B/C/D/E × (agent
    guidance, skill, template, runnable scaffold, denial test, audit example), every cell
    carrying an entry or an explicit dated "N/A because…". New check in
    `scripts/check-data-platform-self-description.py` asserts no cell is silently empty,
    proven with a must-pass/must-fail fixture before wiring into `audit-gates.sh` Gate 263.
  - **Honest limits, stated plainly:** the current Evidence CLI installs via a shell-script
    one-line installer that this session deliberately did not execute (running an arbitrary
    downloaded installer wasn't something to do without more care than a template-authoring
    pass warrants) — so this starter has **not** been run end-to-end against a live `evidence
    dev`/`evidence build`, is **not** yet covered by `P0-4`'s CI build tier, and has **not**
    been dogfooded by `P1-10`'s `dashboard-architecture-audit` pass. All three are named,
    dated follow-ups in the scaffold's own README, not silently implied as done.

**Migration:** none — new, additive template directory; the one existing-file change
(`dashboard-builder.md`'s pricing correction) fixes a claim that was already wrong.

## [0.25.0] — 2026-09-03

### Added

- **P1-10** — `dashboard-architecture-audit` was declared a mandatory build gate but had never
  been run once. Ran it for real against both app starters (structural-read fallback, not a
  live screenshot -- headless-browser spawn was blocked at the sandbox level in this session,
  confirmed via a direct launch attempt, not just an inference from a slow download) and
  committed the first two worked examples: `templates/examples/dashboard-audit-report-cube-
  nextjs.md` and `-cube-astro.md`.
  - Both audits found real findings. Two were genuinely automatable (no engagement-specific
    decision needed) and were **fixed in this same pass**, per the skill's own Last-Mile
    discipline of not just listing what's fixable: a distinct empty/zero-data state (both
    starters' `KpiCard.tsx` previously showed the same `"—"` for "still loading" and
    "genuinely zero data"), and an Astro-specific structural fix -- the static "Dashboard"
    title/tenant-label previously shipped inside the same `client:load` island as the
    data-fetching widgets, forfeiting Astro's own zero-JS-by-default value proposition;
    verified in the compiled build output (`dist/server/pages/index.astro.mjs`) that `Title`/
    `Subtitle` now render with no hydration metadata while only `DashboardIsland` carries
    `client:load`.
  - **Honest correction to the plan's own acceptance test:** the plan expected re-running the
    audit after P1-8 would yield zero open P0/P1 for both starters. It didn't -- the audit's
    structure/narrative/guidance rubric found a genuinely new P1 (no third depth-ladder tier
    below the KPI/chart layer) that P1-8's provenance/accessibility work never touched, and
    that finding is legitimately engagement-specific (a starter has no opinion on what a
    tenant's drill-down view should contain) -- not something to force-fix or force-hide.
    `architecture_audit_status` is honestly `partial` for both starters, not `pass`, matching
    `dashboard-builder.md`'s own Output Contract rule that unresolved P0/P1 findings mean the
    build isn't complete.
  - Added a worked-example pointer + tenant-isolation-scope-boundary note to
    `skills/dashboard-architecture-audit/SKILL.md`'s References.
  - Added `scripts/audit-gates.sh` Gate 267: a lightweight, no-browser-needed structural check
    (empty-state branch + comparison-baseline label both present in source) as a cheap
    complement to the full audit, which does need a browser or a human to run for real.

**Migration:** `DashboardIsland`'s props changed in the Astro starter -- it no longer accepts
`tenantLabel` (moved to `index.astro`'s own markup). A consumer who forked that starter and
calls `<DashboardIsland tenantLabel={...} />` directly needs to move that prop to a sibling
`<Title>`/`<Subtitle>` in their own page.

## [0.24.0] — 2026-09-03

### Added

- **P1-9** — an executable cross-tenant denial test harness, `templates/cube-denial-test-
  harness/`, replacing both starters' `test/cross-tenant-denial.md`'s honestly-disclosed
  "procedure, not a passing CI check" status (that status was correct at the time -- "a script
  that always passes because it never reaches a live Cube instance would be worse than no
  test" -- the gap was always the missing environment, not the script). New docker-compose
  fixture: Postgres 16 + Cube pinned to `v1.7.33` (verified against the Docker Hub registry
  API directly, not just documentation -- and chosen specifically because it satisfies P0-1's
  `access_policy` >=1.2.0 floor, the version-floor confusion this whole harness exists to stop
  recurring). A `vitest` test asserts a positive control (tenant A's own revenue is non-zero --
  without it, a broken pipeline and a working denial both look like "empty result") before
  asserting the actual denial, at both the Cube `access_policy` layer and the Postgres RLS
  layer. Caught and fixed a real bug in the harness's own design before shipping it: the
  compose Postgres superuser always bypasses RLS regardless of policy, so the RLS-layer
  assertion connects as `viewer_role` (granted LOGIN in the seed fixture specifically for
  this), never the superuser -- an RLS test run as a superuser would have passed
  unconditionally and proven nothing. Wired into `scripts/audit-gates.sh` as Gate 266, Tier 4,
  opt-in behind `DP_INTEGRATION=1` (never in the default suite -- it needs docker); with
  docker absent it loud-skips via the existing `_skip_or_fail` helper (hard failure in CI,
  never a silent pass).
  - **Honest limit:** this harness was authored and reasoned through carefully -- the
    docker-compose YAML validated, the Cube image tag confirmed to exist via the registry API,
    the schema-mount path verified against Cube's own documented convention (via Context7, not
    assumed), the test file typechecks clean and correctly fails with `ECONNREFUSED` (not a
    syntax/import error) when run with no live server -- but it has **not been executed
    against a live Cube+Postgres pair**, since no docker runtime was available in the sandbox
    that built it. The mutation tests plan.md's own acceptance criteria call for (delete
    `access_policy` -> denial test must fail; drop `FORCE ROW LEVEL SECURITY` -> RLS test must
    fail) are documented in the harness's README as not-yet-run, for the next session with
    docker available to execute directly.

**Migration:** none — new, additive template directory; no existing file's behavior changed.

## [0.23.0] — 2026-09-03

### Fixed

- **P1-8** — `best-practices/dashboard-provenance-on-every-widget.md` (an ABSOLUTE rule) requires
  source query + date range + comparison baseline on every widget; `KpiCard.tsx`'s
  `useCubeQuery({ measures })` carried no `timeDimensions` and no baseline label while its own
  docblock claimed the rule satisfied. Separately, `agents/dashboard-builder.md` claimed WCAG
  2.1 AA while `knowledge/dashboard-visual-craft-2026.md` declared a WCAG 2.2 floor -- two
  different numbers for one plugin -- and `grep -rnE 'aria-[a-z]+|role=' templates/cube-*-
  dashboard-starter` returned zero real matches in either starter (confirmed with a positive
  control proving the probe could see the tree).
  - Reconciled to **WCAG 2.2 AA** everywhere (a superset of 2.1) across `agents/dashboard-
    builder.md`, `templates/dashboard-engagement-checklist.md`,
    `knowledge/dashboard-visual-craft-2026.md`. `grep -rn "WCAG 2\.1" plugins/data-platform`
    now returns 0.
  - Rewrote `KpiCard.tsx`/`RevenueChart.tsx` in **both** starters separately (per the critic's
    finding that the Astro copy is a separately-maintained duplicate, not byte-shared with the
    Next.js version -- a union grep across both trees can pass with only one fixed): real
    `timeDimensions` with a current-period + comparison-period Cube query pair, a visible
    provenance footer naming the measure/date-range/baseline, `role="status"`/`aria-live` on
    async-updating regions, `role="img"`/`aria-label` + a visually-hidden `<table>` fallback on
    charts, `role="alert"` + icon-and-text (not color-alone) on error states.
  - New `best-practices/dashboard-meet-the-accessibility-floor.md` codifying the reconciled
    floor as a citable, absolute rule.
  - Added an `axe-core` (`@axe-core/playwright`) assertion to the shared
    `templates/ci-headless-smoke.js` -- zero serious/critical violations, asserted per starter
    (two independent CI jobs, not a union).
  - Both starters verified: `tsc --noEmit`/`astro check` clean, production build clean,
    `aria-`/`role=` grep non-zero in both trees (confirmed separately, not via a union check).

**Migration:** `KpiCard`'s prop signature changed -- `timeDimension` is now required (it was
previously accepted only by `RevenueChart`). A consumer who forked either starter and calls
`<KpiCard>` directly needs to add that prop.

## [0.22.0] — 2026-09-03

### Fixed

- **P1-7** — removed `@tremor/react` from both app starters. Verified this session: its
  registry line has had no stable release since 2025-01-13 (`npm view @tremor/react
  time.modified`) — there are unreleased `4.0.0-beta-tremor-v4.*` versions on npm, so "no
  successor at all" overstates it, but nothing stable has shipped in ~20 months, and the
  vendor's own distribution model has moved to "Tremor Raw" (copy-paste components, no npm
  package). Both starters actually only used 9 primitives (`Card`, `Metric`, `Text`, `Flex`,
  `BadgeDelta`, `Title`, `Subtitle`, `Grid`, `Col`); authored small local Tremor-Raw-style
  equivalents in `components/ui/` (Next.js) / `src/components/ui/` (Astro, ported unchanged)
  using the same `tremor.*` Tailwind color tokens the starters already defined (those were
  always plain Tailwind config, not a dependency on the npm package). Verified by direct
  render (all 9 primitives render identical-shaped HTML, no errors) and by production build:
  the Next.js starter's First Load JS for `/` dropped 145 kB → 130 kB; the Astro starter's
  `DashboardIsland` client bundle dropped 916.85 kB → 483.17 kB, which also resolves the
  "chunks larger than 500 kB" build warning P0-4's probe recorded as an open finding.
  Regenerated both lockfiles.

**Migration:** a consumer who forked either starter and imported from `@tremor/react`
directly should switch to importing the same component names from `./ui`/`./components/ui`
instead — the props surface is a deliberate subset matching what these starters actually
used, not a full re-implementation of Tremor's API.

## [0.21.0] — 2026-09-03

### Fixed

- **P1-6** — five of fifteen skills (`dbt-project-scaffolding`, `multi-tenant-migration`,
  `data-quality-tests`, `cross-system-identity-resolution`, `support-ticket-normalization`)
  had zero references in any `agents/*.md` — confirmed this session with a positive control
  (`cube-schema-scaffolding` returns a hit in `dashboard-builder.md`, proving the probe
  works) before trusting the negative result. A dispatched subagent loads its own
  `agents/*.md`, not `CLAUDE.md`'s skill table, so these were shipped, indexed, and
  structurally invisible at runtime — the highest ratio of already-paid-for value to effort
  in the whole FORGE run. Wired all five into their owning agents (References + Surface-area
  pointers): `etl-pipeline-engineer.md` gets four, `database-setup-guide.md` gets
  `multi-tenant-migration`, `dashboard-builder.md` gets two secondary pointers.
- New `scripts/check-data-platform-skill-reachability.py` (data-platform-scoped) — every
  skill must be mentioned in an `agents/*.md` file or carry an `invoked_by:` frontmatter
  field for the legitimate cross-plugin case. Added `invoked_by:` frontmatter to the four
  skills genuinely primary-consumed by `ravenclaude-core` agents (`stack-selection`,
  `jwt-embed-issuance`, `rls-policy-authoring`, `embed-csp-and-iframe-sandboxing`).
  Deliberately reads `agents/*.md` and each skill's own frontmatter directly rather than
  CLAUDE.md's prose table (P0-2 already found that class of table drifts from reality —
  trusting it as this gate's source of truth would reintroduce the same defect shape).
  Wired into `audit-gates.sh` as Gate 265, with a must-pass/must-fail fixture pair.

**Migration:** none — doc + script fixes only; no skill or agent behavior changed.

## [0.20.0] — 2026-09-03

### Fixed

- **P0-5** — the execution-blocking-severity defects P0-4's build gate surfaced. Confirmed
  empirically (not by inference) via direct build-and-grep testing this session:
  - Both starters read `JWT_SIGNING_KEY`/`JWT_ISSUER`/`JWT_KEY_VERSION` (Astro) via
    `import.meta.env.X` with a `||` fallback. Vite's dead-code-elimination froze the
    `JWT_ISSUER`/`JWT_KEY_VERSION` reads to their literal fallback at build time when those
    vars were unset during `astro build` — a later deployment's runtime value was silently
    ignored until a rebuild. **One prior FORGE-plan claim was directly disconfirmed and
    corrected rather than silently accepted**: the plan asserted the JWT signing *secret*
    itself gets inlined into the built bundle. A canary value set at build time does NOT
    appear anywhere in `dist/` — Astro compiled that specific bare `import.meta.env` read to
    a genuine runtime `process.env` read in this Vite version. The real, narrower, confirmed
    defect was the `||`-fallback freeze on `JWT_ISSUER`/`JWT_KEY_VERSION`, and the identical
    pattern in `middleware.ts`'s `CUBE_API_ORIGIN` read (this one matched the plan's claim
    exactly). All four switched to bare `process.env.X` reads.
  - The Next.js starter's CSP, set via `next.config.js`'s `headers()`, is baked into
    `.next/routes-manifest.json` once at `next build` time — confirmed by building without
    `CUBE_API_ORIGIN` set and finding the frozen `localhost:4000` value in the manifest.
    Moved to a new `middleware.ts` (runs per-request); the differential test — one built
    artifact, booted twice with two different `CUBE_API_ORIGIN` env values, produces two
    different `connect-src` header values — was run live, not asserted from inference.
  - Added a nonce-based `script-src`/`style-src` to the Next.js starter, following Next.js's
    own documented CSP recipe (verified via Context7 docs 2026-09-03). Added
    `style-src 'self' 'unsafe-inline'` to the Astro starter — a documented, scoped
    relaxation (Astro 4.x, the pinned line, has no native CSP hash/nonce mechanism —
    confirmed absent from the installed `astro@4.16.19`'s own config types — and Recharts
    renders inline `style="..."` attributes on SVG chart elements at runtime, which a hash
    couldn't cover regardless); `script-src 'self'` needed no relaxation since Astro islands
    hydrate via external `<script type="module">` tags, not inline.
  - Both starters' unbounded `requestLog` rate-limiter map now sweeps stale entries every 5
    minutes — verified with a standalone simulated-time test (50k distinct users across 5
    cycles never left the map holding more than the currently-active set; a real-time burst
    test alone couldn't exercise the eviction path).
  - Named, not fixed: Next.js 16 deprecates the `middleware` filename/export in favor of
    `proxy` (not a blocker today — deferred with the rest of the Next.js major-version
    CVEs — but documented in `next.config.js`'s comments so a future bump doesn't require a
    second rewrite of this file).
- **P0-5, security-review round.** A dispatched `ravenclaude-core/security-reviewer` pass on
  the above diff (mandatory per house rule) returned **blocked** — 1 real blocker, 5 concerns.
  All fixed in this same change, all re-verified live against a booted server:
  - **Blocker:** a bare nonced `style-src` authorizes inline `<style>` *elements* only, not
    `style=""` *attributes* — exactly what `RevenueChart.tsx` and Recharts emit at runtime.
    Would have collapsed the chart to 0px height. Fixed with the correct CSP Level 3 split
    (`style-src-attr 'unsafe-inline'` + a `style-src-elem 'self'` that's tighter than before,
    prod-only).
  - `CUBE_API_ORIGIN` was interpolated raw into the CSP header — a value containing `;` could
    inject an early directive, since CSP honors only the first occurrence of each one. Fixed
    with a `safeOrigin()` validator (`URL`-parsed, origin-only, safe fallback); verified live
    that an injection payload correctly falls back rather than reaching the header.
  - The Next middleware matcher was unanchored (`api` matched `/apidashboard`, not just
    `/api/`) and dropped the *whole* CSP, not just the nonce, on excluded/prefetch paths.
    Fixed: only truly static assets are excluded from running the middleware; `/api/*` and
    prefetches now get a real, nonce-free baseline CSP instead.
  - The rate-limiter sweep bounds the number of keys but not a single key's array under a
    sustained flood (O(n²) CPU, unbounded per-key growth the sweep can't reclaim). Fixed:
    `isRateLimited` returns before pushing once already over the ceiling, in both starters.
  - Added `X-Content-Type-Options: nosniff` to all `/api/cube-token` response paths.
  - `astro.config.mjs`'s "swap only the adapter line" portability claim went stale under the
    `process.env` fix (Workers-class targets have no usable `process.env`) — comment updated,
    not the code.
  - Added `@types/node` as an explicit Astro-starter devDependency (was only transitive).
  - Promoted the Astro starter's existing `npm audit`-recorded middleware-bypass advisory from
    a passing mention to an explicit instruction, since this diff routes more security posture
    through that same middleware channel.

**Migration:** the CSP headers moved from `next.config.js` to `middleware.ts` in the Next.js
starter — a consumer who already copied the old `next.config.js` headers() block should
delete it and adopt `middleware.ts` instead, or they'll get duplicate/conflicting CSP
headers. Both starters' env-var-reading code changed from `import.meta.env`/mixed patterns
to consistent `process.env` reads — no consumer-facing API change, but re-verify env-var
propagation if you've forked these files.

## [0.19.0] — 2026-09-03

### Fixed

- **P0-3** — `flag-data-platform-smells.sh` read only the ON-DISK file at PreToolUse, where
  the write has not happened yet: a `Write` of a new file hit an early `exit 0` (file
  doesn't exist yet), and an `Edit` introducing a violation grepped the pre-edit content.
  Reproduced and confirmed this session before the fix (a secret in `.tool_input.content`
  for a non-existent path passed silently). Rewritten to build its subject text from the
  tool payload — `.tool_input.content` (Write), `.tool_input.new_string` (Edit), each
  `.tool_input.edits[].new_string` (MultiEdit) — falling back to the on-disk file only for
  a non-Claude-Code manual invocation. Stays on **PreToolUse** (not moved to PostToolUse —
  that would have silently downgraded `DATA_PLATFORM_STRICT=1`'s exit-2 blocking control
  into a detective-only report after the write already landed; a tiebreak ruling that
  prescribed the PostToolUse move was corrected by this run's own red-team gate before
  shipping). Added an inline `additionalContext` envelope so the advisory actually reaches
  the model's context on the non-STRICT path, self-contained (no `_advise.sh` dependency —
  measured this session: 0 of 118 non-core plugins reference it). `scripts/audit-gates.sh`
  Gate 30 gained a dedicated stdin-payload fixture pair proving the fix (must-pass: fires
  on a secret in `.tool_input.content` for a file not on disk; must-pass: silent on clean
  content) — the pre-fix hook was directly confirmed to fail this exact leg.
- **P0-4** — nothing anywhere executed either app starter before this. Ran `npm ci` +
  typecheck + build by hand for both (recorded in
  `.ravenclaude/runs/forge/dashboard-top1pct/p0-4-prebuild-probe.md`) and fixed two real
  defects the probe surfaced: the Next.js starter's `/` route was missing `export const
  dynamic = "force-dynamic"`, so the build's static-prerender pass called the
  intentionally-throwing `getSession()` seam with no request in flight and failed; both
  starters had a type-only `CubeApi` import (`import cubejs, { CubeApi } from ...`) that
  should be `import cubejs, { type CubeApi } from ...` (Astro's build warned on the unused
  JS import after type-erasure). Both starters now install/typecheck/build clean. Added
  `.github/workflows/validate-data-platform-starters.yml` (non-required initially, per this
  repo's own required-status-check discipline) covering npm ci → typecheck → build → a
  headless Playwright smoke asserting zero console errors, plus `scripts/audit-gates.sh`
  Gate 264 for the Tier-1-only static check (package.json/lockfile parse + presence —
  deliberately not network-calling, since that gate is a dependency of the REQUIRED
  validate-marketplace.yml check).

**Migration:** none — the hook rewrite changes what it reads, not its advisory-by-default
contract; the two starter fixes make previously-broken builds succeed, no API change.

## [0.18.0] — 2026-09-03

### Fixed

- **P0-2 of the same FORGE gap-analysis pass** — self-description / doc-drift reconciliation.
  The plugin's own constitution was miscounting its own inventory, the exact failure mode
  CLAUDE.md §5's Capability Grounding Protocol exists to prevent in agent *output*, found in
  the plugin's own *scaffolding*: `CLAUDE.md` said "14 skills" (15 exist, `dashboard-
  architecture-audit` was the omission), `best-practices/README.md` said "31 rules" (33
  exist — `connector-rate-limit-aware-retry.md` and `deny-test-every-stack.md` were both
  written but never indexed), `CHANGELOG.md`'s top entry was two minor versions behind
  `plugin.json`, `CLAUDE.md`'s templates count was stale, `README.md`'s Status section still
  read "v0.1.0 — first ship", the 5 slash commands under `commands/` were enumerated in
  neither `CLAUDE.md` nor `README.md`, and `etl-pipeline-engineer.md` had a "Fivatran" typo
  inside a scenario `intent` field.
- Fixed all eight drifted statements, backfilled the `[0.15.0]`/`[0.16.0]` CHANGELOG entries
  this reconciliation surfaced were also missing, added a `## Commands` / `## 1a. Slash
  commands` section to both `README.md` and `CLAUDE.md`, and corrected `dashboard-builder.md`'s
  "Three cases... Case A/B/C/D... and Case E" internal contradiction to "Four cases... plus
  Case E as a separate non-framework lane."
- **New: `scripts/check-data-platform-self-description.py`** (data-platform-scoped, not
  marketplace-wide — see the script's own docstring for why) — derives each count from the
  filesystem and fails loud on drift: skills count, best-practices count, templates count,
  CHANGELOG-vs-plugin.json version freshness, and (per this run's own red-team RT-8) that the
  Cube-version-floor string P0-1 corrected stays byte-identical across all five files it
  touched, so the next Cube version boundary doesn't silently repeat P0-1's defect on a slower
  clock. Wired into `validate-marketplace.yml` and `audit-gates.sh` (Gate 263, with its own
  must-pass/must-fail fixture pair).

**Migration:** none — doc + script fixes only; no template, skill, or agent behavior changed.

## [0.17.0] — 2026-09-03

### Fixed

- **P0-1 of a FORGE gap-analysis pass** (`/forge` run `dashboard-top1pct`, standard depth — G0 through
  G8, red-team included). The critic gate (G4a) found a pre-existing, security-relevant defect:
  `templates/cube-schema-starter.yml` claimed a "Cube 0.36+" floor while depending on `access_policy`
  (Data Access Policies) unconditionally. WebSearch-verified: `access_policy` requires Cube Core
  **>=1.2.0** — below that floor it is a no-op the server does not implement, and a schema that "has"
  one is silently unenforced. Corrected the floor everywhere it was stated (`cube-schema-starter.yml`,
  both app starters' READMEs, `skills/cube-schema-scaffolding/SKILL.md`, `dashboard-builder.md`'s
  opinions list).
- Bumped `@cubejs-client/core` + `@cubejs-client/react` together `0.35.0` → `1.7.33` in both app
  starters (the two packages are hard-pinned to each other in the real npm registry; leaving the
  client on `0.35.x` while stating the `>=1.2.0` server floor would have shipped a version-mismatched
  starter). Added `engines.node >=18.17.0` to both `package.json`s and `@astrojs/check` to the Astro
  starter's `devDependencies` (previously missing). Generated and committed `package-lock.json` for
  both starters (previously absent).
- Documented, not fixed: this pass's own `npm audit` on the regenerated lockfiles found the pinned
  `next@14.2.x` and `astro@4.15.x` majors carry real high/moderate-severity CVEs not patched within
  their own major line (fix requires `next@16.3.4` / `astro@7.3.0`, both breaking bumps) — recorded
  honestly in both starters' READMEs rather than silently left or claimed fixed. **Migration:** the
  `@cubejs-client/*` bump is additive (API-compatible within the 1.x line vs 0.35.x's usage here); no
  action needed unless a consumer had vendored a copy of the 0.35.x client separately.

## [0.16.0] — 2026-09-03

### Added

- **`templates/cube-astro-dashboard-starter/`** — Astro-islands port of the Case C Next.js starter,
  for the more common shape at this shop: a mostly-static site with a Cube-backed widget or two,
  which is architecturally closer to Case A/B than to a dedicated always-interactive SaaS app.
  `KpiCard.tsx`/`RevenueChart.tsx` are reused **unchanged** from the Next.js starter (plain React, no
  framework coupling); the Astro-specific plumbing (an `APIRoute` token endpoint, CSP via middleware
  instead of `next.config.js` `headers()`) carries over the same reviewed security patterns but has
  **not itself** been independently re-reviewed. `dashboard-builder.md` now asks the shape question
  ("mostly-static-with-widgets vs. dedicated app") before defaulting to either starter.
- **`skills/dashboard-architecture-audit/SKILL.md`** — a page-by-page rubric across three axes this
  plugin had no coverage for: structure/information architecture, narrative/storytelling, and user
  guidance toward action (distinct from `dashboard-visual-craft-2026.md`'s per-widget visual craft,
  `dashboard-performance-tuning`'s latency budgets, `visual-feedback-loop`'s pixel-correctness, and
  `security-reviewer`'s auth scope). Reuses `visual-feedback-loop`'s existing render-and-see mechanism
  rather than building a second one. Wired into `dashboard-builder`'s Output Contract as a mandatory
  gate — a build with open P0/P1 audit findings is `status: partial`, never `status: complete`, for
  both new builds and standalone "harden this dashboard" requests.
- **`templates/dashboard-audit-report-template.md`** — the priority-tagged (P0-P3) output shape for
  the new audit skill.

**Migration:** none — both additions are new surfaces; no existing template or skill was renamed or
removed.

## [0.15.0] — 2026-09-03

### Added

- **`templates/cube-nextjs-dashboard-starter/`** — a real, runnable Next.js App Router + Tremor +
  Recharts Case C (productized SaaS) scaffold wired to the existing `cube-schema-starter.yml` and
  `jwt-issuer.ts` templates, with a documented (not yet CI-executed) cross-tenant denial test
  procedure.
- Promoted the three seam-marked embed stubs to real, compiling code:
  **`templates/superset-embed-iframe.tsx`**, **`templates/metabase-interactive-embed.tsx`**,
  **`templates/power-bi-embedded-react.tsx`**. The original `.tsx.md` files are kept as seam
  rationale/history, now carrying a promotion banner.

### Fixed

- `ravenclaude-core/security-reviewer`'s first pass on the promoted code returned a **blocked**
  verdict: a client-controlled tenant scope in the Superset and Power BI embed seams (`tenantId` /
  `EffectiveIdentity` composed client-side and passed unvalidated into the RLS clause / DAX identity),
  and a secret/client-component colocation risk in the Metabase seam. All three fixed in this same
  change:
  - **`templates/superset-guest-token-endpoint.ts`** (new) — the only caller of Superset's guest-token
    endpoint; resolves `tenantId` server-side and validates its shape before it reaches the RLS clause.
    `superset-embed-iframe.tsx` no longer carries a `tenantId` prop.
  - **`templates/pbi-embed-token-endpoint.ts`** — narrowed to `{workspaceId, reportId, datasetId}`;
    `EffectiveIdentity` now resolved via a server-side session seam and refused when `roles` is empty
    (a roleless identity previously fails open with no row filter). `power-bi-embedded-react.tsx` no
    longer carries `tenantId`/`daxRole` props.
  - **`templates/metabase-embed-url.server.ts`** (new, `import "server-only"` as its first line) —
    split out of the client component so the signing secret can't ship to the browser.
  - Plus the review's secondary findings on the new Cube starter: CSP `headers()`, `no-store` +
    rate-limiting on `/api/cube-token`, and a real (not just claimed) token-refresh short-circuit in
    `lib/cube-client.ts`.
- ⛔ **The fixes have not themselves been re-reviewed** — the reviewer's recommended path was
  "rewrite, then re-submit"; the rewrite happened, the re-review has not. Both starters' READMEs state
  this explicitly rather than claiming a clean bill of security health.

**Migration:** any prior consumer copy of the seam-marked `.tsx.md` stubs' original single-file shape
(pre-split) should re-pull the promoted files — the props contract changed (`tenantId`/`daxRole` props
removed from all three client components).

## [0.14.4] — 2026-09-01

### Added

- **`knowledge/dashboard-visual-craft-2026.md`** — dashboard-specific visual/UX craft (information hierarchy, one-dominant-KPI + whitespace + status-only color, chart-type selection — avoid pie/3D/gauge, prefer bar/sparkline — and the WCAG 2.2 accessibility floor), closing the gap between framework selection (`embedded-analytics-landscape-2026.md`) and latency budgets (`dashboard-performance-tuning`): neither addressed *taste*. Sourced via an adversarially-verified `rc-deep-research` pass — 5 of the extracted claims survived skeptical refutation; the pass explicitly found no claim about the React/D3/Recharts/Tremor/Cube/Evidence.dev/shadcn tool landscape survived verification, so this file stays scoped to craft and does not touch stack recommendations. Wired into `dashboard-builder.md` (Surface area + References) and cross-linked from `web-design/knowledge/design-references.md`'s dashboard mention, mirroring the `design-clone`↔`web-design` cross-plugin precedent. **Migration:** none — additive knowledge file.

## [0.14.3] — 2026-08-28

### Added

- **`skills/airbyte-cdk-authoring/SKILL.md`** — agent-consumed playbook for custom Airbyte connectors (monthly skill-gap audit #821). Promotes `/build-incremental-connector` so spawned `connector-developer` loads it. Retargeted `edtech-lms-connector-gap.md` off `connector-configuration`. **Migration:** none.

## [0.14.2] — 2026-08-14

### Changed

- Dropped hand-maintained artifact-count literals from the plugin description (D1). The roster enumerates itself; Gate 206 forbids the digit.

## [0.14.0] — 2026-06-24

OAuth-app / credential **registration walkthroughs** per ELT source — the connector docs stated the auth *mechanism* ("Connected App + OAuth 2.0", "OAuth 2.0 Authorization Code") but never how to register the app in the provider's developer portal, or who's allowed to.

### Added

- **`skills/connector-configuration/SKILL.md`** — a "Register the app" pointer under QuickBooks, Salesforce, HubSpot, Shopify, and GA4 (portal URL + who can do it + link to the knowledge-doc walkthrough). Made explicit that **Stripe is an API key, not an OAuth app** (restricted-key creation, no portal registration).
- **Per-connector knowledge docs** — a "Registering the app (developer portal)" subsection added to `quickbooks-online-integration.md` (developer.intuit.com), `salesforce-integration.md` (App Manager → Connected App), `hubspot-integration.md` (Private App vs marketplace OAuth app), `shopify-integration.md` (custom app vs Partner app), and `ga4-integration.md` (BigQuery-export link needs no app; Data API uses a service account / OAuth client, cross-linking the Google SSO walkthrough). Each names the **role/permission required** and is marked `[verify-at-build]` per the files' existing refresh-trigger discipline.

### Notes

- Secrets stay a **reference** (env-var name / vault URI), never a literal — consistent with the plugin's `flag-data-platform-smells.sh` hook.
- Companion to the `auth-identity` 0.3.0 social-provider walkthroughs (same "someone has to register the app — here's how, and whether you can" framing).

## [0.13.2] — 2026-06-22

Version bump previously unlogged here (rolls up `0.12.0` → `0.13.2`); the change that set `0.13.2`:

- Repo review autonomous fixes + B1–B6 deferred items + dead-regex CI guard (#449)

## [0.12.0] — 2026-06-05

Value-add build-out against the full menu — closing the net-new gaps left after PR #315 (which consolidated the knowledge decision-trees + `best-practices/` + `templates/`). Every menu item dispositioned; see [`CLAUDE.md`](CLAUDE.md) § "Value-add completeness (build-out 2026-06-05)".

### Added

- **scenarios/ bank enabled (4 field notes).** 3 net-new dated, scope-tagged, unverified engagement narratives — `scd-type-2-overwrite-lost-history` (overwrite destroys unrecoverable history; model Type-2 before the first run), `embedded-rls-leak-via-cube-securitycontext` (enforce the tenant filter in the semantic layer from a verified JWT claim, never the client query; ship the denial test even though the Postgres RLS hook won't fire), `warehouse-cost-blowout-dashboard-launch` (pre-aggregate + lower auto-suspend + isolate dashboard compute — sizing-down alone masks the symptom) — joining the pre-existing `elt-backfill-double-counted-rows`. Matches the `scenarios/README.md` index + 9-field schema. CLAUDE.md §8b TODO block replaced with the enabled-bank section.
- **2 new Mermaid decision trees** in `knowledge/data-platform-decision-trees.md`: **dimension history (SCD Type-1/2/3 + snapshot)** and **warehouse cost control (FinOps)**. Each complements an existing tree (dbt-materialization → load cost; dashboard-performance → latency) without duplicating it; grounded, cited, dated, and corroborated by two of the new scenarios.
- **CLAUDE.md §8c — technical-runtime tier** (LSP + MCP disposition) and the value-add completeness table.

### Decisions (recorded, not built)

- **No bundled MCP server (recommend-not-bundle).** Every warehouse/DB MCP server (Snowflake-Labs first-party, Postgres) is per-tenant + authenticated — a connection string is a secret — so all fail the doctrine's zero-config + read-only bar. Documented the recommended setup + `ravenclaude-core/security-reviewer` gate; flagged the archived/deprecated Anthropic `@modelcontextprotocol/server-postgres` reference. No invented servers, no `mcpServers` entry, no `NOTICE.md`.
- **No `.lsp.json` (recommend-with-config).** The only real SQL language server, `sqls` (v0.2.45, 2026-01-07 `[verify-at-use]`), needs a live credentialed DB connection for its useful features and is pre-1.0 / no stable release — fails the bundle bar. TS/Python/YAML servers are generic editor setup, not data-platform-specific. Revisit if `sqls` ships a stable no-connection metadata mode.
- **No runnable `scripts/` artifact.** A warehouse-cost estimator would bake in quarterly-volatile per-engine credit rates (against the §3 #9 discipline) and duplicate the dated landscape knowledge + the new cost-control tree.
- **No `bin/`, monitors, output-styles, settings, or themes** — none cleared the "groundable + broadly valuable, doesn't duplicate the existing advisory hook / Output Contract / a neighbouring plugin" bar.
- **Skills/commands/templates/hooks coverage held sufficient** — 13 skills, 5 commands, 12 templates, 1 advisory hook; the scenarios + trees extend reach without a new agent or 14th skill (team-growth-as-knowledge house rule).

### Verify-at-use

- `sqls` v0.2.45 / install path (`go install github.com/sqls-server/sqls@latest`) and its RDBMS-connection requirement; the Snowflake-Labs MCP shape; the Anthropic postgres-reference deprecation; Cube `securityContext`/`access_policy` API naming; dbt snapshot config; all warehouse `$`/credit figures. Version-volatile — re-confirm against the vendor before quoting.

## [0.11.2] — earlier

4-agent data-platform team (database-setup-guide, etl-pipeline-engineer, dashboard-builder, connector-developer): 13 skills, 12 templates, a 24-doc knowledge bank + consolidated decision-tree file (PR #315), 21 best-practices, 5 commands, 1 advisory hook. Connector coverage across QuickBooks / Stripe / Salesforce / HubSpot / GA4 / Shopify / HRIS / Planhat / Intercom / Slack-as-source plus 8-vendor support-tool integration. Opinionated against per-viewer-priced BI for greenfield SMB.
