# Ten new-plugin candidates for RavenClaude — research, prioritization, and build status (2026-06-23)

> **Date:** 2026-06-23 · **Author:** Claude Code (autonomous routine) · **Status:** research + one initial build
>
> Task: research and identify 10 plugins **not yet implemented**, prioritize by user demand × technical feasibility, and build out the highest-priority first. This doc is the research deliverable; the build (`plugins/open-source-maintenance/`) ships alongside it.

## How this run relates to the prior passes (read first)

This is a **recurring routine** with a **standing decision** it must respect (see `docs/proposals/2026-06-09 … 2026-06-22-ten-new-plugin-candidates.md`, the parked-#409 rationale, and `docs/idea-board.md`):

> **The accepted output of this routine is: build the single highest-priority _unbuilt_ gap to full gate-passing quality, and refresh the prioritized roadmap — NOT ship 10 speculative shells.** Ten shallow plugins would fail the frontmatter/scenario gates and dilute a catalog already at ~118 plugins, and shipping speculative shells contradicts the documented **build-on-real-demand over catalog-breadth** policy.

The prior passes also surfaced a durable failure mode: **parallel routine runs keep re-deriving the same roadmap and racing to build the same candidate.** Mitigation honored here — I read the **live roster** (`plugins/` on disk, 2026-06-23) before picking, and chose a gap that appears in **no** prior roadmap and is **not** on disk: `open-source-maintenance`.

### What the prior roadmaps proposed, and what is now built

The 2026-06-22 reconciliation noted many candidates merged in parallel. Verified against the live `plugins/` tree (2026-06-23):

| Prior candidate | State on disk (2026-06-23) |
|---|---|
| cli-tooling-engineering, browser-extension-engineering, email-engineering, data-orchestration, developer-relations, trust-and-safety, geospatial-engineering | **BUILT** (merged) |
| realtime-collaboration-engineering, computer-vision-engineering, accessibility-of-native-apps | **still unbuilt** (carried forward below) |

So the prior roadmaps are mostly drained. This pass adds **`open-source-maintenance`** as the new #1 — a structural gap none of them named.

## Coverage map (what already ships, so we don't duplicate)

- **App craft:** backend / frontend / mobile / desktop-app / cli-tooling / api / database / auth-identity / browser-extension — broad and now CLI-complete.
- **Platform & ops:** devops-cicd, cloud-native-kubernetes, terraform-iac, observability-sre, platform-engineering-idp, performance-engineering, finops-cloud-cost, qa-test-automation, security-engineering, cybersecurity-grc, itsm-service-management.
- **Cloud:** aws / azure / gcp.
- **Data & AI:** data-platform, data-orchestration, analytics-engineering, data-streaming, ml-engineering, ai-rag-engineering, data-science-research, applied-statistics, data-governance-privacy, microsoft-fabric, tableau, claude-app-engineering — **gaps: no _computer-vision_ owner; no _realtime-collaboration_ owner.**
- **Specialized eng:** blockchain-web3, embedded-iot, game-development, accessibility-engineering, localization-i18n, search-relevance, experimentation-growth, email-engineering, geospatial, wordpress-cms — **gap: no _streaming-media_ owner; no _realtime-collaboration_ owner.**
- **Dev-lifecycle meta:** developer-tooling (build/monorepo), developer-relations (advocacy/community), technical-writing-docs, engineering-management, project/technical-program-management — **gap: no owner for the _open-source project maintenance_ craft (licensing, governance, semver/release management, deprecation, coordinated security releases, supply-chain provenance).** ← this run.
- **Business / verticals:** ~70 plugins. Business-side carry-overs remain **held pending real demand** per the #409 decision.

## The 10 candidates (prioritized)

Scoring: **Demand** (how often a real practitioner needs this) × **Feasibility** (durable craft, not volatile facts that rot) × **Disjoint** (low overlap with an existing plugin). 1–5 each; Priority = sum.

| # | Candidate | Demand | Feas. | Disjoint | Priority | Closest existing → seam |
|---|---|---|---|---|---|---|
| 1 | **open-source-maintenance** ✅ *(built here)* | 4 | 5 | 5 | 14 | developer-relations (advocacy) / devops-cicd (pipeline) / security-engineering (vuln) → owns the _maintainer craft_: license, governance, triage, semver/changelog, deprecation, coordinated security release, provenance |
| 2 | **realtime-collaboration-engineering** *(carry-over, unbuilt)* | 4 | 4 | 5 | 13 | frontend/backend → multiplayer/collab: CRDT vs OT, WebSocket/WebRTC transport, presence/awareness, offline merge, the sync server |
| 3 | **streaming-media-engineering** | 3 | 4 | 5 | 12 | backend / game-dev → audio/video delivery: HLS/DASH packaging, transcode ladders, DRM, low-latency (LL-HLS/WebRTC), CDN/ABR, player QoE |
| 4 | **computer-vision-engineering** *(carry-over, unbuilt)* | 3 | 4 | 4 | 11 | ml-engineering (generic MLOps) → CV craft: detection/segmentation/OCR, annotation/dataset hygiene, augmentation, mAP/IoU eval, edge/realtime inference |
| 5 | **ux-research** | 4 | 4 | 3 | 11 | web-design (ux-designer = wireframes) / product-management (what/why) → research methods: interviews, usability tests, surveys, JTBD, personas, research ops, sample/bias rigor |
| 6 | **design-systems-engineering** | 3 | 4 | 4 | 11 | web-design (visual/tokens) / frontend (components) → DS as a product: token architecture, component API/governance, Figma↔code, versioning a DS, contribution model |
| 7 | **knowledge-management-engineering** | 3 | 4 | 3 | 10 | technical-writing-docs (product docs) → internal KM: wiki IA, search relevance for docs, knowledge ops, decision records, stale-content lifecycle |
| 8 | **robotics-engineering (ROS)** | 2 | 3 | 5 | 10 | embedded-iot (devices) → ROS 2 nodes/topics/actions, URDF, sim (Gazebo/Isaac), perception↔control loop, realtime constraints |
| 9 | **bioinformatics-engineering** | 2 | 3 | 5 | 10 | data-science-research (generic) / clinical-trials (ops) → sequence/variant pipelines, Nextflow/Snakemake, reference genomes, FAIR data |
| 10 | **accessibility-of-native-apps** *(carry-over, stretch)* | 3 | 3 | 4 | 10 | accessibility-engineering (web/WCAG) → native a11y APIs (UIA / AX / AccessKit) for desktop + TUI; pairs with desktop-app + cli-tooling |

### Per-candidate brief — purpose, approach, dependencies

**1. open-source-maintenance** — The maintainer's craft, which no plugin owned. `developer-relations` grows the community, `developer-tooling` builds the monorepo, `devops-cicd` runs the pipeline, `technical-writing-docs` writes the docs — but *nobody* owned **licensing, governance, issue/PR triage policy, semver discipline, changelogs, release automation, deprecation/breaking-change windows, coordinated security releases, dependency intake, and supply-chain provenance.** *Purpose:* run a public project people can use, trust, and contribute to. *Approach:* 2 agents (oss-maintainer-strategist = stewardship; release-and-versioning-engineer = release), 5 skills, a knowledge bank (two Mermaid decision trees — licensing + semver/release — plus community-health/governance and a dated 2026 tooling map), 8 best-practices, 4 templates (CONTRIBUTING/SECURITY/release-checklist/governance), 1 advisory hook. *Deps:* ravenclaude-core; seams to devops-cicd, security-engineering, developer-relations, technical-writing-docs, developer-tooling. **Highest feasibility in the list — the craft is almost entirely durable (SemVer, Keep a Changelog, SPDX/copyleft reach, coordinated disclosure are stable specs); only the tooling map is dated/`verify-at-use`.** ← built in this PR.

**2. realtime-collaboration-engineering** *(carry-over)* — Multiplayer/collaborative editing (Figma/Notion-style): CRDT vs OT by merge cost, transport (WebSocket vs WebRTC, SFU vs mesh), presence/awareness, offline reconciliation, the sync server. *Approach:* 3 agents (collab-architect, sync-engine-engineer, presence-and-transport-engineer). *Deps:* frontend-engineering, backend-engineering, data-streaming.

**3. streaming-media-engineering** — Audio/video delivery infrastructure: HLS/DASH packaging, transcode/bitrate ladders, DRM/Widevine/FairPlay, low-latency (LL-HLS, WebRTC), CDN + adaptive bitrate, and player QoE metrics. *Approach:* 3 agents (media-pipeline-architect, transcode-and-packaging-engineer, delivery-and-playback-engineer). *Deps:* backend-engineering, aws/gcp (MediaConvert/Transcoder), performance-engineering. *Risk:* codec/DRM specifics dated.

**4. computer-vision-engineering** *(carry-over)* — The CV specialization `ml-engineering` is too generic for: task framing (classification/detection/segmentation/OCR/pose), annotation + dataset hygiene, augmentation, transfer learning, evaluation (mAP/IoU), edge/realtime inference (ONNX/TensorRT/CoreML). *Approach:* 3 agents (cv-architect, vision-model-engineer, edge-inference-engineer). *Deps:* ml-engineering, data-platform. *Risk:* model/tooling facts volatile.

**5. ux-research** — The research-methods lane no plugin owns: `web-design`'s ux-designer does wireframes/conversion and `product-management` owns the what/why, but neither owns *how to know* — interview/usability-test design, survey rigor, sampling/bias, JTBD, persona/journey synthesis, and research ops. *Approach:* 1–2 agents (ux-researcher [+ research-ops-strategist]). *Deps:* web-design, product-management, applied-statistics (the significance seam). Methodology vertical → advisory, low runtime, like applied-statistics.

**6. design-systems-engineering** — A design system as a *product*: token architecture (primitive→semantic→component), component API design + governance, Figma↔code sync, versioning/releasing a DS (semver for components!), and the contribution model. *Approach:* 2 agents (design-system-architect, component-library-engineer). *Deps:* web-design, frontend-engineering; **strong seam to #1 (a DS is a released, versioned, contributed-to artifact).**

**7. knowledge-management-engineering** — Internal knowledge ops, distinct from product docs: wiki IA, search relevance for an internal corpus, decision records (ADRs), and the stale-content lifecycle. *Approach:* 2 agents (km-architect, knowledge-ops-engineer). *Deps:* technical-writing-docs, search-relevance-engineering.

**8. robotics-engineering (ROS)** *(stretch)* — ROS 2 nodes/topics/services/actions, URDF, simulation (Gazebo/Isaac), the perception↔planning↔control loop, realtime constraints. *Deps:* embedded-iot-engineering, ml-engineering. *Niche but fully unowned.*

**9. bioinformatics-engineering** *(stretch)* — Sequence/variant pipelines, Nextflow/Snakemake workflow craft, reference data management, reproducibility/FAIR. *Deps:* data-science-research, data-orchestration. *Niche, unowned.*

**10. accessibility-of-native-apps** *(carry-over, stretch)* — Native accessibility APIs (Windows UI Automation, macOS AX, AccessKit) for desktop apps + TUIs, distinct from `accessibility-engineering`'s web/WCAG lane. *Deps:* accessibility-engineering, desktop-app-engineering, cli-tooling-engineering.

## Prioritization rationale

- **#1 open-source-maintenance** is the highest-value, lowest-risk build now. It closes a **genuinely unowned lane in the dev-lifecycle-meta cluster** — the marketplace had every *adjacent* role (DevRel, build tooling, CI/CD, docs, security) but no owner for the *maintainer's* craft of stewardship + release management. **Demand is broad** (almost every team ships or depends on open source), **feasibility is maximal** (the craft is built on stable specs — SemVer, Keep a Changelog, SPDX/copyleft, coordinated disclosure — so the knowledge barely rots; only the tooling map is dated), and **overlap is near-zero** (the closest plugins are all clean seams, not duplications). It mirrors the proven two-agent advisory+doing recipe (applied-statistics / customer-success-analytics).
- **#2 realtime-collaboration, #3 streaming-media** are the next tier: durable engineering craft, genuinely unowned lanes, clean seams.
- **#4 computer-vision, #5 ux-research, #6 design-systems** are strong but each carries either volatile facts (CV) or a thinner disjoint margin (ux-research vs product-management; design-systems vs web-design) — buildable, with care on the seam.
- **#7–#10** are valuable but niche/stretch (robotics, bioinformatics) or pair with already-built plugins (native-a11y, KM); hold pending real demand per the #409 policy.

## Build status (this PR)

- **#1 open-source-maintenance — BUILT.** Full plugin to the marketplace quality bar: 2 agents (scenario-schema complete, each description ≤300 chars), 5 skills, a knowledge bank (licensing + semver/release Mermaid decision trees, community-health/governance, a dated 2026 tooling map), 8 best-practice rules, 4 templates, 1 advisory ERE-only hook, README + CLAUDE.md + CHANGELOG. Registered in `.claude-plugin/marketplace.json` and the `docs/architecture.md` roster. Globs already covered by `.repo-layout.json` (`plugins/*/**`).
- **#2–#10 — SCOPED, NOT YET BUILT.** Each existing plugin is ~25–45 files of cited, CI-gated content. Building all ten to the depth bar in one pass would fail the frontmatter/scenario gates and dilute the marketplace — the documented anti-pattern. One complete, gate-passing plugin plus this fully-scoped, prioritized roadmap is the higher-value deliverable; the remaining nine are ready to build in priority order, business-side carry-overs awaiting real demand per the #409 decision.

## Blockers / notes

- **No technical blockers** were hit building #1 — the JSON, frontmatter (incl. the 300-char agent cap + scenario schema), prettier, ruff, md-link, version-sync, and marketplace-claims structural gates are all runnable locally (see the PR description for the gate run).
- The only real constraint is **breadth vs depth** plus the standing **build-on-real-demand** policy: ten shallow plugins would fail gates and dilute the catalog. The responsible deliverable is one excellent plugin in the cleanest remaining structural gap + this roadmap.
- **Routine-collision note for the next run:** before building, read `plugins/` on disk *and* the latest `docs/proposals/*-ten-new-plugin-candidates.md`, then pick the highest-priority row **not** already on disk. As of 2026-06-23 the top unbuilt rows are #2 realtime-collaboration-engineering and #3 streaming-media-engineering.
