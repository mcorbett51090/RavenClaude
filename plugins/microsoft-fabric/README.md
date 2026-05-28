# microsoft-fabric

A Microsoft Fabric specialist team for Claude Code — seven agents that bring decision-tree-driven, citation-grounded Fabric judgment to enterprise Microsoft data-and-analytics engagements.

## What it is

Microsoft Fabric is a big, fast-moving platform (it ships monthly), and the hard part of a Fabric engagement is rarely the typing — it's the **decisions**: lakehouse or warehouse? mirror or copy? which Direct Lake mode? why is the capacity throttling? This plugin encodes those decisions as a team of advisory specialists backed by an 8-doc knowledge bank whose every claim is grounded in Microsoft Learn with a retrieval date.

The agents are **advisory and interactive**: your Fabric tenant lives outside the repo, so they recommend the design and emit runnable `fab` CLI / KQL / T-SQL / PySpark / Power Query snippets you run yourself.

## The team

| Agent | Owns |
|---|---|
| `fabric-architect` | workspace/domain/capacity topology, store selection, shortcut/mirror/copy, medallion design |
| `lakehouse-engineer` | Lakehouse, Spark/Delta/V-Order/NEE, medallion, materialized lake views, gold-shaping for Direct Lake |
| `warehouse-engineer` | Fabric Warehouse T-SQL, dimensional modeling, multi-table ACID, SQL endpoint, perf |
| `data-factory-engineer` | ingestion: Mirroring, Copy job, pipelines, Dataflow Gen2, Eventstream; incremental/CDC |
| `realtime-intelligence-engineer` | Eventstream → Eventhouse → KQL → Real-Time dashboard → Activator; anomaly detection |
| `fabric-semantic-model-engineer` | Direct Lake semantic models (on-OneLake vs on-SQL), framing, fallback, PBIP/TMDL |
| `fabric-admin` | capacity FinOps, OneLake security (two planes), domains/Purview, ALM (Git + deployment pipelines + Fabric CLI) |

Plus: an 8-doc knowledge bank (two Mermaid decision trees + medallion / Direct Lake / capacity / security / ALM references + a dated 2026 capability map), 6 templates, and 1 advisory anti-pattern hook (14 house opinions).

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install microsoft-fabric@ravenclaude
/reload-plugins
```

Requires `ravenclaude-core@>=0.7.0` (inherits the Capability Grounding + Structured Output protocols).

## Prerequisite

No bundled MCP. Fabric automation uses the **Fabric CLI** (`pip install ms-fabric-cli`), **fabric-cicd**, and the **Fabric REST APIs** (Microsoft Entra auth). The agents recommend and emit the commands; you run them with your own credentials. See [`knowledge/fabric-alm-cicd.md`](knowledge/fabric-alm-cicd.md).

## How it relates to the other plugins

- **`power-platform/power-bi-engineer`** — standalone Power BI reports / DAX / `.pbix`. This plugin owns the Fabric storage layer + Direct Lake model underneath. *Measure/visual/`.pbix` → power-bi-engineer; Delta tables / storage mode / fallback → here.*
- **`data-platform`** — non-Microsoft, SMB, cost-sensitive, embedded-in-app analytics (Cube/Evidence/Metabase). Enterprise Microsoft/Fabric → here.
- **`applied-statistics`** — "is this Fabric metric movement real?"

See [`CLAUDE.md`](CLAUDE.md) §10 for the full seam wording.

## Versioning

Semver; bump on every user-visible change and keep `.claude-plugin/plugin.json` in sync with the catalog entry in `.claude-plugin/marketplace.json`. Because Fabric ships monthly, the dated capability map (`knowledge/fabric-2026-capability-map.md`) is re-reviewed on each Researcher staleness sweep.
