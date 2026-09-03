# Changelog — data-platform

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

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
