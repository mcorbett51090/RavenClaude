# Ten new-plugin candidates for RavenClaude — research, prioritization, and build status (2026-06-24)

> **Date:** 2026-06-24 · **Author:** Claude Code (autonomous routine) · **Status:** research + one initial build
>
> Task: research and identify 10 plugins **not yet implemented**, prioritize by user demand × technical feasibility, and build out the highest-priority first. This doc is the research deliverable; the build (`plugins/realtime-collaboration-engineering/`) ships alongside it.

## How this run relates to the prior passes (read first)

This is a **recurring routine** with a **standing decision** it must respect (see `docs/proposals/2026-06-09 … 2026-06-23-ten-new-plugin-candidates.md`, the parked-#409 rationale, and `docs/idea-board.md`):

> **The accepted output of this routine is: build the single highest-priority _unbuilt_ gap to full gate-passing quality, and refresh the prioritized roadmap — NOT ship 10 speculative shells.** Ten shallow plugins would fail the frontmatter/scenario gates and dilute a catalog already at ~118 plugins, and shipping speculative shells contradicts the documented **build-on-real-demand over catalog-breadth** policy.

The prior passes also surfaced a durable failure mode: **parallel routine runs keep re-deriving the same roadmap and racing to build the same candidate.** Mitigation honored here — I read the **live roster** (`plugins/` on disk, 2026-06-24, 118 plugins) and the latest prior roadmap (2026-06-23) **before** picking, and chose the **highest-priority row that the prior roadmap already named as the top unbuilt candidate and that is confirmed not on disk**: `realtime-collaboration-engineering`.

### What the prior roadmap (2026-06-23) left, and what is now built

The 2026-06-23 pass built `open-source-maintenance` (now on disk, merged via #477) and left this collision note: *"the top unbuilt rows are #2 realtime-collaboration-engineering and #3 streaming-media-engineering."* Verified against the live `plugins/` tree (2026-06-24):

| Prior candidate | State on disk (2026-06-24) |
|---|---|
| open-source-maintenance | **BUILT** (merged, #477) |
| **realtime-collaboration-engineering** | **BUILT in this PR** ← this run |
| streaming-media-engineering, computer-vision-engineering, ux-research, design-systems-engineering, knowledge-management-engineering, robotics-engineering, bioinformatics-engineering, accessibility-of-native-apps | **still unbuilt** (carried forward, re-prioritized below) |

So this pass drains the prior #2. **`streaming-media-engineering` becomes the new top unbuilt row** for the next run.

## Coverage map (what already ships, so we don't duplicate)

- **App craft:** backend / frontend / mobile / desktop-app / cli-tooling / api / database / auth-identity / browser-extension — broad and CLI-complete.
- **Platform & ops:** devops-cicd, cloud-native-kubernetes, terraform-iac, observability-sre, platform-engineering-idp, performance-engineering, finops-cloud-cost, qa-test-automation, security-engineering, cybersecurity-grc, itsm-service-management.
- **Cloud:** aws / azure / gcp.
- **Data & AI:** data-platform, data-orchestration, analytics-engineering, data-streaming, ml-engineering, ai-rag-engineering, data-science-research, applied-statistics, data-governance-privacy, microsoft-fabric, tableau, claude-app-engineering — **gap: no _computer-vision_ owner.**
- **Specialized eng:** blockchain-web3, embedded-iot, game-development, accessibility-engineering, localization-i18n, search-relevance, experimentation-growth, email-engineering, geospatial, wordpress-cms, **realtime-collaboration ← this run** — **gap: no _streaming-media_ owner.**
- **Dev-lifecycle meta:** developer-tooling, developer-relations, technical-writing-docs, open-source-maintenance, engineering-management, project/technical-program-management — well covered after #477.
- **Business / verticals:** ~70 plugins. Business-side carry-overs remain **held pending real demand** per the #409 decision.

## The 10 candidates (prioritized)

Scoring: **Demand** (how often a real practitioner needs this) × **Feasibility** (durable craft, not volatile facts that rot) × **Disjoint** (low overlap with an existing plugin). 1–5 each; Priority = sum.

| # | Candidate | Demand | Feas. | Disjoint | Priority | Closest existing → seam |
|---|---|---|---|---|---|---|
| 1 | **realtime-collaboration-engineering** ✅ *(built here)* | 4 | 4 | 5 | 13 | frontend/backend → multiplayer/collab: CRDT vs OT, transport (WS/WebRTC, SFU vs mesh), presence/awareness, offline merge, the sync server |
| 2 | **streaming-media-engineering** *(new top unbuilt)* | 3 | 4 | 5 | 12 | backend / game-dev → audio/video delivery: HLS/DASH packaging, transcode ladders, DRM, low-latency (LL-HLS/WebRTC), CDN/ABR, player QoE |
| 3 | **computer-vision-engineering** *(carry-over)* | 3 | 4 | 4 | 11 | ml-engineering (generic MLOps) → CV craft: detection/segmentation/OCR, annotation/dataset hygiene, augmentation, mAP/IoU eval, edge/realtime inference |
| 4 | **ux-research** *(carry-over)* | 4 | 4 | 3 | 11 | web-design (ux-designer = wireframes) / product-management (what/why) → research methods: interviews, usability tests, surveys, JTBD, personas, research ops, sample/bias rigor |
| 5 | **design-systems-engineering** *(carry-over)* | 3 | 4 | 4 | 11 | web-design (visual/tokens) / frontend (components) → DS as a product: token architecture, component API/governance, Figma↔code, versioning a DS, contribution model |
| 6 | **knowledge-management-engineering** *(carry-over)* | 3 | 4 | 3 | 10 | technical-writing-docs (product docs) → internal KM: wiki IA, search relevance for docs, knowledge ops, decision records, stale-content lifecycle |
| 7 | **robotics-engineering (ROS)** *(carry-over)* | 2 | 3 | 5 | 10 | embedded-iot (devices) → ROS 2 nodes/topics/actions, URDF, sim (Gazebo/Isaac), perception↔control loop, realtime constraints |
| 8 | **bioinformatics-engineering** *(carry-over)* | 2 | 3 | 5 | 10 | data-science-research (generic) / clinical-trials (ops) → sequence/variant pipelines, Nextflow/Snakemake, reference genomes, FAIR data |
| 9 | **accessibility-of-native-apps** *(carry-over, stretch)* | 3 | 3 | 4 | 10 | accessibility-engineering (web/WCAG) → native a11y APIs (UIA / AX / AccessKit) for desktop + TUI; pairs with desktop-app + cli-tooling |
| 10 | **ar-vr-xr-engineering** *(new)* | 2 | 3 | 5 | 10 | game-development (3D engines) / mobile → XR craft: scene/anchor/spatial-mapping, hand/eye input, render-budget for HMDs, OpenXR portability, comfort/locomotion |

### Per-candidate brief — purpose, approach, dependencies

**1. realtime-collaboration-engineering** — Multiplayer/collaborative editing (Figma/Notion/Docs-style), a lane no plugin owned. `frontend` renders, `backend` hosts the service, `data-streaming` fans out an event log — but *nobody* owned the **collaboration-specific craft**: the merge model (CRDT vs OT vs LWW by data shape), the shared-document model + causal identity, offline/reconnection merge, presence/awareness kept out of the document, transport (WebSocket vs WebRTC, client-server/SFU/mesh), and scaling the sync server. *Approach:* 3 agents (collab-architect = the irreversible decisions; sync-engine-engineer = the merge engine; presence-and-transport-engineer = the wire + scale), 5 skills, a knowledge bank (CRDT-vs-OT + transport/topology Mermaid trees, **durable** consistency concepts kept separate from a **dated** 2026 tooling map), 8 best-practices, 4 templates, 3 commands, 1 advisory hook. *Deps:* ravenclaude-core; seams to frontend, backend, data-streaming, performance, security, open-source-maintenance. **High feasibility — the distributed-systems reasoning (strong eventual consistency, causal order, tombstones, intention preservation) is durable; only the library map is `verify-at-use`.** ← built in this PR.

**2. streaming-media-engineering** *(new top unbuilt)* — Audio/video delivery infrastructure: HLS/DASH packaging, transcode/bitrate ladders, DRM (Widevine/FairPlay), low-latency (LL-HLS, WebRTC), CDN + adaptive bitrate, and player QoE metrics. *Approach:* 3 agents (media-pipeline-architect, transcode-and-packaging-engineer, delivery-and-playback-engineer). *Deps:* backend, aws/gcp (MediaConvert/Transcoder), performance. *Risk:* codec/DRM specifics dated → keep them in a `verify-at-use` tooling file, durable ABR/packaging reasoning separate.

**3. computer-vision-engineering** *(carry-over)* — The CV specialization `ml-engineering` is too generic for: task framing (classification/detection/segmentation/OCR/pose), annotation + dataset hygiene, augmentation, transfer learning, evaluation (mAP/IoU), edge/realtime inference (ONNX/TensorRT/CoreML). *Approach:* 3 agents (cv-architect, vision-model-engineer, edge-inference-engineer). *Deps:* ml-engineering, data-platform. *Risk:* model/tooling facts volatile.

**4. ux-research** *(carry-over)* — The research-methods lane: interview/usability-test design, survey rigor, sampling/bias, JTBD, persona/journey synthesis, research ops. *Approach:* 1–2 agents (ux-researcher [+ research-ops-strategist]). *Deps:* web-design, product-management, applied-statistics (significance seam). Methodology vertical → advisory, low runtime.

**5. design-systems-engineering** *(carry-over)* — A design system as a *product*: token architecture (primitive→semantic→component), component API design + governance, Figma↔code sync, versioning/releasing a DS (semver for components), the contribution model. *Approach:* 2 agents (design-system-architect, component-library-engineer). *Deps:* web-design, frontend; strong seam to open-source-maintenance (a DS is a released, versioned, contributed-to artifact).

**6. knowledge-management-engineering** *(carry-over)* — Internal knowledge ops, distinct from product docs: wiki IA, search relevance for an internal corpus, decision records (ADRs), stale-content lifecycle. *Approach:* 2 agents (km-architect, knowledge-ops-engineer). *Deps:* technical-writing-docs, search-relevance-engineering.

**7. robotics-engineering (ROS)** *(carry-over, stretch)* — ROS 2 nodes/topics/services/actions, URDF, simulation (Gazebo/Isaac), the perception↔planning↔control loop, realtime constraints. *Deps:* embedded-iot, ml-engineering. Niche but fully unowned.

**8. bioinformatics-engineering** *(carry-over, stretch)* — Sequence/variant pipelines, Nextflow/Snakemake workflow craft, reference-data management, reproducibility/FAIR. *Deps:* data-science-research, data-orchestration. Niche, unowned.

**9. accessibility-of-native-apps** *(carry-over, stretch)* — Native accessibility APIs (Windows UI Automation, macOS AX, AccessKit) for desktop apps + TUIs, distinct from `accessibility-engineering`'s web/WCAG lane. *Deps:* accessibility-engineering, desktop-app, cli-tooling.

**10. ar-vr-xr-engineering** *(new)* — Spatial/immersive apps: scene graph, anchors/spatial mapping, hand/eye/controller input, the strict HMD render budget, OpenXR portability, and comfort/locomotion. *Deps:* game-development (3D engines), mobile. Niche; pairs with game-development. Replaces the now-built realtime-collaboration in the bottom tier to keep the list at ten.

## Prioritization rationale

- **#1 realtime-collaboration-engineering** was the highest-value buildable row this run: it was the prior roadmap's named **top unbuilt** candidate, it closes a **genuinely unowned lane** (every adjacent role existed — frontend, backend, data-streaming, performance — but none owned the collaboration-specific craft), **demand is real** (multiplayer/collab is now a default expectation for editors and docs tools), and **feasibility is high** because the hard core is durable distributed-systems reasoning, with the volatile library landscape quarantined in a dated `verify-at-use` file. It mirrors the proven multi-agent-with-a-lead recipe (architect + two doing-engineers) used by `backend-engineering` / `data-streaming-engineering`.
- **#2 streaming-media-engineering** is the next build: durable ABR/packaging craft, a genuinely unowned lane, clean seams — the only watch-out is keeping codec/DRM specifics dated.
- **#3–#5 (computer-vision, ux-research, design-systems)** are strong but each carries either volatile facts (CV) or a thinner disjoint margin (ux-research vs product-management; design-systems vs web-design) — buildable, with care on the seam.
- **#6–#10** are valuable but niche/stretch (robotics, bioinformatics, AR/VR) or pair with already-built plugins (native-a11y, KM); hold pending real demand per the #409 policy.

## Build status (this PR)

- **#1 realtime-collaboration-engineering — BUILT.** Full plugin to the marketplace quality bar: 3 agents (scenario-schema complete, each description ≤ 300 chars), 5 skills, a 4-file knowledge bank (CRDT-vs-OT + transport/topology Mermaid decision trees, durable consistency/merge concepts, a dated 2026 tooling map), 8 best-practice rules, 4 templates, 3 commands, 1 advisory ERE-only hook, README + CLAUDE.md + CHANGELOG. Registered in `.claude-plugin/marketplace.json` and the `docs/architecture.md` Status table; README plugin counts updated 118 → 119. Globs already covered by `.repo-layout.json` (`plugins/*/**`).
- **#2–#10 — SCOPED, NOT YET BUILT.** Each existing plugin is ~25–45 files of cited, CI-gated content. Building all ten to the depth bar in one pass would fail the frontmatter/scenario gates and dilute the marketplace — the documented anti-pattern. One complete, gate-passing plugin plus this refreshed, prioritized roadmap is the higher-value deliverable; the remaining nine are ready to build in priority order, business-side carry-overs awaiting real demand per the #409 decision.

## Blockers / notes

- **No technical blockers** were hit building #1. Gates run locally and green: JSON validity, `check-frontmatter.py` (incl. the 300-char agent cap + scenario schema — caught a missing `quickstart` on all three agents and two over-cap descriptions, all fixed), `check-md-links.py`, `check-marketplace-claims.py` (`--structural-only` and full count mode after the README count fixes), and prettier on the changed JSON/doc files.
- The only real constraint is **breadth vs depth** plus the standing **build-on-real-demand** policy: ten shallow plugins would fail gates and dilute the catalog. The responsible deliverable is one excellent plugin in the cleanest remaining structural gap + this roadmap.
- **Routine-collision note for the next run:** before building, read `plugins/` on disk *and* the latest `docs/proposals/*-ten-new-plugin-candidates.md`, then pick the highest-priority row **not** already on disk. As of 2026-06-24 the top unbuilt row is **#2 streaming-media-engineering**, followed by #3 computer-vision-engineering and #4 ux-research.
