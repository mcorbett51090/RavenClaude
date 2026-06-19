# New plugin candidates — research & prioritization (2026-06-19)

> **Audience:** anyone working *on* the RavenClaude marketplace. This doc is the research deliverable behind the "identify 10 new plugins" task. It enumerates 10 gap-filling plugin candidates, scores them by demand × feasibility, and records which one was built first.
>
> **Method note:** the existing roster (101 plugins as of `marketplace.json` v0.86.0) was enumerated from `ls plugins/` and the marketplace catalog. Candidates below were chosen to be **genuinely uncovered** (no existing plugin owns the lane) and to lean on **principle-stable knowledge** an agent team can carry without volatile facts going stale. Demand is a qualitative read of how often the lane shows up in engineering/consulting work, marked `[ESTIMATE]` — not a measured signal.

## What's already covered (so we don't rebuild it)

The marketplace already owns the software-delivery chain (devops-cicd, observability-sre, security-engineering, qa-test-automation, cloud-native-kubernetes, terraform-iac, platform-engineering-idp, performance-engineering), the three clouds, app craft (backend / frontend / mobile / desktop / embedded-iot / game / api / auth / database), the data & AI stack (data-platform, analytics-engineering, data-streaming, ml-engineering, ai-rag-engineering, data-science-research, applied-statistics, search-relevance), the Microsoft stack, and ~40 business/ops verticals. The gaps below sit **outside** all of those lanes.

## The 10 candidates

| # | Candidate plugin | One-line purpose | Why it's a gap |
|---|---|---|---|
| 1 | **legacy-modernization** | The team that modernizes legacy systems safely — assess (the 6 R's), characterize before touching, strangle the monolith, migrate the data, cut over with a rollback. | No plugin owns "I have a working-but-aging system I'm afraid to change." Adjacent to backend/database/qa but none cover strangler-fig, characterization tests, or rewrite-vs-refactor. |
| 2 | **itsm-service-management** | ITIL 4 / IT service management — service desk, incident vs. problem vs. change, CMDB, SLAs, change-advisory-board. | observability-sre owns *engineering* incident response; nothing owns the *ITSM/ITIL* operating model (ticketing, change management, CAB, CMDB) that enterprise IT and MSPs run on. |
| 3 | **chaos-resilience-engineering** | Resilience verification — failure-mode hypotheses, fault injection, game days, steady-state metrics, blast-radius control. | observability-sre owns SLOs and incident response; no plugin owns *proactively breaking things* to prove resilience (chaos experiments, game-day design). |
| 4 | **gis-geospatial-engineering** | Geospatial/GIS engineering — PostGIS, spatial indexing, projections/CRS, tiling, routing, vector/raster pipelines. | A whole technical discipline with zero coverage. database-engineering is OLTP-generic; spatial has its own data types, indexes (GiST), and CRS pitfalls. |
| 5 | **digital-marketing-performance** | Paid media + SEO/SEM performance marketing — campaign structure, attribution, CAC/ROAS, keyword & content strategy. | marketing-operations is ops/martech-stack focused; nothing owns the *performance-marketing* craft (PPC, ROAS, attribution models, SEO content). |
| 6 | **grant-writing-management** | Grant lifecycle — prospect research, proposal/narrative writing, budgets, logic models, reporting & compliance. | nonprofit-fundraising and public-sector-govtech touch grants but neither owns the *writing/management* craft (narratives, logic models, federal post-award compliance). |
| 7 | **developer-relations-advocacy** | DevRel/DX — developer onboarding funnels, sample/tutorial strategy, community, docs-as-product, dev-survey metrics. | technical-writing-docs owns docs; nothing owns DevRel as a function (developer journey, advocacy, community, DX metrics). |
| 8 | **robotics-ros-engineering** | Robotics software — ROS 2 architecture, nodes/topics/services, SLAM/navigation, real-time control, sim-to-real. | embedded-iot-engineering is firmware/device focused; ROS 2 robotics is a distinct stack (DDS, nav2, MoveIt, Gazebo). |
| 9 | **content-marketing-seo** | Editorial content engine — content strategy, topic clusters, editorial calendar, on-page SEO, repurposing. | Overlaps #5; broken out because editorial/content ops is a distinct buyer from paid-media. (Merge candidate.) |
| 10 | **bioinformatics-computational-biology** | Bioinformatics pipelines — sequence analysis, NGS workflows (Nextflow/Snakemake), variant calling, reproducible science. | clinical-trials owns the trial operating model, not the *computational* layer. Niche but zero coverage and high value where it lands. |

## Prioritization (demand × feasibility)

Scored 1–5 each, `[ESTIMATE]`. **Feasibility** = how confidently a strong agent team can be authored from principle-stable knowledge (no volatile facts), and how cleanly it seams with existing plugins without overlap.

| Candidate | Demand | Feasibility | Score | Notes |
|---|---|---|---|---|
| **legacy-modernization** | 5 | 5 | **25** | Huge, perennial enterprise spend; knowledge (strangler fig, characterization tests, the 6 R's, ACL) is stable and well-documented. Clean seams to backend / database / qa / devops. **Build first.** |
| itsm-service-management | 4 | 5 | 20 | High enterprise/MSP demand; ITIL 4 is stable. Clean seam vs observability-sre (engineering incidents). Strong #2. |
| chaos-resilience-engineering | 4 | 4 | 16 | Solid demand; Principles of Chaos are stable. Must carve a sharp boundary vs observability-sre. |
| gis-geospatial-engineering | 3 | 4 | 12 | Real technical gap; durable knowledge (PostGIS/CRS). Narrower audience. |
| grant-writing-management | 3 | 4 | 12 | Steady nonprofit/edu/gov demand; durable craft. Seams to nonprofit-fundraising / public-sector-govtech. |
| digital-marketing-performance | 4 | 3 | 12 | High demand but platform specifics (ad networks) are volatile → freshness burden. |
| developer-relations-advocacy | 3 | 3 | 9 | Niche-but-loved; some overlap risk with technical-writing-docs. |
| robotics-ros-engineering | 2 | 3 | 6 | Distinct stack, narrow audience for this marketplace's buyer base. |
| content-marketing-seo | 3 | 2 | 6 | Merge into digital-marketing-performance rather than ship separately. |
| bioinformatics-computational-biology | 2 | 3 | 6 | Niche; high value where it lands but smallest audience. |

## Build progress (this run)

- ✅ **Built: `legacy-modernization`** (priority #1) — full plugin: 4 agents (modernization-strategist, codebase-archaeologist, refactoring-engineer, migration-engineer), 5 skills, 4 templates, 4 commands, 1 advisory hook, 8 best-practices, a knowledge bank with Mermaid decision trees + a dated 2026 capability map. Registered in `marketplace.json` and `docs/architecture.md`; inherits `ravenclaude-core` protocols. Seams: in-place refactor stays here vs. backend redesign → `backend-engineering`; schema migration mechanics → `database-engineering`; deploy/cutover automation → `devops-cicd`; test-suite buildout → `qa-test-automation`.
- ⏳ **Deferred to follow-up runs:** the remaining 9 candidates. Recommended next two by score: `itsm-service-management` (#2) and `chaos-resilience-engineering` (#3).

**Why one and not ten in a single autonomous run:** every plugin must pass ~50 CI gates (frontmatter scenario-schema, marketplace-claims count/structural, layout allow-list, prettier, the gate-audit meta-test). Shipping one *complete, CI-passing* plugin plus a researched backlog is higher-value than ten half-built directories that fail the build. The backlog above is sequenced so each follow-up run can pick up the next-highest score.
