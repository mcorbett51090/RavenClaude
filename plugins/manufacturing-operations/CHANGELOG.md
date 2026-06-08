# Changelog — manufacturing-operations

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

## 0.1.0 — 2026-06-08

Initial release. The plan / make / control operations layer for discrete and process manufacturing.

- **3 agents** — `production-planner` (MRP/MPS, demand-vs-capacity, S&OP, BOM management, lot sizing, finite scheduling),
  `shop-floor-and-oee-analyst` (OEE with defined denominators, throughput, takt vs cycle time, Theory-of-Constraints
  bottleneck analysis, MES/downtime data), `quality-and-capa-lead` (SPC, NCR/CAPA, inspection plans, FMEA, supplier
  quality, control plans). Each carries the full scenario-authoring frontmatter.
- **3 skills** — `mrp-and-production-planning`, `oee-and-throughput`, `capa-and-spc`.
- **Knowledge bank** — `manufacturing-operations-decision-trees.md`: Mermaid trees (plan-to-constraint, TOC bottleneck
  identification, special-vs-common-cause control-chart signal) + a dated 2026 method/standard map (MRP/MPS, OEE, takt,
  TOC, NCR/CAPA, SPC, ISO 9001 / IATF 16949) (`[verify-at-build]`).
- **8 best-practices**, **3 commands** (`plan-production`, `analyze-oee`, `run-capa`),
  **2 templates** (production-plan brief, CAPA report), **1 advisory hook**
  (`check-manufacturing-operations-anti-patterns.sh`; `MFG_STRICT=1` to make it blocking), and a **scenarios bank**.
- Seams: process redesign → `process-improvement`; inferential stats / Gage R&R → `applied-statistics`; sourcing →
  `procurement-sourcing`; distribution → `fleet-logistics`. Requires `ravenclaude-core@>=0.7.0`.
