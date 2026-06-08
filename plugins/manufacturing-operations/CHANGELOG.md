# Changelog — manufacturing-operations

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

## 0.2.0 — 2026-06-08

Depth build-out to the v0.2.0 standard. No agent/skill count change (still 3 agents, 3 skills);
the surface deepened around them.

- **12 best-practices** (was 8) — added `lot-size-trades-setup-against-holding`,
  `safety-stock-is-a-decision-not-a-default`, `the-bom-must-match-as-built`, and
  `no-silent-regulated-sign-off`; `best-practices/README.md` indexes all 12.
- **Knowledge bank — 5 Mermaid decision trees** (was 3): added *how-do-I-size-this-lot
  (setup vs holding, constraint-aware)* and *where-does-this-nonconformance-disposition-stop
  (draft vs human sign-off)* alongside plan-to-constraint, TOC bottleneck, and
  special-vs-common-cause; the dated 2026 method/standard map (`[verify-at-build]`) extended.
- **Runnable calculator** — `scripts/mfg_calc.py` (stdlib only, Python 3.8+, ruff-clean on
  F,E9,B,C4,I,UP): `oee` (Availability x Performance x Quality with stated denominators +
  six-big-losses + sandbagged-ideal warning), `takt` (available time / demand vs cycle time),
  `capacity` (MRP net requirement + load vs finite/bottleneck capacity). A calculator, not a
  data source — every formula and denominator is printed and cited to a best-practice.
- **Scenarios bank — 5 dated field notes** (was 2): added *schedule that ignored the
  constraint* (infinite-capacity planning), *building ahead of takt* (over-production), and
  *tampering with a stable process* (special vs common cause). 9-field schema, `reviewed: false`.
- CLAUDE.md milestone + count reconciliation; plugin.json bumped 0.1.0 → 0.2.0 with the
  best-practices count corrected to 12.

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
