# Plugin candidate research & roadmap — 2026-06-17

A scheduled research pass over the marketplace gap surface. At the time of writing the
marketplace shipped **101 plugins**; this pass identified **10 candidate plugins** absent
from that roster, prioritized them by user demand × technical feasibility × non-overlap,
and began the build-out of the three P0 candidates.

## Method

- Enumerated the full installed roster (`ls plugins/` + `.claude-plugin/marketplace.json`).
- Mapped each candidate against the existing roster to confirm it is a **genuine gap**, not
  a slice already owned by a shipping plugin, and recorded the **seam** to the nearest
  neighbors so a new plugin deepens rather than duplicates.
- Scored on three axes: **demand** (how often the domain shows up in real engagements),
  **feasibility** (can it be built to the marketplace's CI-passing quality bar without
  external services), and **overlap** (distance from the nearest existing plugin).

## The 10 candidates

| # | Plugin | Purpose | Nearest neighbor / seam | Priority |
|---|--------|---------|-------------------------|----------|
| 1 | **trust-and-safety** | Content-moderation policy, abuse/fraud/spam detection engineering, human-review ops, enforcement measurement | classifier validity → applied-statistics; PII → data-governance-privacy; ATO → security-engineering | **P0 — built** |
| 2 | **geospatial-engineering** | GIS/spatial data engineering — PostGIS, SRID/projections, spatial SQL, vector tiles, MapLibre, routing/GDAL | warehouse → data-platform; OLTP → database-engineering; consumed by precision-agriculture & fleet-logistics | **P0 — built** |
| 3 | **developer-relations** | DevRel/advocacy — DX strategy, sample apps & quickstarts, community, the developer funnel + DevRel metrics | docs site → technical-writing-docs; API design → api-engineering; positioning → product-management | **P0 — built** |
| 4 | **pricing-monetization** | SaaS pricing & packaging strategy — value metric, tiering, willingness-to-pay research, monetization experiments | what-to-build → product-management; billing plumbing → fintech-payments-engineering | P1 |
| 5 | **quantitative-trading-engineering** | Backtesting frameworks, market-data engineering, execution/OMS, risk & PnL attribution | advisory/portfolio → wealth-management-ria; corporate finance → finance | P1 |
| 6 | **xr-spatial-computing** | AR/VR/XR engineering — Unity/Unreal XR, WebXR, visionOS/ARKit, spatial UX, performance budgets | 2D/3D games → game-development; native mobile → mobile-engineering | P1 |
| 7 | **bioinformatics-engineering** | Genomics/omics pipelines — Nextflow/Snakemake, sequence alignment, variant calling, reproducible workflows | generic analysis → data-science-research; trials → clinical-trials | P2 |
| 8 | **robotics-ros-engineering** | ROS 2 robotics — nodes/topics/services, navigation/SLAM, sim (Gazebo), real-time control | device firmware → embedded-iot-engineering | P2 |
| 9 | **technical-due-diligence** | Code/architecture/eng-org DD for M&A & investment — scorecards, risk findings, remediation costing | eng health (internal) → engineering-management; security audit → security-engineering | P2 |
| 10 | **event-management** | Conference & event operations — run-of-show, vendor/venue, budget, registration, sponsor & speaker ops | project delivery → project-management; field events → marketing-operations | P2 |

## Prioritization rationale

- **P0 (build first)** — the three with the strongest demand-feasibility product and the
  cleanest non-overlap. All three are **domain-neutral or broadly horizontal** (apply across
  many of the existing verticals), buildable entirely from durable domain knowledge with no
  external service dependency, and have a crisp seam to their nearest neighbor.
- **P1** — high-value but more specialized audiences (`pricing-monetization`,
  `quantitative-trading-engineering`, `xr-spatial-computing`). Each carries more volatile,
  citation-hungry facts (live market structure, headset SKUs, pricing benchmarks) that want
  a dated/citation pass to meet the accuracy discipline.
- **P2** — niche or heavier to do justice (`bioinformatics-engineering`,
  `robotics-ros-engineering`, `technical-due-diligence`, `event-management`). Real demand but
  a narrower audience and, for the first two, a deep tooling surface.

## Build status (this pass)

- **Built to CI-passing baseline:** `trust-and-safety`, `geospatial-engineering`,
  `developer-relations` — each ships `plugin.json` + `README.md` + `CLAUDE.md`, 2 agents
  (full scenario-authoring frontmatter), 3 skills, a 2-doc knowledge bank with a Mermaid
  decision tree, 2 templates, 3 best-practices, and 1 advisory hook. Wired into
  `marketplace.json` and the `docs/architecture.md` Status table.
- **Scoped for follow-up:** candidates 4–10 above, each a self-contained future PR following
  the same scaffold. They are intentionally **not** stub-committed — an empty plugin
  directory would fail the structural-claims gate and ship a blank card.

## Next steps

1. Land the P0 PR.
2. Take P1 (`pricing-monetization` first — broadest audience) as the next build, with the
   volatile-fact citation pass its content needs.
3. Re-run this gap scan after each batch; the roster moves.
