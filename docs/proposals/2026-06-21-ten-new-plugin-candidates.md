# Ten new-plugin candidates for RavenClaude — research, prioritization, and build status (2026-06-21)

> **Date:** 2026-06-21 · **Author:** Claude Code (autonomous scheduled routine) · **Status:** research + initial build
>
> Task: research and identify 10 plugins **not yet implemented**, prioritize by user demand and technical feasibility, and build out the highest-priority first. This doc is the research deliverable; this pass ships **three** full plugins alongside it — `data-orchestration`, `developer-tooling`, and `startup-fundraising`.

## Method & prior art

The marketplace already carries **~100 plugins** (`.claude-plugin/marketplace.json`). Three prior candidate passes exist and each built a subset:

- [`2026-06-09-ten-new-plugin-candidates.md`](2026-06-09-ten-new-plugin-candidates.md) → built **engineering-management**.
- [`../plugin-candidates-2026-06-10.md`](../plugin-candidates-2026-06-10.md) → built **sales-engineering**.
- [`2026-06-12-ten-new-plugin-candidates.md`](2026-06-12-ten-new-plugin-candidates.md) → built **desktop-app-engineering**; recognized batch **orchestration** (Airflow/Dagster/Prefect) as the #4 unbuilt gap.

This pass (a) **builds three** of the highest-value still-open candidates rather than one — the recognized orchestration gap plus two net-new candidates the prior passes did not surface (build-systems/monorepo tooling, and founder-side venture fundraising) — and (b) re-lists the still-unbuilt high-priority backlog so the roadmap stays whole. For each candidate I name the **closest existing plugin(s)** and the **seam** that keeps it disjoint, per AGENTS.md § "House rules" (no overlap, no re-skin).

## Coverage gaps this pass targets

- **App / build craft:** backend / frontend / mobile / api / database / auth / desktop all ship — **gap: no owner of the _build/monorepo tooling_ layer** (Nx/Turborepo/Bazel, remote caching, dependency policy) distinct from `devops-cicd` pipelines. → **developer-tooling (built)**.
- **Data & AI:** data-platform (ELT), analytics-engineering (dbt), data-streaming (Kafka/Flink) all ship — **gap: no owner of batch _orchestration_** (DAGs, schedules, backfills, SLAs). → **data-orchestration (built)**.
- **Business / founder:** finance (corporate FP&A), product-management, sales-* all ship — **gap: no owner of _founder-side venture fundraising_** (round strategy, deck/narrative, cap-table/dilution, SAFE/term-sheet literacy). → **startup-fundraising (built)**.

## The 10 candidates (prioritized)

Scoring: **Demand** (how often a real practitioner needs it) × **Feasibility** (durable craft, not volatile facts that rot) × **Disjoint** (low overlap with an existing plugin). 1–5 each; Priority = sum.

| #  | Candidate | Demand | Feas. | Disjoint | Priority | Closest existing → seam |
| -- | --------- | ------ | ----- | -------- | -------- | ----------------------- |
| 1 | **data-orchestration** ✅ *(built here)* | 4 | 4 | 5 | 13 | analytics-engineering (dbt) / data-platform (ELT) / data-streaming (Kafka) → owns batch **orchestration**: DAGs/assets, schedules vs sensors, idempotent backfills, retries/SLAs, lineage |
| 2 | **developer-tooling** ✅ *(built here)* | 5 | 5 | 4 | 14 | devops-cicd (pipelines) / backend / frontend → owns the **build & monorepo** layer: Nx/Turborepo/Bazel, task graph & affected builds, remote/content-addressable caching, dependency & lockfile policy |
| 3 | **startup-fundraising** ✅ *(built here)* | 4 | 4 | 5 | 13 | finance (corp FP&A) / product-management → owns **founder-side venture raising**: round strategy, deck/narrative, cap-table & dilution, SAFE/term-sheet literacy (NOT legal advice → legal-ops-clm) |
| 4 | **cli-tooling-engineering** *(carry-over)* | 4 | 5 | 5 | 14 | backend/devops → building CLIs/TUIs: arg parsing, config precedence, output/exit-code contracts, single-binary distribution, Ink/Bubble Tea/Textual |
| 5 | **developer-relations** *(carry-over, repeatedly top-ranked, still unbuilt)* | 4 | 4 | 4 | 12 | technical-writing-docs / marketing-operations → advocacy, quickstart/sample-app engineering, talks/CFPs, OSS community health, DevRel funnel |
| 6 | **content-marketing-seo** *(carry-over)* | 4 | 3 | 4 | 11 | marketing-operations / web-design → editorial strategy, topical authority/clusters, content briefs, GEO (AI-answer optimization) as a discipline |
| 7 | **computer-vision-engineering** *(carry-over)* | 3 | 4 | 4 | 11 | ml-engineering (generic MLOps) → CV craft: detection/segmentation/OCR, annotation/dataset hygiene, augmentation, mAP/IoU eval, edge/realtime inference |
| 8 | **grant-writing-management** *(carry-over)* | 4 | 4 | 4 | 12 | nonprofit-fundraising (donor giving) → federal/foundation proposals, logic models, budget narratives, 2 CFR 200 post-award compliance |
| 9 | **gis-geospatial-engineering** *(carry-over)* | 3 | 3 | 5 | 11 | data-platform / database-engineering → PostGIS, CRS/projections, vector/raster pipelines, tiling, routing, map rendering |
| 10 | **trust-and-safety-engineering** *(carry-over)* | 3 | 4 | 4 | 11 | security-engineering / data-governance-privacy → content moderation, abuse/fraud detection, policy taxonomy, reviewer tooling, T&S metrics |

### Per-candidate brief — purpose, approach, dependencies

**1. data-orchestration** *(BUILT)* — The batch-orchestration lane no plugin owned. *Purpose:* the Airflow-vs-Dagster-vs-Prefect-vs-cloud-native choice, DAG/asset modeling and dependencies, schedules vs event/sensor triggers, idempotent + backfillable tasks, retries with backoff, data-aware/asset-based scheduling, freshness SLAs & alerting, lineage. *Approach:* 2 agents (orchestration-architect, pipeline-orchestration-engineer), 3 skills (choose-orchestrator, design-dag-and-dependencies, handle-backfills-and-retries), a Mermaid orchestrator-selection decision tree + a dated 2026 patterns doc, 2 templates (DAG design doc, backfill runbook). *Deps:* ravenclaude-core; seams to analytics-engineering (the dbt it runs), data-platform (the warehouse/ingestion), data-streaming-engineering (real-time counterpart), devops-cicd/cloud (deploy).

**2. developer-tooling** *(BUILT)* — The build/monorepo layer the app-craft cluster was missing. *Purpose:* the monorepo-tool choice (Nx / Turborepo / Bazel / Buck2 / pnpm workspaces / Moon), the task graph and affected-only builds, remote + content-addressable caching and build performance, dependency & lockfile policy (pinning ranges, Renovate/Dependabot, supply-chain/SBOM hygiene), and scaffolding/codegen. *Approach:* 2 agents (build-systems-architect, monorepo-engineer), 3 skills (choose-monorepo-tooling, optimize-build-and-cache, manage-dependencies), a Mermaid tooling decision tree + a build-caching/performance doc, 2 templates (adoption plan, dependency-upgrade runbook). *Deps:* ravenclaude-core; seams to devops-cicd (CI pipelines run the build), backend/frontend (the code being built), cloud (remote-cache infra).

**3. startup-fundraising** *(BUILT)* — Founder-side venture raising, an unowned business lane. *Purpose:* round strategy (pre-seed/seed/Series A; SAFE vs priced; how-much/runway math), the pitch narrative & deck, the fundraising model/projections, cap-table & dilution math (option pool, pro-rata, post-money SAFE conversion), term-sheet/SAFE **literacy** (cap, discount, liquidation preference, board — essentials, not legal advice), investor pipeline & data room, investor updates. *Approach:* 2 agents (fundraising-strategist, pitch-and-narrative-coach), 3 skills (build-investor-pipeline, model-cap-table-and-dilution, prepare-data-room), a Mermaid stage decision tree + a term-sheet/SAFE essentials doc, 2 templates (deck outline, investor update). *Deps:* ravenclaude-core; seams to finance (model mechanics), product-management (what/why), legal-ops-clm (binding term-sheet legal review).

**4. cli-tooling-engineering** *(carry-over)* — CLIs/TUIs that feel native to the shell: arg/subcommand design, config precedence (flags > env > file > default), the output contract (human vs `--json`, stable exit codes), single-binary distribution (Homebrew/Scoop/npm), TUIs (Ink/Bubble Tea/Textual). *Deps:* backend-engineering, devops-cicd, technical-writing-docs.

**5. developer-relations** *(carry-over)* — Advocacy, quickstart/sample-app engineering, talks/CFPs, OSS community health, DevRel funnel metrics. *Deps:* technical-writing-docs, marketing-operations, api-engineering.

**6. content-marketing-seo** *(carry-over)* — Editorial strategy, topical authority/clusters, content briefs, and GEO (AI-answer optimization) as a content discipline (distinct from web-design's on-page SEO mechanics). *Risk:* SEO/GEO facts are volatile → date them. *Deps:* marketing-operations, web-design.

**7. computer-vision-engineering** *(carry-over)* — Task framing (classification/detection/segmentation/OCR/pose), annotation + dataset hygiene, augmentation, transfer learning, mAP/IoU eval, edge/realtime inference (ONNX/TensorRT/CoreML). *Risk:* model/tooling facts volatile → date them. *Deps:* ml-engineering, data-platform.

**8. grant-writing-management** *(carry-over)* — Federal/foundation proposals, logic models, budget narratives/justification, 2 CFR 200 post-award compliance & reporting. *Deps:* nonprofit-fundraising, finance.

**9. gis-geospatial-engineering** *(carry-over)* — PostGIS spatial indexing, CRS/projections, vector/raster pipelines, tiling, routing, map rendering. *Risk:* some volatile tool facts. *Deps:* data-platform, database-engineering.

**10. trust-and-safety-engineering** *(carry-over)* — Content moderation, abuse/fraud detection, policy taxonomy, reviewer tooling, T&S metrics. *Deps:* security-engineering, data-governance-privacy.

## Prioritization rationale

- **Built this pass (top tier).** All three score 13–14 and clear the same bar: high demand, durable (evergreen-craft) feasibility, and a clean seam to an existing plugin.
  - **developer-tooling (14)** — the one structural hole left in the app/build-craft cluster; demand is universal (any multi-package repo), and the craft (task graph, caching, lockfile policy) is evergreen with only version-map facts dated.
  - **data-orchestration (13)** — the recognized #4 gap from the 2026-06-12 pass; every data team using dbt/ELT needs an orchestrator, and the patterns (idempotent backfills, retries, SLAs) are durable. Volatile vendor facts are isolated to a dated knowledge doc.
  - **startup-fundraising (13)** — a high-demand business lane with no owner; cap-table/dilution/SAFE mechanics are durable math, market norms are framed as dated ranges, and the legal boundary routes cleanly to legal-ops-clm.
- **cli-tooling (14)** is the strongest still-unbuilt candidate (pure evergreen craft, fully unowned) and is the recommended next build.
- **developer-relations (12)** keeps re-ranking high across passes and remains unbuilt — strong follow-on.
- The remainder (content-marketing-seo, computer-vision, grant-writing, GIS, trust-and-safety) are real and valuable but are either narrower-audience or carry more volatile facts; they slot below.

## Build status (this PR)

- **#1 data-orchestration — BUILT.** 2 agents (full scenario-authoring frontmatter, each description ≤300 chars), 3 skills, a Mermaid orchestrator-selection decision tree + a dated 2026 patterns doc, 2 templates, README + CLAUDE.md. Registered in `marketplace.json` and the `docs/architecture.md` roster.
- **#2 developer-tooling — BUILT.** 2 agents, 3 skills, a Mermaid monorepo-tooling decision tree + a build-caching/performance doc, 2 templates, README + CLAUDE.md. Registered in catalog + roster.
- **#3 startup-fundraising — BUILT.** 2 agents, 3 skills, a Mermaid stage decision tree + a term-sheet/SAFE essentials doc, 2 templates, README + CLAUDE.md, with the founder-literacy/not-legal-advice disclaimer and the legal-ops-clm seam. Registered in catalog + roster.
- **#4–#10 — SCOPED, NOT YET BUILT.** Each existing plugin is ~12–45 files of cited, CI-gated content (agents must carry the full scenario-authoring frontmatter; descriptions are length-capped; relative links must resolve). The honest constraint is **scope-per-quality-bar, not capability** — each candidate above carries enough detail (agents, skills, knowledge, seams, deps) to scaffold in a follow-on PR, in the priority order above.

## Blockers / notes

- **No technical blockers** were hit. The strict gates (frontmatter/scenario schema, marketplace-claims structural check, layout allow-list, relative-link resolution, prettier, version-pin parity) all run locally and were validated before pushing.
- The only real constraint is **breadth vs depth**: ten shallow plugins would fail the frontmatter/scenario gates and dilute the marketplace. Three complete, gate-passing plugins plus this fully-scoped, prioritized roadmap is the higher-value deliverable; the remaining seven are ready to build in priority order.
</content>
</invoke>
