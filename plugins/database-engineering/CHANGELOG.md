# Changelog — database-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.3.1] — 2026-06-22

Weekly news-cadence sweep correction (Tier-A, `data_and_bi`). See [`docs/research/2026-06-22-weekly-sweep-findings.md`](../../docs/research/2026-06-22-weekly-sweep-findings.md).

### Fixed

- **Anchored the vague "current major" PostgreSQL row in the capability map.** `knowledge/database-engineering-decision-trees.md` listed PostgreSQL as "GA, current major" — now resolvable to a concrete, verifiable anchor: **PG18 (GA 2025-09-25)**, kept `[verify-at-build]`. Tightens an imprecise dated-fact cell to the actual current major without changing any guidance.

## [0.3.0] — 2026-06-05

Value-add build-out — the scenarios bank + the technical-runtime tier, following PR #315 (which added the consolidated decision-tree knowledge file, `best-practices/`, and `templates/`). Every value-add menu item is dispositioned (built or recorded N-A with reason); see [`CLAUDE.md`](CLAUDE.md) § "Value-add completeness (build-out 2026-06-05)".

### Added

- **scenarios/ bank (4 field notes).** `slow-query-missing-composite-index` (one composite ordered equality→equality→range beats one index per column), `online-add-not-null-column-lock-storm` (expand/contract + batched backfill + NOT VALID/VALIDATE, never one coupled statement), `replication-lag-stale-reads-after-failover` (route by freshness need; raise failover durability deliberately), `connection-pool-exhaustion-pgbouncer` (transaction-mode pooler sized to DB vCPU, not a higher `max_connections`). Matches the `scenarios/README.md` index and the 9-field schema (the README's index was added in #315; this release wrote the files).
- **Decision-tree knowledge.** `knowledge/oltp-olap-and-read-routing-decision-trees.md` — two Mermaid trees: OLTP-vs-OLAP workload placement (the `data-platform` seam drawn as a decision) and per-read routing across replicas (operationalizing the replication-lag rule). Complements #315's trees (index/migration/normalize/SQL-NoSQL/scaling/isolation/partial-index/online-NOT-NULL).
- **LSP code-intelligence config.** `.lsp.json` (referenced from `plugin.json` `lspServers`) configuring `sqls` (MIT, maintained — Postgres/MySQL/SQLite/MSSQL) for `.sql` files. Ships the config, not the binary; the binary installs separately (loud-but-non-fatal if missing). Schema-aware completion needs a consumer-provided `sqls` DB config (a per-tenant credential we don't ship). Verified against the Claude Code plugins reference (2026-06-05).
- **CLAUDE.md** §5 (knowledge & scenario banks), §6 (LSP tier), §7 (recommended-not-bundled MCP servers), and the value-add completeness disposition table.

### Decisions (recorded, not built)

- **No bundled MCP server.** Every database-useful MCP server is per-tenant + handles a connection-string secret, so none clears the doctrine's zero-config + read-only + secret-free bar. Documented the recommended `claude mcp add …` paths — Postgres MCP Pro (`crystaldba/postgres-mcp`, Restricted/read-only mode) and Google's MCP Toolbox for Databases (`googleapis/mcp-toolbox`) — each with secret-as-reference and a `security-reviewer` gate. Explicitly steer consumers **away** from the deprecated/vulnerable Anthropic `@modelcontextprotocol/server-postgres` reference (archived 2025-07-10 after a SQL-injection finding). No invented servers.
- **No `scripts/` calculator** — pool sizing is already covered by the `connection-pool-tuning` skill's formulas + `pgbouncer.ini` example; index/bloat estimation is a live-catalog (`EXPLAIN` / `pg_stat_statements`) task, not an offline computation.
- **No `bin/`, monitors, output-styles, or themes** — a monitor would need a per-tenant DB secret (same disqualifier as MCP); the rest don't clear the "groundable + broadly valuable, doesn't duplicate an existing surface" bar.
- **Skills/commands/templates/hooks coverage held sufficient** — the new read-routing tree slots into the knowledge bank rather than needing a new skill.

### Verify-at-use

- The `sqls` `go install github.com/sqls-server/sqls@latest` module path and current version; the `sqls` config-file path for schema-aware features; Postgres MCP Pro's `--access-mode=restricted` flag + read-only guarantees; the MCP Toolbox version (0.28.0) + Claude Code client support; the Postgres synchronous-replication / LSN-pinning incantations referenced in the scenarios. All version-volatile — re-confirm against the vendor before quoting.

## [0.2.2] — earlier

4-agent database-engineering team (schema-architect, query-performance-engineer, migration-engineer, db-reliability-engineer): 6 skills, a consolidated decision-tree knowledge bank (index choice + migration safety + normalize/denormalize + SQL-vs-NoSQL + scaling reads + isolation + partial index + online NOT NULL add, plus a dated 2026 capability map), 22 best-practices, 4 templates, 4 commands, 1 advisory hook. Seams to data-platform (analytics/ELT), analytics-engineering (dbt), backend-engineering (ORM/data-access), and the cloud plugins (managed DB infra).
