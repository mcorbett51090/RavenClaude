# Development Pipeline Is a Portfolio, Not a Project

**Status:** Pattern
**Domain:** Renewable energy / project development
**Applies to:** `renewable-energy`

---

## Why this exists

A solar developer managing a single project at a time will consistently under-invest in early-stage site control and over-focus on the projects already deep in the queue. That is the wrong prioritization structure. At any given time a development organization holds projects at radically different risk/return profiles: pre-application sites (high optionality, low sunk cost, many), interconnection-queue projects (higher sunk cost, known schedule risk), and NTP-ready projects (high capital commitment, low development risk). The portfolio needs to be managed as a funnel with deliberate stage-gate metrics, not as a list of projects competing for the same management attention. A pipeline that doesn't replenish the early-stage cohort will run out of NTP-ready projects in 24–36 months regardless of how well the current projects execute.

## How to apply

Track the development pipeline in four stages with stage-specific metrics:

```
Development Pipeline Dashboard — [Organization] [Quarter]
──────────────────────────────────────────────────────────
Stage 1 — Site identification and early screening
  Projects in stage:        ___
  MW (DC) in stage:         ___ MW
  Average cost to date:     $___/W
  Target: enough MW to feed Stage 2 funnel (assume ___% conversion to Stage 2)

Stage 2 — Site control secured, application pending
  Projects in stage:        ___
  MW (DC) in stage:         ___ MW
  Avg. months in stage:     ___ (flag if > 6 months without queue application)
  Target conversion to Stage 3: ___% (historical: ___)

Stage 3 — In interconnection queue / permitting
  Projects in stage:        ___
  MW (DC) in stage:         ___ MW
  Expected upgrade costs (range): $___–$___M
  Avg. queue position age:  ___ months
  Key schedule risks:       [List any project-specific risks]

Stage 4 — NTP-ready / construction
  Projects in stage:        ___
  MW (DC) in stage:         ___ MW
  Financial close complete: ___  MW
  Revenue COD in next 12 months: ___ MW
```

**Portfolio health check (run quarterly):**

| Metric | Target | Actual | Signal |
|---|---|---|---|
| Stage 1 MW ÷ Stage 4 MW (replenishment ratio) | ≥ 5:1 | | Below → add early-stage sites |
| Average time Stage 2→3 (months) | < 9 | | Above → queue application process bottleneck |
| % of Stage 3 projects with upgrade cost > 15% of project cost | < 25% | | High → screen earlier for grid congestion |
| Stage 4 MW with COD in next 12 months | [Revenue target] | | Below → acceleration needed |

**Do:**
- Set a MW target for each stage and rebalance the pipeline when any stage falls below its target — a pipeline only managed from the bottom (NTP-ready) starves itself in 2–3 years.
- Model interconnection upgrade cost exposure as a portfolio total, not per-project — the aggregate first-loss exposure from upgrades across all Stage 3 projects is the real development risk number.
- Write off Stage 1 sites that don't progress to queue application within 12–18 months of site control; sunk-cost bias keeps marginal sites alive past their usefulness.
- Track the actual Stage-to-Stage conversion rate historically — a developer who assumes 50% conversion but is achieving 25% is building a materially undersized pipeline.

**Don't:**
- Report pipeline MW as a single number without stage breakdown — a pipeline of 500 MW with 480 MW in Stage 1 is not the same as one with 480 MW in Stage 4.
- Let one project dominate management attention to the point that Stage 1 site activity stops — the 24–36 month development cycle means that a pause today creates a revenue gap in 3 years.
- Include projects past their queue application deadline or with expired site control in the active pipeline — phantom MW in the pipeline produce phantom revenue projections.

## Edge cases / when the rule does NOT apply

A single-project developer building one large utility-scale project without a recurring pipeline strategy does not need a stage-gate funnel — they need a project execution plan. The portfolio framework applies to organizations whose business model requires a recurring stream of projects reaching construction.

## See also
- [`../agents/renewables-engagement-lead.md`](../agents/renewables-engagement-lead.md) — scopes the development strategy and pipeline review.
- [`../agents/solar-project-developer.md`](../agents/solar-project-developer.md) — owns the project-level development milestones within the portfolio.
- [`../knowledge/renewables-economics.md`](../knowledge/renewables-economics.md) — covers development cost structure and stage-gate economics.

## Provenance

Codifies the funnel-based pipeline management approach used by utility-scale and C&I solar developers; the stage-gate and replenishment-ratio framing is consistent with Wood Mackenzie and BloombergNEF development pipeline analysis methodology [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
