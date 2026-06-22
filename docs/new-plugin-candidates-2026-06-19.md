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

## Disposition — fold into an existing plugin, add as new, or skip

After grounding each candidate against the existing roster (not assuming a gap), each idea was routed: **fold** the valuable idea into the plugin that already owns the lane, **add** a new plugin for a genuinely uncovered lane, or **skip** where coverage already exists. (Policy: "if a plugin exists, update it with the valuable idea; add genuinely new ones.")

| # | Candidate | Grounding check | Disposition |
|---|---|---|---|
| 1 | legacy-modernization | No existing home (backend/db/qa adjacent, none own it) | ✅ **ADDED** (new plugin, prior commit) |
| 2 | itsm-service-management | No ITSM/ITIL plugin; observability-sre owns *engineering* incidents, not the ITIL operating model | ✅ **ADDED** (new plugin, this run) |
| 3 | chaos-resilience-engineering | `observability-sre` exists (reliability/incident/SLO) but has **no** chaos/resilience-verification skill | ✅ **FOLDED** into `observability-sre` v0.4.0 — added a `chaos-engineering` skill + `chaos-engineering-reference.md` knowledge doc. The proactive complement to its reactive practices; no separate plugin warranted. |
| 4 | gis-geospatial-engineering | ~~No spatial plugin~~ — **superseded:** `main` shipped **`geospatial-engineering`** (landed 2026-06-22) | ⛔ **NOW COVERED on main.** Removed from the backlog — the lane is owned. |
| 5 | grant-writing-management | `nonprofit-fundraising` **already ships a `grant-writer` agent** + `qualify-the-funder` skill | ⛔ **SKIP** — coverage already exists; low additive value. (Corrects this doc's initial over-statement of the gap.) A federal post-award-compliance skill is the only marginal add; not worth a fold this round. |
| 6 | digital-marketing-performance | `marketing-operations` already covers channel-mix + attribution + CAC/LTV | ⏳ **DEFER → fold.** Net-new value is a dedicated paid-media/ROAS + SEO/SEM skill pair into `marketing-operations`; moderate value, deferred to keep this PR's blast radius bounded. |
| 7 | developer-relations-advocacy | ~~`technical-writing-docs` owns docs~~ — **superseded:** `main` shipped **`developer-relations`** (landed 2026-06-22) | ⛔ **NOW COVERED on main.** Removed from the backlog — the lane is owned. |
| 8 | robotics-ros-engineering | `embedded-iot-engineering` is firmware/device; ROS 2 is distinct | ⏳ **DEFER → new plugin** (low score, narrow audience). |
| 9 | content-marketing-seo | Overlaps #6 | ⛔ **MERGE into #6** (as the doc flagged) — not a separate plugin. |
| 10 | bioinformatics-computational-biology | `data-science-research` adjacent; niche | ⏳ **DEFER → new plugin** (low score, smallest audience). |

## Build progress (this run)

- ✅ **ADDED `legacy-modernization`** (priority #1) — 4 agents, 5 skills, 8 best-practices, 4 templates, 4 commands, 1 advisory hook, Mermaid decision-tree knowledge bank.
- ✅ **ADDED `itsm-service-management`** (priority #2) — 4 agents (service-management-lead, incident-and-problem-manager, change-and-release-manager, service-desk-and-request-manager), 5 skills, 8 best-practices, 4 templates, 4 commands, 1 advisory hook, knowledge bank (ITSM decision trees + ITIL 4 practice reference + dated 2026 tooling map). Sharp seam vs `observability-sre` (ITIL operating model vs engineering reliability practice).
- ✅ **FOLDED chaos engineering into `observability-sre`** (priority #3) — `chaos-engineering` skill + `chaos-engineering-reference.md`; version 0.3.0 → 0.4.0; descriptions + counts updated.
- ⛔ **Skipped** grant-writing (already covered by `nonprofit-fundraising/grant-writer`) and content-marketing-seo (merged into digital-marketing).
- ⏳ **Deferred (documented above):** gis-geospatial (next new plugin), digital-marketing-performance fold, devrel fold, robotics-ros, bioinformatics.

**Why this scope and not all ten at once:** every plugin/fold must pass ~50 CI gates (frontmatter scenario-schema, marketplace-claims count+structural, layout allow-list, prettier, artifact-freshness, the gate-audit meta-test). Two complete new plugins + one clean fold, all CI-green, is higher-value and lower-risk than ten half-built directories that break the build. The deferred items are routed and sequenced so each follow-up run picks up the next highest-value one.
