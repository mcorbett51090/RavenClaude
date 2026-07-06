# New plugin candidates — research, prioritization & build (2026-07-03)

Research pass over the RavenClaude marketplace (**131 plugins** at time of writing)
to identify a fresh batch of **10 high-demand, technically-feasible plugin gaps**
and build out the top three.

Continues the cadence of the prior candidate docs
([`2026-07-01`](new-plugin-candidates-2026-07.md) shipped `incident-response-dfir`;
[`2026-07-02`](new-plugin-candidates-2026-07-02.md) shipped 10 verticals + robotics +
AR/VR/XR). Every pick below was checked against the current roster **and** against
those prior docs' build lists — none collide with anything already built or with each
other.

## Method

1. Enumerated the current roster (`ls plugins/` + `.claude-plugin/marketplace.json`) —
   131 plugins across engineering specialties, cloud/data/ML, and ~55 industry verticals.
2. Cross-referenced the prior candidate docs so already-built picks (robotics, AR/VR/XR,
   DFIR, network-engineering) and their roadmaps are not re-proposed as "new".
3. Mapped remaining white space along the two axes the marketplace splits on —
   **engineering disciplines** and **business/vertical operations** — keeping only domains
   with a large operator base and a *durable* knowledge core distinct from the nearest
   existing plugin.
4. Scored survivors on **user demand** × **technical feasibility** (how groundable the
   domain is without a live external system).

## Implementation approach & dependencies (shared)

Every candidate reuses the **established engineering-/operations-team shape** (reference:
`plugins/ar-vr-xr-engineering/`):

- `.claude-plugin/plugin.json` + `README.md` + `CLAUDE.md` + `CHANGELOG.md`
- `agents/` — **3 agents** (a lead + two function specialists) with the full
  scenario-authoring frontmatter schema (`audience`, `works_with`, `scenarios[]`,
  `quickstart`), each `description` ≤ 300 chars; agent `name`s domain-prefixed for global
  uniqueness.
- `skills/` — **4** SKILL.md capability files.
- `knowledge/` — a Mermaid **decision-tree** file + a **dated 2026 reference**
  (retrieval-dated, verify-at-use) so volatile figures never masquerade as durable facts.
- `best-practices/` — a README + **5** durable principle notes.
- `templates/` — **2** operator artifacts; `commands/` — **2** slash commands.
- **No bundled hooks / MCP / Python** in this batch — keeps the CI gate surface minimal.

Dependency: each declares `requires: ravenclaude-core@>=0.7.0`. No external services, no
secrets, no PII. Each is added to `.claude-plugin/marketplace.json`; the `plugins/*/...`
globs already in `.repo-layout.json` cover every file, so no layout-manifest change is
needed.

## The 10 candidates

### Engineering-discipline gaps

| # | Plugin | Scope (and the nearest existing plugin it is NOT) | Distinctive build notes |
|---|--------|---------------------------------------------------|-------------------------|
| 1 | **computer-vision-engineering** | Production vision systems — detection/segmentation/OCR/video-analytics, annotation pipelines, edge/embedded inference. *Not `ml-engineering`* (MLOps-broad) — vision-specific. | Agents: cv-systems-architect / cv-model-engineer / vision-deployment-engineer. Task-selection, build-vs-API, model-family, and deployment-target trees. |
| 2 | **conversational-ai-voice-engineering** | Real-time voice agents — ASR/TTS pipeline, latency budget, turn-taking/barge-in, telephony/SIP, IVR. *Not `ai-rag-engineering`* (text) or the prior roadmap's `conversation-design` (UX). | Agents: voice-ai-architect / speech-pipeline-engineer / dialog-and-integration-engineer. Cascade-vs-speech-to-speech + build-vs-platform trees. |
| 3 | **streaming-media-engineering** | Video/audio streaming — transcoding, HLS/DASH/CMAF/WebRTC, DRM, CDN, playback QoE. *Not `film-video-production`* (creative ops) or `data-streaming-engineering` (Kafka). | Agents: media-streaming-architect / transcoding-pipeline-engineer / playback-and-delivery-engineer. Protocol/codec/low-latency trees. |
| 4 | **time-series-forecasting-engineering** | Forecasting & anomaly-detection systems — classical (ARIMA/ETS) vs ML vs deep, backtesting, feature/lag design, drift. *Not `data-science-research`* / `analytics-engineering`. | Model-family-by-horizon-and-data tree; backtesting-methodology reference. |
| 5 | **quantum-computing-engineering** | Circuit design, Qiskit/Cirq/PennyLane, error mitigation, hybrid classical-quantum, hardware-vs-simulator. Frontier gap. | Volatile hardware landscape → heavy `[verify-at-use]`. Lowest demand → last. |

### Industry / operations gaps

| # | Plugin | Scope (and the nearest existing plugin it is NOT) | Distinctive build notes |
|---|--------|---------------------------------------------------|-------------------------|
| 6 | **tax-preparation-practice** | Tax-prep firm ops — 1040/business returns, e-file workflow, IRS-notice response, client doc intake, season capacity. *Not `accounting-bookkeeping`* (books, not returns). | Compliance-sensitive: no PII/PTIN; cite IRS forms/deadlines with retrieval date. |
| 7 | **management-consulting** | Engagement delivery — hypothesis-driven structuring (issue trees, MECE), workplan, interviews, deck craft, recommendations. No existing PS-delivery plugin. | Method- and template-heavy, low data-sensitivity. |
| 8 | **hospital-health-system-operations** | Patient-flow, capacity/throughput, bed management, ED/OR ops, staffing ratios, length-of-stay. *Not* the single-clinic verticals (dental/optometry/PT). | HIPAA-adjacent: no PHI; clinical-ops judgment, not medical advice. |
| 9 | **self-storage-operations** | Facility ops — occupancy/rate management (dynamic pricing), delinquency/lien/auction workflow, unit mix, remote/kiosk ops. SMB vertical gap. | Lien-law is jurisdictional → cite with retrieval date + verify-at-use. |
| 10 | **telecom-network-operations** | Telco/ISP NOC & OSS/BSS — service assurance, fault/incident, provisioning, capacity, SLA. *Not `network-engineering`* (enterprise) — carrier/operator ops. | Overlaps `network-engineering`/`observability-sre` — draw seams carefully. |

## Prioritization

Ranked by **(user demand × technical feasibility)**.

| Rank | Candidate | Demand | Feasibility | Why |
|------|-----------|--------|-------------|-----|
| **1** | computer-vision-engineering | High | High | Top-3 applied-AI workload; clean template fit; low overlap with `ml-engineering`. |
| **2** | conversational-ai-voice-engineering | High | High | Voice AI is a 2025–26 breakout; no plugin owns the speech-pipeline/latency/telephony scope. |
| **3** | streaming-media-engineering | Med-High | High | Durable, well-bounded discipline; the two nearby plugins are clearly *not* it. |
| 4 | time-series-forecasting-engineering | Med | High | Common but partially served by `data-science-research`. |
| 5 | tax-preparation-practice | Med | Med | Strong SMB fit; needs careful compliance framing. |
| 6 | management-consulting | Med | High | Template/method heavy; easy to build. |
| 7 | hospital-health-system-operations | Med | Med | Valuable but broad; scope tightly vs single-clinic verticals. |
| 8 | self-storage-operations | Low-Med | High | Clean SMB gap; smaller audience. |
| 9 | telecom-network-operations | Low-Med | Med | Overlap risk needs careful seams. |
| 10 | quantum-computing-engineering | Low | Med | Frontier novelty, volatile landscape, smallest audience. |

## Build status (this PR)

- ✅ **computer-vision-engineering** — built to the full house standard.
- ✅ **conversational-ai-voice-engineering** — built to the full house standard.
- ✅ **streaming-media-engineering** — built to the full house standard.
- ⏭️ Candidates **4–10** — documented above as the prioritized, ready-to-build backlog for
  the next passes; each already has its agent roster, decision-tree list, and
  distinctive-risk note, so a follow-up session can start at rank 4 without re-researching.

Each built plugin clears the CI gates: frontmatter schema (`scripts/check-frontmatter.py`),
the ≤300-char agent-description cap, cross-plugin agent-name uniqueness, the layout
allow-list, prettier, and the gate-audit meta-test.
