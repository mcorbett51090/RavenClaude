---
description: Design a Microsoft Fabric topology — traverse the store-selection tree (lakehouse / warehouse / eventhouse), decide shortcut vs mirror vs copy, lay out the medallion across workspaces, and place workloads on the right capacity.
argument-hint: "[the workload, e.g. 'land 12 source systems and serve BI + a real-time alert']"
---

# Design a Fabric topology

You are running `/microsoft-fabric:design-fabric-topology`. Lay out the Fabric stores, data movement, and workspace/capacity shape for what the user described (`$ARGUMENTS`), following this plugin's `fabric-architect` discipline — pick from the decision tree, never from habit or the word "SQL."

## When to use this

A new Fabric engagement needs its store + movement + topology decided, or an existing layout is being reviewed. For a single-lakehouse POC this is overkill — say so. If the question is "build the medallion" the design is already settled — route to `/microsoft-fabric:build-medallion-lakehouse`.

## Steps

1. **Pick each store from the decision tree:** Spark/Python or mixed/unknown skills → Lakehouse; T-SQL + multi-table ACID → Warehouse; streaming/telemetry/time-series → Eventhouse/KQL DB — never map "SQL" → Warehouse reflexively (`lakehouse-vs-warehouse-choose-from-the-tree.md`, `rti-eventhouse-for-streaming-not-lakehouse.md`). Name the branch that decided each.
2. **Walk the "do I copy?" ladder least-to-most duplication:** shortcut → auto-mirror → mirror → copy job → pipeline. Default to a shortcut when you only need to *read* data that already lives in OneLake/ADLS/S3/GCS (`one-copy-shortcut-before-copying.md`).
3. **State Mirroring's cost honestly** — "free to replicate, billed to query," plus cross-region egress; never call it simply "free" (the anti-pattern hook flags that phrasing) (same file).
4. **Lay out the medallion across workspaces:** bronze raw/immutable, silver curated, gold business-ready — each its own lakehouse/workspace so the layer boundary is also a governance boundary (`lakehouse-medallion-layer-boundaries.md`).
5. **Route streaming to an Eventhouse, additionally to a Lakehouse** only for the historical batch tail; wire Activator so a detected condition fires an action (`rti-eventhouse-for-streaming-not-lakehouse.md`).
6. **Place workloads on capacity deliberately** — interactive BI separated from heavy background jobs (`capacity-isolate-noisy-workloads.md`). Use the `templates/fabric-workspace-and-capacity-plan.md` shape.

## Guardrails

- Never duplicate data a shortcut would serve, and never serve bronze to Direct Lake or the SQL endpoint.
- Cite each capability's GA/preview status with a retrieval date — Fabric ships monthly and "preview" is a design constraint.
- This plugin is advisory: emit the topology + the `fab` CLI / KQL / T-SQL the consultant runs in their own tenant. Auth/secrets/OneLake-security design routes to `ravenclaude-core/security-reviewer`; standalone Power BI / DAX routes to `power-platform/power-bi-engineer`.
