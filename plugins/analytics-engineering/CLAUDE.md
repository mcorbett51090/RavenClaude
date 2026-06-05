# Analytics Engineering (dbt) Plugin — Team Constitution

> Team constitution for the `analytics-engineering` Claude Code plugin — **3** specialist agents for the transformation layer between raw warehouse data and trustworthy analytics — dbt modeling (staging -> marts), a governed semantic layer, and data-quality tests/contracts -- distinct from data-platform's ingestion/BI and database-engineering's OLTP. The Team Lead (the top-level Claude session, typically also running `ravenclaude-core`) dispatches the right specialist(s) and integrates their reports.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).


---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`analytics-engineer`](agents/analytics-engineer.md) | dbt modeling: the staging/intermediate/marts layering, materialization choice, incremental models, the Kimball-vs-OBT decisions, model structure, refs/sources, and warehouse-aware SQL | "model this in dbt", "our dbt project is a mess", "should this be incremental?", "build the marts for this domain" |
| [`semantic-layer-engineer`](agents/semantic-layer-engineer.md) | The governed semantic/metrics layer: one definition per metric (revenue, active user, churn), metrics-as-code (dbt Semantic Layer / MetricFlow or equivalent), dimensions/entities, and the contract every BI tool consumes | "define our metrics once", "different dashboards show different revenue", "set up the semantic layer", "what's our definition of active user?" |
| [`data-quality-testing-engineer`](agents/data-quality-testing-engineer.md) | Data quality in the transform layer: dbt tests (not_null/unique/accepted_values/relationships), source freshness, model contracts, custom/singular tests, anomaly detection, and gating the warehouse in CI and production | "add data quality tests", "bad data reached the dashboard", "set up model contracts", "check source freshness" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.


## 2. Cross-cutting house opinions (every agent enforces)

1. **One definition per metric, defined once.** 'Revenue', 'active user', 'churn' have a single governed definition in the semantic/metrics layer — not re-derived differently in every dashboard. Metric drift is the silent killer of trust in analytics.
2. **Transform in layers: staging -> intermediate -> marts.** Staging cleans and renames one source; intermediate composes; marts are the business-facing models. A 600-line model that does everything is untestable and unownable.
3. **Test the data like code.** Not-null, unique, accepted-values, relationships, and freshness tests run in CI and in production. Untested transformations ship silent corruption to every downstream consumer.
4. **Materialize by the trade, not by habit.** View (cheap storage, recompute on read), table (fast read, full rebuild), incremental (big append-mostly facts). Choosing wrong wastes compute or serves stale/slow data.
5. **Models are owned and documented.** Every model has an owner, a description, column docs, and tests. An undocumented mart is a mystery the business will misuse.
6. **Don't reinvent ingestion or OLTP.** This layer transforms what's already landed in the warehouse — ingestion is data-platform's, the transactional store is database-engineering's. Stay in the transform lane.

## 3. Seams (the bridges to neighbouring plugins)

- **Ingestion/ELT into the warehouse and the warehouse choice/provisioning** → `data-platform` (Airbyte/Fivetran, warehouse selection); this team transforms what's landed.
- **The transactional OLTP database (schema, indexes, migrations)** → `database-engineering`; we work in the analytics warehouse (OLAP), not the app's DB.
- **BI/dashboards consuming the marts and semantic layer** → `tableau` / `data-platform` (embedded analytics).
- **Enterprise Microsoft lakehouse / Direct Lake semantic models** → `microsoft-fabric` (we're the warehouse-neutral dbt lane).
- **Statistical validity of a metric ('is this difference real?')** → `applied-statistics`; we ensure the number is *correct and consistent*, they say if it's *significant*.

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol (decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the dated capability map.

## 5. Knowledge & scenario banks

Two banks back the agents (the dual-bank model — see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)):

- **Canonical / knowledge** (high trust, follow without disclaimer): [`knowledge/analytics-engineering-decision-trees.md`](knowledge/analytics-engineering-decision-trees.md) (materialization, model-layer, star-vs-OBT, freshness-gate, metric-placement, DQ-failure-triage, incremental-strategy, semantic-tool) and [`knowledge/data-quality-and-contract-decision-trees.md`](knowledge/data-quality-and-contract-decision-trees.md) (which dbt test expresses a guarantee; model-contract-vs-test-vs-both at a boundary). **Traverse the relevant Mermaid tree top-to-bottom before choosing** — the proactive complement to the Capability Grounding Protocol.
- **Scenarios** (low/medium trust, surface with the mandatory unverified preamble): [`scenarios/`](scenarios/) — field notes (fan-out join double-counting, incremental late-arriving data, semantic-layer metric drift, test-coverage gap → silent corruption). Secondary source; never replaces the knowledge bank or a freshly-verified warehouse fact. Likeliest beneficiaries: `analytics-engineer` (modeling/incremental), `semantic-layer-engineer` (metric drift), `data-quality-testing-engineer` (coverage gap).

## 6. Technical-runtime tier — LSP code intelligence (recommend-not-bundle, N-A for the dbt file type)

Analytics engineering is a **code** domain (SQL + Jinja + YAML), so an LSP was evaluated — but unlike a compiled-language plugin (e.g. `backend-engineering` ships an `.lsp.json` for Pyright/tsserver/gopls), **this plugin ships no `.lsp.json`**, and the decision is deliberate, not an omission:

- **The dbt primary file type is Jinja-templated SQL.** A dbt model is `.sql` containing `{{ ref('...') }}`, `{{ source(...) }}`, `{% if is_incremental() %}` — *not* executable SQL until dbt compiles it. A generic SQL LSP parses the raw text and chokes on the Jinja, giving false diagnostics rather than real go-to-definition across `ref()` lineage (which is dbt's own DAG, not an LSP concept).
- **`sqls`** ([`sqls-server/sqls`](https://github.com/lighttiger2505/sqls), MIT, Go) `[verify-at-use]` is a real SQL LSP, but it (a) connects to a **live database** — a per-tenant connection string is a *secret* (`docs/best-practices/bundled-mcp-servers.md` "reference-not-literal"), (b) was **pre-1.0 / under active development** with documented breaking changes when last checked, and (c) is not Jinja/dbt-aware. Fails the zero-config + read-only bar on the secret alone.
- **`sqlfluff-lsp`** ([`VasanthakumarV/sqlfluff-lsp`](https://github.com/VasanthakumarV/sqlfluff-lsp), MIT) `[verify-at-use]` wraps SQLFluff and *is* dbt-Jinja-aware via the dbt templater, giving real lint diagnostics — but it needs a **per-project `.sqlfluff`** (dialect + templater + dbt project dir) and `sqlfluff` on `PATH`, so it can't be shipped zero-config, and it provides lint diagnostics, not the cross-file navigation a compiled-language LSP gives.

**Disposition: recommend-not-bundle.** Consumers who want in-editor dbt-SQL linting run SQLFluff (with its LSP or its pre-commit/CI hook) configured to *their* dialect + dbt project — there is no warehouse-neutral, zero-config `.lsp.json` this plugin could ship without guessing the consumer's dialect and project layout. The real lineage intelligence for dbt is `dbt compile` + the manifest DAG, not an LSP. Re-evaluate if a zero-config, dbt-Jinja-native LSP appears.

> Verified 2026-06-05 via web research: `sqls` (sqls-server/sqls, MIT, Go, pre-1.0, live-DB-backed); `sqlfluff-lsp` (VasanthakumarV, MIT, wraps SQLFluff, dbt-templater-aware, per-project `.sqlfluff` required); SQLFluff 4.0.x optional Rust routines. Package names, maintenance status, and the LSP support version are volatile — re-confirm at use.

## 7. Bundled MCP server — `dbt-mcp` is recommend-not-bundle

This plugin **bundles no MCP server**, on purpose. Per [`../../docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md), a bundled server must be **zero-config and read-only by default**; a per-consumer-configured, authenticated, or write-capable server is **recommend-not-bundle**.

| Server | Why recommend-not-bundle | Recommended setup `[verify-at-use]` |
|---|---|---|
| **dbt MCP** ([`dbt-labs/dbt-mcp`](https://github.com/dbt-labs/dbt-mcp), Apache-2.0, **first-party from dbt Labs**) | **First-party from the vendor** *and* **per-tenant + authenticated** (needs a dbt project dir and, for the platform tools, a dbt Platform host + API token = a secret) *and* **write-capable** — its dbt-CLI tools can `run`/`build`, and the repo warns the tools "could modify your data models, sources, and warehouse objects." Three independent disqualifiers; the doctrine routes first-party-OR-authenticated-OR-write-capable straight to recommend-not-bundle. | Consumer-configured, secret as a **reference** (env-var name / vault URI, never a literal), pin the tested version, and **disable the write-capable CLI tools unless explicitly needed** (the server exposes `DISABLE_*` toggles `[verify-at-use]`). Gate adoption of the write tools through `ravenclaude-core/security-reviewer`. Local install via `uvx dbt-mcp==<tested-version>` `[verify-at-use]`. |

**Why not bundle it (the load-bearing reasoning):** the dbt MCP server is the obvious, genuinely-useful candidate — but it is first-party from dbt Labs (reference the published artifact, don't vendor), it requires a consumer-specific project dir and a credentialed dbt Platform token for its remote tools (a secret → reference-not-literal), and its CLI tools are write-capable against the warehouse (an Absolute-rule `security-reviewer` gate before any consumer ships the write verbs). Every one of those independently sends it to **recommend-not-bundle**. We document the `uvx`/`claude mcp add` path and the `DISABLE_*` least-privilege posture instead of shipping an `mcpServers` entry. **No invented servers.**

> Verified 2026-06-05 via web research + the dbt-mcp PyPI/GitHub listings: `dbt-mcp` latest `1.20.1` (released 2026-06-04), Apache-2.0, 60+ tools across CLI / Semantic Layer / Discovery / docs, write-capable (CLI tools can modify warehouse objects), local (`uvx`/`pip install dbt-mcp`) and remote (HTTP to dbt Platform) flavors, an experimental `.mcpb` bundle per release. Version, tool count, and the exact env-var/`DISABLE_*` names are volatile — re-confirm against the repo's `.env.example` and docs.getdbt.com before quoting.

## 8. Value-add completeness (build-out 2026-06-05)

Disposition of every value-add menu item (built vs. recorded N-A with reason). This build-out extends PR #315 (which added the consolidated knowledge decision-trees, `best-practices/`, and `templates/`); the net-new gap closed here is the **scenarios bank** and the **runtime-tier dispositioning** (MCP + LSP).

| # | Item | Disposition |
|---|---|---|
| 1 | **scenarios/ bank** | **BUILT** — 4 field notes (fan-out join double-counting, incremental late-arriving data, semantic-layer metric drift, test-coverage gap → silent corruption) matching the existing `scenarios/README.md` index + 9-field schema. The README + index pre-existed (PR #315 staged it); this build wrote the four narrative files it pointed at. |
| 2 | **Decision-tree knowledge** | **BUILT** — `knowledge/data-quality-and-contract-decision-trees.md`: two new Mermaid trees (which dbt test expresses a guarantee; model-contract-vs-test-vs-both at a boundary) + a dated capability note. Chosen because PR #315's `analytics-engineering-decision-trees.md` already covers materialization / model-layer / star-vs-OBT / freshness / metric-placement / DQ-triage / incremental-strategy / semantic-tool — the test-type-selection and contract-enforcement decisions were the gaps, and the test-type tree is the natural complement to the existing DQ-failure-triage tree. |
| 3 | **Bundled MCP server** | **N-A (recommend-not-bundle)** — §7. The obvious candidate, the first-party `dbt-mcp` (dbt Labs, Apache-2.0), fails the bundling bar on three independent counts: first-party-from-vendor, per-tenant + authenticated (a dbt Platform token = a secret), and write-capable (CLI tools can modify warehouse objects). Documented the `uvx` / `claude mcp add` path + `DISABLE_*` least-privilege posture + `security-reviewer` gate instead. No invented servers. |
| 4 | **LSP server** | **N-A (recommend-not-bundle)** — §6. dbt's primary file type is Jinja-templated SQL, which generic SQL LSPs can't navigate (the lineage is dbt's compiled DAG, not an LSP concept). `sqls` is live-DB-backed (secret) + pre-1.0 + not Jinja-aware; `sqlfluff-lsp` is dbt-Jinja-aware but needs a per-project `.sqlfluff` (dialect + project dir), so it can't ship zero-config. No warehouse-neutral `.lsp.json` is shippable without guessing the consumer's dialect — recommended SQLFluff (LSP or pre-commit/CI) instead. |
| 5 | **Runnable script (`scripts/`)** | **N-A** — no stdlib-only calculator clears the "real value, doesn't duplicate an existing surface" bar. The high-value runtime checks for this domain (incremental correctness, grain/cardinality, test coverage, freshness) are *dbt's own* (`dbt build`, `dbt test`, `dbt source freshness`, model contracts) and SQLFluff's — a hand-rolled Python script would either re-implement dbt badly or operate on a project layout we can't assume. The advisory hook + the `run-the-dbt-project-in-ci` best-practice point consumers at the real runtime. |
| 6 | **bin/ / monitors / output-styles / settings / themes** | **N-A** — no groundable, broadly-valuable instance. A SQL/dbt linter `bin/` would duplicate SQLFluff + the advisory hook; there is no long-running process to monitor (builds are dbt-orchestrated); deliverables are governed by the agents' Output Contract, not an output-style; the plugin is config-light by design. |
| 7 | **skills/hooks/commands/templates** | **Coverage sufficient** — 5 skills (dbt-modeling, semantic-metrics-layer, data-quality-testing, incremental-model-patterns, dbt-ci-governance), 4 commands, 4 templates, 1 advisory hook already cover modeling, the semantic layer, testing, incrementals, and CI governance. The new scenarios + second decision-tree file extend reach without a new agent or skill (team-growth-as-knowledge house rule); a 6th skill would gold-plate. |
| 8 | **CHANGELOG.md** | **BUILT** — added with a top entry for this build-out. No `NOTICE.md` (nothing third-party is bundled; `dbt-mcp`/`sqls`/`sqlfluff-lsp` are referenced + cited, not vendored). |

## 9. Milestones

- **v0.2.x** — initial analytics-engineering team: 3 agents (analytics-engineer, semantic-layer-engineer, data-quality-testing-engineer), 5 skills, the consolidated decision-tree knowledge bank, 12 best-practices, 4 templates, 4 commands, 1 advisory hook (PR #315 added the consolidated knowledge trees + best-practices + templates).
- **next bump** — value-add build-out: scenarios bank (4 field notes), a second topic-specific decision-tree file (test-type selection + contract-vs-test enforcement), and the runtime-tier dispositioning (dbt-mcp + LSP recorded recommend-not-bundle with cited, dated research). CHANGELOG added.
