# Changelog — microsoft-fabric

All notable changes to this plugin are documented here. Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

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
