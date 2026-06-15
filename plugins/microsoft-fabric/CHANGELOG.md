# Changelog — microsoft-fabric

All notable changes to this plugin are documented here. Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.8.2] — 2026-06-15

Research-sweep **correction** — bring the dedicated OneLake-security doc in line with the GA reality that PR #411 (0.8.1) already applied to the capability map but left stale in `onelake-security-and-governance.md`. Re-verified 2026-06-15 against `learn.microsoft.com` via the Microsoft-Learn MCP.

### Fixed

- **`knowledge/onelake-security-and-governance.md`** — removed the now-false "OneLake-security data **preview**" framing: OneLake security (data-access roles + RLS/CLS/OLS) is **GA and default-on (May 2026)**; what remains **public preview** is only Eventhouse RLS and authorized third-party-engine enforcement. Added a Status callout, the supported-item-types table (Lakehouse Read/**ReadWrite**, Azure Databricks Mirrored Catalog Read, Mirrored Databases Read), the **DefaultReader residual-access gotcha**, and the **authorized-engine model** detail (`principalAccess` API) replacing the vague "third-party engines / partial / preview" row. Corrected "schema-enabled lakehouses are **required**" → recommended-not-required (schemaless RLS/CLS works via `spark.sql.fabric.catalog.enable-schemaless-lakehouses=true`). Restamped **Last reviewed: 2026-06-15**.
- **`CLAUDE.md`** — house-opinion #14 updated to match (GA + default-on; schema-enabled is the recommended-not-required path; schemaless escape hatch noted). `[verify-at-use]`.
- Version **0.8.1 → 0.8.2** in `.claude-plugin/plugin.json` + `marketplace.json` (lockstep).

## [0.8.1] — 2026-06-11

Research-sweep **corrections** — two now-false facts in the capability map, re-verified 2026-06-11 against `learn.microsoft.com` via the Microsoft-Learn MCP.

### Fixed

- **`knowledge/fabric-2026-capability-map.md`** — **Fabric Runtime 2.0 is Spark 4.1 / Delta 4.1 / Python 3.13** (was documented as Spark 4.0 / Delta 4.0). Added the **breaking-change** note (Python 3.12→3.13 requires re-publishing every Environment that has libraries). Source: [Runtime 2.0](https://learn.microsoft.com/fabric/data-engineering/runtime-2-0). (Runtime 2.0 remains public preview — unchanged.)
- **`knowledge/fabric-2026-capability-map.md`** — **OneLake security + OneLake data access roles are GA (May 2026)** and being **enabled by default on all supported items by end of May 2026** (was documented as "preview"). Corrected the supported data items (Lakehouse, Azure Databricks Mirrored Catalog, Mirrored Databases), added the **ReadWrite** permission and the **authorized-engine model** for third-party enforcement (was "third-party engines preview"). Source: [Fabric what's-new](https://learn.microsoft.com/fabric/fundamentals/whats-new), [data access control model](https://learn.microsoft.com/fabric/onelake/security/data-access-control-model).
- **`knowledge/medallion-on-onelake.md`** — Native Execution Engine GA note: Runtime 2.0 is **Spark 4.1** (was Spark 4.0).
- Version **0.8.0 → 0.8.1** in `.claude-plugin/plugin.json` + `marketplace.json` (lockstep).

## [0.7.0] — 2026-06-05

Value-add build-out — closes the net-new gaps after PR #315 (which had consolidated the knowledge decision-trees + `best-practices/` + `templates/` and stubbed the scenarios index).

- **Scenarios bank enabled (4 scenarios).** Authored the four dated, scope-tagged engagement narratives the pre-existing `scenarios/README.md` index already referenced (the files were the gap): capacity-CU throttling (background-rejection collision → isolate-before-scale), Direct Lake → DirectQuery fallback (Warehouse RLS forced it), OneLake shortcut medallion modeling (shortcut-first), deployment-pipeline ALM autobind break (missing data-source rule). 9-field marketplace schema; each maps to an existing best-practice rule; every GA/preview-sensitive fact dated + `[verify-at-use]`. CLAUDE.md §8a flipped from TODO to enabled.
- **1 new diagnostic decision-tree file (2 trees).** `knowledge/direct-lake-fallback-triage-decision-tree.md` — a mode-aware **Direct Lake misbehaving (fell-back / errored / empty)** triage tree + a **semantic-model refresh/framing failure** triage tree. Complements #315's *selection* trees (which had no *diagnostic* tree).
- **Bundled MCP — `microsoft-learn`.** The official Microsoft Learn MCP Server (`microsoftdocs/mcp`, remote streamable HTTP `https://learn.microsoft.com/api/mcp`) — bundled because it is the one Microsoft-ecosystem server that is **no-auth, free, read-only, no-install**, and on-mission for the "cite GA/preview with a date" discipline. Declared in `plugin.json` `mcpServers` + top-level `x-mcpAttribution` (third-party) + new `NOTICE.md`. **Recommend-not-bundle:** Fabric RTI MCP (`microsoft-fabric-rti-mcp`) + Fabric MCP (`Fabric.Mcp.Server`) — both credentialed + write-capable (documented `claude mcp add` paths + `security-reviewer` gate). All package names/endpoints/verbs verified against Microsoft Learn + GitHub 2026-06-05.
- **Runnable capacity helper.** `scripts/fabric_capacity_calc.py` (stdlib only, ruff-clean) — `sku-fit` / `smoothing` / `isolation`. **No prices baked in** (CU is a capability figure; cost left to the Azure Pricing Calculator).
- **CLAUDE.md** gained a "## Value-add completeness (build-out 2026-06-05)" dispositioning table (every menu item BUILT or honest N-A) and the rewritten §11 (bundled-Learn-MCP doctrine block + operational-server recommend-not-bundle table).

### Migration
- On `/plugin marketplace update`, consumers gain the bundled `microsoft-learn` MCP server, which **auto-connects** (remote HTTP, no auth, no cost). If `learn.microsoft.com` is unreachable or denied by `web-access.yaml`, it shows `failed` in `/mcp` (loud-but-non-fatal) — Claude Code and all other tools keep working. No prerequisite to install; no other behavior changes.

## [0.1.0] — 2026-05-28

Initial release. A Microsoft Fabric specialist team built from a researched, expert-reviewed plan (see [`docs/microsoft-fabric-plugin-analysis.md`](../../docs/microsoft-fabric-plugin-analysis.md) and [`docs/microsoft-fabric-build-plan.md`](../../docs/microsoft-fabric-build-plan.md)).

- **7 agents:** `fabric-architect`, `lakehouse-engineer`, `warehouse-engineer`, `data-factory-engineer`, `realtime-intelligence-engineer`, `fabric-semantic-model-engineer`, `fabric-admin`.
- **8-doc knowledge bank** (citation-grounded, retrieval-dated 2026-05-28): store-selection + data-movement Mermaid decision trees, medallion-on-OneLake, Direct Lake (two-mode), capacity FinOps + throttling, OneLake security (GA/preview matrix), ALM/CI-CD, and a dated 2026 capability map.
- **6 templates:** workspace-and-capacity plan, medallion-lakehouse spec, ingestion design, Direct Lake semantic-model spec, capacity-cost review, ALM runbook.
- **1 advisory hook** (`check-fabric-anti-patterns.sh`, `FABRIC_STRICT=1` to block) with **14 house opinions**.
- **Seams:** reciprocal handoff with `data-platform` (enterprise-Microsoft here vs non-Microsoft/SMB embedded there); the `power-platform/power-bi-engineer` litmus test (Delta/storage-mode here vs measure/visual/`.pbix` there); `applied-statistics` for "is it real?".
- Requires `ravenclaude-core@>=0.7.0`. No bundled MCP — documents the `fab` CLI / REST prerequisite.

### Deferred to a later version
- `fabric-data-ai-engineer` (notebooks/MLflow/AutoML, Fabric Data Agents, Operations Agents, Copilot, AI functions).
- A `skills/` directory (procedures promoted from `/wrap` feedback) and a `scenarios/` bank (first real engagement scenario).
