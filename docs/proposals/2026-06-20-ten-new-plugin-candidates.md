# Ten New Plugin Candidates for RavenClaude

_Authored 2026-06-20 by `claude` (scheduled routine). Status: research + prioritization, with the #1 candidate built in the same PR._

## Context

The marketplace already ships **102 plugins** (101 before this PR), with deep coverage of the software-delivery chain, the three clouds, the data/AI stack, the Microsoft stack, and ~50 business/healthcare/finance/real-estate verticals. "New plugin" therefore means **genuine white space** — a domain with durable, groundable knowledge that no existing plugin owns and that has real demand. Each candidate below was checked against the existing roster (`plugins/` + `.claude-plugin/marketplace.json`) to confirm it is not already covered.

Every candidate is scoped to the marketplace's house style: a small team of advisory *doing*-agents (it never forks core's review roles), a decision-tree knowledge bank, best-practices, templates, commands, and one advisory hook — inheriting `ravenclaude-core` protocols.

## The 10 candidates

| # | Candidate | One-line purpose | Closest existing (why it's still a gap) |
|---|---|---|---|
| 1 | **geospatial-gis-engineering** ✅ BUILT | Location-aware systems: spatial storage, CRS, spatial SQL, map tiling | `database-engineering`/`data-platform` (no spatial/CRS/tiling coverage) |
| 2 | **computer-vision-engineering** | Image/video ML: detection, segmentation, OCR, data pipelines, edge inference | `ml-engineering` (generic MLOps, no CV-specific craft) |
| 3 | **email-deliverability-engineering** | Getting mail to the inbox: SPF/DKIM/DMARC, warmup, reputation, sending infra | `marketing-operations` (campaigns, not deliverability mechanics) |
| 4 | **browser-extension-engineering** | Chrome/Firefox extensions: Manifest V3, content scripts, service workers, store review | `frontend-engineering`/`desktop-app-engineering` (extension model is distinct) |
| 5 | **content-marketing-engine** | SEO content + editorial ops: briefs, topic clusters, content calendar, measurement | `marketing-operations` (broader ops); `web-design` content strategist (per-site) |
| 6 | **wordpress-cms-engineering** | WordPress builds done right: themes/blocks, plugins, performance, security hardening | none (huge install base, no CMS plugin) |
| 7 | **event-management** | Conferences/webinars/field events: budget, run-of-show, sponsorship, logistics | `project-management` (generic delivery, not event craft) |
| 8 | **grant-management** | Post-award grant compliance: budgets, reporting, allowable costs, audit trail | `nonprofit-fundraising` (pre-award/development side) |
| 9 | **physical-therapy-rehab-clinic** | Outpatient rehab ops: scheduling, plan-of-care docs, billing units, compliance | `behavioral-health-practice` (mental health), `medical-revenue-cycle` (RCM only) |
| 10 | **optometry-eyecare-practice** | Eye-care practice ops: exam workflow, optical/dispensary, recall, payor mix | `dental-practice`/`veterinary-practice` (different practice model) |

## Per-candidate implementation approach & dependencies

All inherit `ravenclaude-core@>=0.7.0`; none bundles an MCP server in v1 (per the bundled-MCP doctrine). "Agents" below means advisory doing-agents.

1. **geospatial-gis-engineering** — 3 agents (architecture / spatial data / app), 5 skills, 4 Mermaid decision trees, dated stack map, 10 best-practices, advisory hook (non-sargable filters, area-in-3857, unknown SRID, no-typmod). Deps: durable OGC/PostGIS/EPSG/RFC-7946 knowledge — no external service. **Built in this PR.**
2. **computer-vision-engineering** — agents for the CV pipeline (data/annotation, training, serving/edge). Decision trees: task→architecture, edge-vs-cloud inference. Deps: stable CV literature; seams to `ml-engineering`. Feasible, but overlaps `ml-engineering` enough to need careful seam-drawing.
3. **email-deliverability-engineering** — 2-3 agents (auth/DNS, reputation/warmup, infra). Decision trees: SPF/DKIM/DMARC alignment, dedicated-vs-shared IP. Deps: very durable (RFCs); high pain, niche. Strong standalone build.
4. **browser-extension-engineering** — agents for MV3 architecture + store submission. Decision trees: MV3 permission model, content-script vs service-worker. Deps: MV3 is volatile (carries verify-at-use); seams to `frontend-engineering`.
5. **content-marketing-engine** — agents for strategy, production, measurement. Templates: content brief, topic cluster, calendar. Deps: durable; risk of overlap with `marketing-operations` (must be the *content engine*, not all of marketing).
6. **wordpress-cms-engineering** — agents for build (block themes/Gutenberg), extension (plugins/hooks), and ops (performance/security). Deps: large but versioned surface; clean gap.
7. **event-management** — agents for planning, logistics/run-of-show, sponsorship/revenue. Deps: durable practice; seams to `project-management`.
8. **grant-management** — agents for budget/compliance, reporting, audit. Deps: durable (Uniform Guidance etc., carry citations); complements `nonprofit-fundraising` cleanly.
9. **physical-therapy-rehab-clinic** — agents for clinical ops, documentation/compliance, billing. Deps: vertical knowledge with payor/compliance citations; seams to `medical-revenue-cycle`.
10. **optometry-eyecare-practice** — agents for clinical/exam ops, optical/dispensary, front-office/recall. Deps: vertical; mirrors `dental-practice` structure.

## Prioritization rationale (demand × feasibility)

**Tier 1 — build first (high demand, clean groundable build, strong seams):**
- **#1 geospatial-gis-engineering** — pervasive demand (every logistics, real-estate, public-sector, field-service, precision-ag product touches maps/location), durable standards (OGC/PostGIS/EPSG/RFC 7946), and it slots cleanly beside the existing engineering plugins with five ready-made seams (`database-engineering`, `data-platform`, `frontend-engineering`, `fleet-logistics`, `precision-agriculture`). Highest demand-feasibility product → **built in this PR.**
- **#3 email-deliverability-engineering** and **#2 computer-vision-engineering** — high demand, durable knowledge; #3 edges ahead on standalone clarity (RFC-anchored, no overlap), #2 needs the most seam-drawing against `ml-engineering`.

**Tier 2 — strong, slightly more overlap or volatility:**
- **#6 wordpress-cms-engineering** (clean gap, large surface), **#4 browser-extension-engineering** (MV3 volatility), **#5 content-marketing-engine** (overlap risk with `marketing-operations`).

**Tier 3 — solid verticals, narrower demand:**
- **#8 grant-management**, **#7 event-management**, **#9 physical-therapy-rehab-clinic**, **#10 optometry-eyecare-practice** — valuable, citation-heavy vertical builds; lower cross-cutting demand than the engineering tier, so scheduled after Tier 1/2.

## Progress in this PR

- **Built (#1):** `plugins/geospatial-gis-engineering/` — 3 agents, 5 skills, 2 knowledge docs (4 Mermaid trees + dated stack map), 10 best-practices, 3 templates, 3 commands, 1 advisory hook, CLAUDE.md / README.md / CHANGELOG.md, marketplace + architecture + README wiring. Validated against the local gate suite.
- **Documented (#2–#10):** the candidate list above is the backlog; each is a follow-up PR sized to the same structure.

## Blockers / notes

- None blocking. The single risk for the engineering-tier follow-ups (#2, #4, #5) is **seam discipline** — they must deepen, not duplicate, `ml-engineering` / `frontend-engineering` / `marketing-operations`; the candidate notes call out the boundary for each.
