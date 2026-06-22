# Ten new-plugin candidates for RavenClaude — research, prioritization, and build status (2026-06-12)

> **Date:** 2026-06-12 · **Author:** Claude Code (autonomous task) · **Status:** research + initial build
>
> Task: research and identify 10 plugins **not yet implemented**, prioritize by user demand and technical feasibility, and build out the highest-priority first. This doc is the research deliverable; the first build (`plugins/desktop-app-engineering/`) ships alongside it.

## Method

The marketplace already carries **100 plugins** (`.claude-plugin/marketplace.json`). Two prior candidate passes ([`2026-06-09-ten-new-plugin-candidates.md`](2026-06-09-ten-new-plugin-candidates.md), [`../plugin-candidates-2026-06-10.md`](../plugin-candidates-2026-06-10.md)) were **role/business-heavy** and each built exactly one plugin (`engineering-management`, `sales-engineering`). This pass takes a deliberately **technical / app-craft lens** to surface engineering gaps those passes under-covered, then re-lists the still-unbuilt high-priority business candidates so the roadmap stays whole.

For each candidate I name the **closest existing plugin(s)** and the **seam** that keeps it disjoint, per AGENTS.md § "House rules" (no overlap, no re-skin).

## Coverage map (what already ships, so we don't duplicate)

- **App craft:** backend / frontend / mobile / api / database / auth-identity — **note the gap: no _desktop_ sibling.**
- **Platform & ops:** devops-cicd, cloud-native-kubernetes, terraform-iac, observability-sre, platform-engineering-idp, performance-engineering, finops-cloud-cost, qa-test-automation, security-engineering, cybersecurity-grc
- **Cloud:** aws / azure / gcp
- **Data & AI:** data-platform, analytics-engineering, data-streaming, ml-engineering, ai-rag-engineering, data-science-research, applied-statistics, data-governance-privacy, microsoft-fabric, tableau — **gap: no batch-pipeline _orchestration_ owner (Airflow/Dagster/Prefect); no _computer-vision_ owner.**
- **Specialized eng:** blockchain-web3, embedded-iot, game-development, accessibility-engineering, localization-i18n, search-relevance-engineering, experimentation-growth-engineering — **gaps: CLI tooling, browser extensions, realtime-collaboration, email infra.**
- **Business / verticals:** finance, fintech-payments, product-management, project-management, process-improvement, sales-engineering, sales-revops, marketing-operations, engineering-management, plus ~50 industry verticals.

## The 10 candidates (prioritized)

Scoring: **Demand** (how often a real practitioner needs this) × **Feasibility** (grounds in durable craft, not volatile facts that rot) × **Disjoint** (low overlap with an existing plugin). 1–5 each; Priority = sum.

| # | Candidate | Demand | Feas. | Disjoint | Priority | Closest existing → seam |
|---|---|---|---|---|---|---|
| 1 | **desktop-app-engineering** ✅ *(built here)* | 5 | 5 | 5 | 15 | frontend/mobile/backend → owns the _desktop_ runtime (Electron/Tauri): process/security model, packaging, signing/notarization, auto-update, native OS integration |
| 2 | **cli-tooling-engineering** | 4 | 5 | 5 | 14 | backend/devops → owns building _CLIs/TUIs_ (arg parsing, config precedence, output/exit-code contracts, distribution, Ink/Bubble Tea) |
| 3 | **browser-extension-engineering** | 4 | 4 | 5 | 13 | frontend → owns MV3 extensions: service worker, content-script isolation, message passing, permissions, store review |
| 4 | **data-engineering-orchestration** | 4 | 4 | 4 | 12 | analytics-engineering (dbt) / data-streaming (Kafka) / data-platform (ELT) → owns batch **orchestration** (Airflow/Dagster/Prefect): DAGs, idempotent backfills, retries/SLAs, lineage |
| 5 | **realtime-collaboration-engineering** | 4 | 4 | 5 | 13 | frontend/backend → owns multiplayer/collab: CRDTs vs OT, WebRTC/WebSocket transport, presence, offline merge, awareness |
| 6 | **computer-vision-engineering** | 3 | 4 | 4 | 11 | ml-engineering (generic MLOps) → owns the CV craft: detection/segmentation, annotation/dataset hygiene, augmentation, edge/realtime inference |
| 7 | **email-deliverability-engineering** | 4 | 4 | 4 | 12 | marketing-operations / backend → owns sending infra: SPF/DKIM/DMARC/BIMI, ESP integration, warmup, bounce/complaint handling, deliverability |
| 8 | **developer-relations** *(carry-over, unbuilt)* | 4 | 4 | 4 | 12 | technical-writing-docs / marketing-operations → owns advocacy, quickstart/sample-app craft, talks/CFPs, community health, DevRel funnel |
| 9 | **gis-geospatial-engineering** *(carry-over, unbuilt)* | 3 | 3 | 5 | 11 | data-platform / database-engineering → owns PostGIS, CRS/projections, vector/raster pipelines, tiling, routing |
| 10 | **trust-and-safety-engineering** *(carry-over, unbuilt)* | 3 | 4 | 4 | 11 | security-engineering / data-governance-privacy → owns moderation, abuse/fraud detection, policy taxonomy, reviewer tooling, T&S metrics |

### Per-candidate brief — purpose, approach, dependencies

**1. desktop-app-engineering** — The desktop runtime the app-craft cluster is missing. *Purpose:* build cross-platform desktop apps well — the Electron-vs-Tauri-vs-native-vs-PWA decision, a hardened process/security model (contextIsolation, IPC allow-lists, Tauri capabilities), reproducible packaging + code-signing/notarization on Windows + macOS, safe auto-update, and native OS integration (tray, menus, notifications, file associations, deep links). *Approach:* 4 agents (desktop-architect, electron-engineer, tauri-engineer, desktop-platform-engineer), 5 skills, a decision-tree knowledge bank (framework-choice + IPC-security trees + a dated 2026 capability map), ~12 best-practices, 4 templates, 4 commands, 1 advisory anti-pattern hook, a scenarios bank, `.lsp.json` (TS + Rust). *Deps:* ravenclaude-core; seams to frontend-engineering (the renderer UI), backend-engineering/api-engineering (the backend it talks to), auth-identity (tokens in the OS secure store), devops-cicd (signing/notarization in CI), mobile-engineering (the offline/lifecycle sibling). **← built in this PR.**

**2. cli-tooling-engineering** — Building command-line tools and TUIs that feel native to the shell. *Purpose:* arg/flag parsing and subcommand design, config precedence (flags > env > file > default), the output contract (human vs `--json`, stable exit codes, stderr/stdout discipline), distribution (single-binary, Homebrew/Scoop/npm), and TUIs (Ink, Bubble Tea, Textual). *Approach:* 3–4 agents (cli-architect, cli-implementation-engineer, tui-engineer), arg-design + distribution decision trees. *Deps:* seams to backend-engineering, devops-cicd (release/signing), technical-writing-docs (man pages/help).

**3. browser-extension-engineering** — Manifest V3 extensions across Chrome/Edge/Firefox/Safari. *Purpose:* the MV3 service-worker model, content-script isolation + the DOM boundary, `chrome.runtime` message passing, the permissions/host-permissions minimization discipline, storage + sync, and the store review/publishing pipeline. *Approach:* 3 agents (extension-architect, extension-implementation-engineer, extension-store-and-review-specialist). *Deps:* seams to frontend-engineering, auth-identity, security-engineering (CSP/permissions review).

**4. data-engineering-orchestration** — The batch-orchestration lane no plugin owns. *Purpose:* DAG/asset modeling, idempotent + backfillable tasks, retries/SLAs/alerting, sensors/triggers vs schedules, data lineage, and the Airflow-vs-Dagster-vs-Prefect choice. *Approach:* 3 agents (orchestration-architect, pipeline-dag-engineer, data-reliability-engineer). *Deps:* seams to analytics-engineering (dbt invoked by the orchestrator), data-platform (the warehouse), data-streaming (real-time counterpart).

**5. realtime-collaboration-engineering** — Multiplayer/collaborative editing (Figma/Notion/Google-Docs-style). *Purpose:* CRDT vs OT choice by merge cost, transport (WebSocket vs WebRTC, SFU vs mesh), presence/awareness, offline-edit reconciliation, and the document/sync server. *Approach:* 3 agents (collab-architect, sync-engine-engineer, presence-and-transport-engineer). *Deps:* seams to frontend-engineering, backend-engineering, data-streaming.

**6. computer-vision-engineering** — The CV specialization `ml-engineering` is too generic for. *Purpose:* task framing (classification/detection/segmentation/OCR/pose), annotation + dataset hygiene, augmentation, transfer learning, evaluation (mAP/IoU), and edge/realtime inference (ONNX/TensorRT/CoreML). *Approach:* 3 agents (cv-architect, vision-model-engineer, edge-inference-engineer). *Deps:* seams to ml-engineering (the MLOps loop), data-platform. *Risk:* model/tooling facts are volatile — date them.

**7. email-deliverability-engineering** — Transactional + lifecycle email infrastructure. *Purpose:* authentication (SPF/DKIM/DMARC/BIMI), the ESP/relay choice, IP/domain warmup, list hygiene + bounce/complaint handling, template/MIME craft, and inbox-placement/deliverability monitoring. *Approach:* 3 agents (email-infra-architect, deliverability-engineer, email-template-engineer). *Deps:* seams to marketing-operations (campaigns), backend-engineering (the send path), data-governance-privacy (consent).

**8. developer-relations** *(carry-over from 2026-06-10, still unbuilt)* — Advocacy, quickstart/sample-app engineering, talks/CFPs, community health, DevRel funnel metrics. *Deps:* technical-writing-docs, marketing-operations, api-engineering.

**9. gis-geospatial-engineering** *(carry-over)* — PostGIS spatial indexing, CRS/projections, vector/raster pipelines, tiling, routing, map rendering. *Deps:* data-platform, database-engineering. *Risk:* some volatile tool facts.

**10. trust-and-safety-engineering** *(carry-over)* — Content moderation, abuse/fraud detection, policy taxonomy, reviewer tooling, T&S metrics. *Deps:* security-engineering, data-governance-privacy.

## Prioritization rationale

- **#1 desktop-app-engineering tops the list** on every axis: it is the **one structural hole in the app-craft cluster** (backend/frontend/mobile/api/database/auth all exist; desktop is the missing sibling), demand is high (every team shipping an Electron/Tauri app), feasibility is high (durable craft — the security model, signing, and update mechanics are evergreen, with only the version-map dated `[verify-at-use]`), and its seams are clean (it routes UI to frontend, signing to devops, auth to auth-identity). That makes it the highest-value, lowest-risk first full build — and it directly mirrors the proven `mobile-engineering` recipe.
- **#2 cli-tooling, #3 browser-extension, #5 realtime-collaboration** are the next tier: high feasibility (durable craft), genuinely unowned lanes, clean seams to the existing engineering plugins.
- **#4 orchestration, #7 email-deliverability** are high-demand but carry more volatile vendor facts (Airflow/Dagster releases; ESP/deliverability specifics) → dated, re-verify-at-use knowledge.
- **#6 computer-vision, #8 developer-relations, #9 GIS, #10 trust-and-safety** are real and valuable but either narrower-audience or carry-overs already on the roadmap; they slot below the fresh app-craft gaps.

## Build status (this PR)

- **#1 desktop-app-engineering — BUILT.** Full plugin to the marketplace quality bar: 4 agents (scenario-schema complete, each description ≤300 chars), 5 skills + 4 commands, a decision-tree knowledge bank (framework-choice + IPC-security Mermaid trees + a dated 2026 capability map), ~12 best-practice rules, 4 templates, a 3-scenario bank, 1 advisory anti-pattern hook, `.lsp.json` (TypeScript + Rust), README + CLAUDE.md + CHANGELOG. Registered in `marketplace.json` and the `docs/architecture.md` roster; globs already covered by `.repo-layout.json` (`plugins/*/**`).
- **#2–#10 — SCOPED, NOT YET BUILT.** Each existing plugin is ~35–45 files of carefully-grounded, CI-gated content (agents must carry the full scenario-authoring frontmatter; the knowledge bank must be cited; descriptions are length-capped). Building all ten to the depth bar is a multi-session effort. The honest blocker is **scope-per-quality-bar, not capability** — each candidate above carries enough detail (agents, knowledge, seams, deps) to scaffold in a follow-on PR, in the priority order above.

## Blockers / notes

- **No technical blockers** were hit building #1 — git, the layout gate, the frontmatter gate, and the marketplace-claims structural gate are all green locally.
- The only real constraint is **breadth vs depth**: ten shallow plugins would fail the frontmatter/scenario gates and dilute the marketplace. One complete, gate-passing plugin plus this fully-scoped, prioritized roadmap is the higher-value deliverable; the remaining nine are ready to build in priority order.
