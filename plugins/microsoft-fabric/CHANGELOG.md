# Changelog — microsoft-fabric

All notable changes to this plugin are documented here. Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

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
