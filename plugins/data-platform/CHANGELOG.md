# Changelog — data-platform

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.14.2] — 2026-07-09

Snowflake AI/Cortex billing correction — as of **2026-04-01** Snowflake bills Cortex/AI in a **separate AI Credit currency at a flat rate ($2.00/credit global, $2.20 regional), edition-independent**; only Platform Credits (warehouse compute/storage) stay edition-priced. (Retrieved 2026-07-09; release-note 2026-04-06.)

### Changed

- **`knowledge/cloud-database-landscape-2026.md`** — added a dated AI-Credit note to the Snowflake section (source: `docs.snowflake.com/en/release-notes/2026/other/2026-04-06-ai-services-billing-breakout`; `[verify-at-use — pricing, subject to change; primary /pricing 403'd, secondary-sourced]`).
- **`knowledge/snowflake-psm-dashboard-cost-model.md`** — corrected the stale edition-dependent Cortex-credit estimate ("~30 credits ≈ $60–90 depending on edition") to the flat, edition-independent AI-Credit model, pointing to the dated figure in the capability map rather than embedding a price. `[verify-at-use]`

### Notes

- Provenance stated inline: the primary `docs.snowflake.com/.../pricing` page 403'd automated fetch; the claim is cross-referenced via secondaries plus the 2026-04-06 release note.
- No permanent price embedded in the cost model — it references the dated capability-map figure per the plugin's quarterly-volatility discipline (§3 #9).

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
