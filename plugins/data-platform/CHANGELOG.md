# Changelog — data-platform

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.13.1] — 2026-06-22

Version bump previously unlogged here (rolls up `0.12.0` → `0.13.1`); the change that set `0.13.1`:

- feat: add developer-tooling, data-orchestration & startup-fundraising plugins (+ 10-candidate roadmap) (#460)

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
