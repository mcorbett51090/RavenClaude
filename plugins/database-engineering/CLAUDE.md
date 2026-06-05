# Database Engineering Plugin — Team Constitution

> Team constitution for the `database-engineering` Claude Code plugin — **4** specialist agents for designing and operating the transactional data layer well — relational schema and normalization, indexing and query performance, safe zero-downtime migrations, and connection/transaction reliability — distinct from the analytics/ELT layer. The Team Lead (the top-level Claude session, typically also running `ravenclaude-core`) dispatches the right specialist(s) and integrates their reports.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).


---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`schema-architect`](agents/schema-architect.md) | Logical and physical schema design: normalization to 3NF and deliberate denormalization, keys and constraints (PK/FK/UNIQUE/CHECK/NOT NULL), data types, relationships, and the model that keeps data correct | "design the schema for this", "should I denormalize this?", "model this domain in Postgres", "are these the right constraints?" |
| [`query-performance-engineer`](agents/query-performance-engineer.md) | Query and index tuning: reading EXPLAIN/ANALYZE plans, choosing the right index type (B-tree/partial/composite/covering/GIN), fixing slow queries, killing N+1 at the SQL level, and partitioning large tables | "this query is slow", "what index do I need?", "read this EXPLAIN plan", "our table is huge and queries crawl" |
| [`migration-engineer`](agents/migration-engineer.md) | Safe schema evolution: expand/contract (parallel-change) migrations, zero-downtime ALTERs, backfills, online index creation, migration tooling and ordering, and reversibility | "migrate this schema safely", "add a NOT NULL column without downtime", "this migration locked the table", "how do I rename a column live" |
| [`db-reliability-engineer`](agents/db-reliability-engineer.md) | Operational reliability: connection pooling, transaction/isolation discipline, replication and read replicas, backup/restore (tested), failover/HA, vacuum/bloat management, and observability of the database | "set up connection pooling", "which isolation level?", "add read replicas", "is our backup/restore solid?" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.


## 2. Cross-cutting house opinions (every agent enforces)

1. **Model for correctness first (normalize), denormalize deliberately.** Start at 3NF; denormalize only with a measured read-performance reason and the write/consistency cost named. Premature denormalization is data corruption with extra steps.
2. **The query plan is the truth.** Read `EXPLAIN (ANALYZE)` before adding an index or rewriting a query. Guessing at performance is how you add five useless indexes and miss the one that matters.
3. **Indexes are not free.** Each one speeds reads and slows writes and costs storage. Index for the actual query patterns; an unused index is pure overhead.
4. **Migrations are expand/contract and reversible.** Add-nullable → backfill → switch reads → drop-old, in separate deploys. A blocking `ALTER` on a hot table mid-deploy is an outage.
5. **Constraints belong in the database.** FKs, NOT NULL, UNIQUE, CHECK — the database is the last line of defense for integrity, and application code is not a reliable enforcer.
6. **Transactions are short and isolation is chosen, not defaulted.** Long transactions hold locks and bloat; know your isolation level and what anomalies it permits.

## 3. Seams (the bridges to neighbouring plugins)

- **Analytics warehouse, ELT pipelines, and embedded BI** → `data-platform`; this team owns the OLTP/transactional store, that one owns OLAP. The litmus: serves the app's reads/writes → here; feeds dashboards → there.
- **The dbt transformation layer on top of the warehouse** → `analytics-engineering`.
- **The application's ORM usage, data-access layer, and N+1 in app code** → `backend-engineering` (we own the schema/index/plan; they own how the app calls it).
- **Provisioning the managed database (RDS/Cloud SQL/Azure DB), HA topology, parameter groups** → the cloud plugin; we own logical design + tuning.
- **Schema migrations as part of a progressive rollout** → coordinate with `devops-cicd/release-engineer` (expand/contract sequences with the deploy).

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol (decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the dated capability map.

## 5. Knowledge & scenario banks

Two banks back the agents (the dual-bank model — see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)):

- **Canonical / knowledge** (high trust, follow without disclaimer): [`knowledge/database-engineering-decision-trees.md`](knowledge/database-engineering-decision-trees.md) (index choice, migration safety, normalize/denormalize, SQL-vs-NoSQL, scaling reads, isolation level, partial index, online NOT NULL add — plus the dated capability map) and [`knowledge/oltp-olap-and-read-routing-decision-trees.md`](knowledge/oltp-olap-and-read-routing-decision-trees.md) (OLTP-vs-OLAP workload placement — the `data-platform` seam as a decision — and per-read routing across replicas). **Traverse the relevant Mermaid tree top-to-bottom before choosing** — the proactive complement to the Capability Grounding Protocol.
- **Scenarios** (low/medium trust, surface with the mandatory unverified preamble): [`scenarios/`](scenarios/) — field notes (slow-query/missing-composite-index, online NOT NULL add lock storm, replication lag / stale reads after failover, connection-pool exhaustion with PgBouncer). Secondary source; never replaces the knowledge bank.

## 6. Technical-runtime tier — LSP code intelligence (bundled config, binary installed separately)

Database engineering is a **code/SQL** domain, so the plugin ships an [`.lsp.json`](.lsp.json) (referenced from `plugin.json` `lspServers`) giving agents real-time SQL code intelligence — completion against the schema, hover, and diagnostics — instead of grep-and-guess over `.sql` files. Verified against the [Claude Code plugins reference](https://code.claude.com/docs/en/plugins-reference) (LSP servers section, 2026-06-05): `.lsp.json` maps a server name to `{command, args, extensionToLanguage}`, `transport` defaults to `stdio`, and **the plugin ships the config, not the binary**.

| Language | Server | `command` | Install (consumer, separate) |
|---|---|---|---|
| SQL | [`sqls`](https://github.com/sqls-server/sqls) (MIT, Go) | `sqls` | `go install github.com/sqls-server/sqls@latest` `[verify-at-use]` |

**Why `sqls`:** it is a maintained (v0.2.45, 2026-01-07, MIT), single-binary SQL language server covering Postgres / MySQL / SQLite / MSSQL — the engines this plugin leans on — over the standard stdio LSP transport. Per the plugins reference: "LSP plugins configure how Claude Code connects to a language server, but they don't include the server itself." If the `sqls` binary isn't on `PATH`, the `/plugin` Errors tab shows `Executable not found in $PATH` and SQL intelligence degrades — Claude Code and every other tool keep working (the same **loud-but-non-fatal** posture as a missing MCP prerequisite). `/reload-plugins` is needed to pick up a config change mid-session.

> **Note for full schema-aware features:** `sqls` provides syntax/keyword completion and diagnostics from the config alone, but live *schema* completion (table/column names) requires the consumer to point `sqls` at a database via its own `~/.config/sqls/config.yml` — a per-tenant, credentialed step we deliberately do **not** ship (a connection string is a secret; same reasoning as the MCP table below). The bundled config enables the zero-config features; the consumer opts into schema-aware features with their own credentials. `[verify-at-use]` — confirm the `sqls` config path and the `go install` module path at use; both are version-volatile.

## 7. Recommended (not bundled) MCP servers — database context

This plugin **bundles no MCP server**, on purpose. Per [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md), a bundled server must be **zero-config and read-only by default**. Every database-useful server needs a **connection string (a secret) and is per-tenant** — both disqualify bundling, and a secret stays a **reference (env-var name / vault URI), never a literal**. So we document the recommended `claude mcp add …` paths, gated through `ravenclaude-core/security-reviewer`, instead of shipping an `mcpServers` entry.

| Server | Why recommend-not-bundle | Recommended setup `[verify-at-use]` |
|---|---|---|
| **Postgres MCP Pro** ([`crystaldba/postgres-mcp`](https://github.com/crystaldba/postgres-mcp), open source) | The most domain-relevant server (database health checks, index tuning, `EXPLAIN`-plan analysis, hypothetical-index simulation) — but it is **per-tenant + needs a connection string (secret)**. It has a **Restricted (read-only) Mode** limiting it to read-only transactions for production, which is the mode to use — but the secret + per-tenant config still send it to recommend-not-bundle. | Consumer-configured, `--access-mode=restricted` (read-only), connection string as a **reference** (env-var name / vault URI), `security-reviewer` sign-off before adoption. `[verify-at-use]` — confirm the flag name + read-only guarantees at adoption. |
| **MCP Toolbox for Databases** ([`googleapis/mcp-toolbox`](https://github.com/googleapis/mcp-toolbox), Apache-2.0, formerly genai-toolbox) | Google's actively-maintained (v0.28.0, 2026-03) multi-database MCP server; lists Claude Code as a supported client. Same disqualifier: **per-tenant + credentialed**, and its power is a custom-tools framework that needs configuration. | Consumer-configured with a least-privilege read-only DB role, secret as a **reference**, scoped tool definitions, `security-reviewer` sign-off. |
| **`@modelcontextprotocol/server-postgres` (Anthropic reference)** | **Do NOT recommend.** Archived/deprecated (2025-07-10, moved to `modelcontextprotocol/servers-archived`) after Datadog found a SQL-injection vuln that bypassed its read-only restriction; the fix never shipped. Listed here only to steer consumers *away* from it (it still has ~21k weekly npm downloads). | — (use a maintained server above instead). |

**Why none are bundled (the load-bearing reasoning):** every useful DB MCP server handles a **connection string** (a secret → Absolute-rule "reference-not-literal") and is **per-tenant** (can't hardcode) — the doctrine's decision table sends "per-consumer config OR write-capable OR secret-handling" to **recommend, don't bundle**. Read-only mode (Postgres MCP Pro's Restricted Mode, a least-privilege role for the Toolbox) is the *floor* for recommending one at all, plus a `security-reviewer` gate. If a genuinely zero-config, read-only, secret-free DB server ever appears, revisit with the doctrine block in [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md) Step 4.

> Verified 2026-06-05 (web): the `@modelcontextprotocol/server-postgres` deprecation + archival + the Datadog SQL-injection finding (securitylabs.datadoghq.com; modelcontextprotocol/servers-archived); Postgres MCP Pro's read/write + restricted access modes (crystaldba/postgres-mcp README); MCP Toolbox v0.28.0 + Claude Code client support (googleapis/mcp-toolbox; googleapis.github.io/genai-toolbox). Package names, versions, archival status, and flag names are volatile — re-confirm at use.

## Value-add completeness (build-out 2026-06-05)

Disposition of every value-add menu item (built vs. recorded N-A with reason). This build-out followed PR #315 (which added the consolidated `database-engineering-decision-trees.md`, `best-practices/`, and `templates/`); the net-new gap was the scenarios bank + the technical-runtime tier (MCP/LSP).

| # | Item | Disposition |
|---|---|---|
| 1 | **scenarios/ bank** | **BUILT** — 4 scenarios (slow-query/missing-composite-index, online NOT NULL add lock storm, replication lag / stale reads after failover, connection-pool exhaustion with PgBouncer) matching the existing `scenarios/README.md` index + 9-field schema. The README already listed these 4 (added in #315); this build-out wrote the files themselves. |
| 2 | **Decision-tree knowledge** | **BUILT** — `knowledge/oltp-olap-and-read-routing-decision-trees.md`: OLTP-vs-OLAP workload placement (the `data-platform` seam as a decision) + per-read routing across replicas. Chosen to **complement** #315's trees (index/migration/normalize/SQL-NoSQL/scaling/isolation/partial-index/online-NOT-NULL) — these two were the gaps and draw the neighbouring-plugin seams. |
| 3 | **Bundled MCP server** | **N-A (recommend-not-bundle)** — §7. No DB server clears the zero-config + read-only + secret-free bar: every useful one (Postgres MCP Pro, Google MCP Toolbox) is per-tenant + handles a connection-string secret. Documented the recommended `claude mcp add` paths (read-only mode + secret-as-reference + `security-reviewer` gate) and explicitly steer away from the **deprecated/vulnerable** Anthropic `@modelcontextprotocol/server-postgres` reference. No invented servers. |
| 4 | **LSP server** | **BUILT** — `.lsp.json` (`sqls`, MIT, maintained), wired via `plugin.json` `lspServers`. Genuinely useful for a SQL domain; binary installs separately (§6). Zero-config features work from the bundled config; schema-aware completion needs a consumer credential we don't ship. |
| 5 | **Runnable script under scripts/** | **N-A** — the connection-pool sizing math is already delivered as formulas + a worked example + a `pgbouncer.ini` template in the `connection-pool-tuning` skill, and index/bloat estimation is a live `EXPLAIN`/`pg_stat_statements`/catalog-query task (data is in the DB, not computable offline). A standalone calculator would duplicate the skill or invent numbers that only the live catalog has. |
| 6 | **bin/ / monitors / output-styles / settings / themes** | **N-A** — no groundable, broadly-valuable instance. A monitor would need a live DB connection (per-tenant secret, same disqualifier as MCP); an output-style would overlap the agents' Output Contract. Config-light by design. |
| 7 | **skills/hooks/commands/templates** | **Coverage sufficient** — 6 skills, 4 commands, 4 templates, 1 advisory hook already cover schema design, query/index tuning, safe migrations, pool tuning, and reliability. The new read-routing decision tree slots into the existing knowledge bank rather than needing a new skill. |
| 8 | **CHANGELOG.md** | **BUILT** — added with a top entry for this build-out. No `NOTICE.md` (nothing third-party is bundled — the LSP binary and MCP servers install separately on the consumer's machine). |
