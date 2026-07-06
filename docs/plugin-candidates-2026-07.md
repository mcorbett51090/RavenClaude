# Plugin candidates — 2026-07 research pass

> Research + prioritization for **10 new RavenClaude plugins** not yet in the
> catalog. Method: enumerate the current 131-plugin roster (`.claude-plugin/marketplace.json`),
> map its clusters, then find genuine whitespace — capabilities that a real user
> would ask a specialist team for and that **no existing plugin already owns**.
> Each candidate is scored on **user demand** × **technical feasibility** (how
> confidently the marketplace can author authoritative, durable content for it).
>
> **Build order chosen this pass:** the two highest-demand / highest-feasibility /
> cleanest-whitespace **engineering** picks — `computer-vision-engineering` (P1)
> and `streaming-media-engineering` (P2) — are built in this PR. The remaining
> eight are scoped-and-ready below.

## How the gaps were found

The catalog already covers, densely:

- **Software-delivery chain** — devops-cicd, observability-sre, security-engineering,
  qa-test-automation, cloud-native-kubernetes, terraform-iac, platform-engineering-idp,
  performance-engineering, incident-response-dfir, developer-tooling.
- **Cloud** — aws / azure / gcp, finops-cloud-cost.
- **App craft** — backend, frontend, mobile, desktop-app, database, api, auth-identity,
  browser-extension, cli-tooling, email, realtime-collaboration, localization-i18n,
  wordpress-cms, web-design.
- **Data & AI** — data-platform, analytics-engineering, data-orchestration,
  data-streaming (Kafka/Flink **data**, not media), ml-engineering (**generic** ML),
  ai-rag-engineering, ai-coding-model-guidance, data-governance-privacy,
  applied-statistics, data-science-research, geospatial, search-relevance, tableau,
  microsoft-fabric, claude-app-engineering.
- **Emerging-tech engineering** — blockchain-web3, ar-vr-xr, game-development,
  embedded-iot (**firmware**, not hardware), robotics-autonomous-systems.
- **~60 business & industry verticals** — from accounting and dental to freight,
  hospice, mortgage, restaurant, veterinary, wealth-management.

The whitespace falls in three bands: **specialist engineering disciplines** that
`ml-engineering` / `data-streaming` / `embedded-iot` are too generic to own; a
**modern creator/monetization** business; and **service-vertical operations** with
distinct unit economics that the current verticals don't cover.

---

## The 10 candidates (ranked)

| # | Plugin | Cluster | Demand | Feasibility | Score | Whitespace vs. nearest existing |
|---|---|---|---|---|---|---|
| **P1** | **computer-vision-engineering** | Eng / AI | High | High | ★★★★★ | `ml-engineering` is generic training/MLOps; CV is its own discipline (detection/segmentation/OCR/tracking, video analytics, edge inference, annotation ops, camera calibration). |
| **P2** | **streaming-media-engineering** | Eng / Media | High | High | ★★★★★ | `data-streaming-engineering` = Kafka/Flink **data** streams; `film-video-production` = content. Nobody owns **video/audio delivery**: transcode ladders, ABR (HLS/DASH/CMAF/LL-HLS), WebRTC, CDN, DRM, QoE. |
| **P3** | **telehealth-operations** | Vertical / Health | High | High | ★★★★☆ | The in-person practice plugins (dental, optometry, PT, behavioral-health) don't own virtual-care ops: modality (sync/async/RPM), cross-state licensure, telehealth reimbursement, patient throughput. |
| **P4** | **creator-economy-operations** | Business | Med-High | High | ★★★★☆ | `marketing-operations` / `developer-relations` don't own a **creator business**: platform mix, newsletter/podcast/membership monetization, brand deals, audience funnel, MRR. |
| **P5** | **hardware-electronics-engineering** | Eng | Med | Med | ★★★☆☆ | `embedded-iot-engineering` owns firmware/HAL; nobody owns the **board**: schematic capture, PCB layout, DFM/DFT, BOM, signal/power integrity, EMC/FCC/CE. |
| **P6** | **self-storage-operations** | Vertical | Med | High | ★★★☆☆ | Clean whitespace: revenue management (dynamic street rate + ECRI), unit mix, delinquency→lien→auction, ancillary (insurance/retail), unattended/remote ops. |
| **P7** | **tutoring-test-prep-operations** | Vertical / Edu | Med | High | ★★★☆☆ | `edtech-partner-success` = B2B EdTech vendor CS; a tutoring center/agency's ops (enrollment funnel, tutor utilization & pay, session scheduling, package revenue, outcomes) is distinct. |
| **P8** | **llm-evaluation-and-guardrails-engineering** | Eng / AI | High | Med | ★★★☆☆ | Overlap risk with `claude-app-engineering` / `ai-rag-engineering`. Scoped narrowly to **evals + guardrails + LLM observability** (LLM-as-judge, offline/online eval, injection defense, cost/latency SLOs) it is distinct; needs a sharp seam statement. |
| **P9** | **catering-events-operations** | Vertical | Med | High | ★★★☆☆ | `restaurant-operations` = on-premise; `event-management` = the planner. Off-premise **catering**: BEO, event food-cost, event labor, rentals/logistics, deposits/contracts, menu engineering. |
| **P10** | **brewery-winery-distillery-operations** | Vertical | Med | Med | ★★★☆☆ | Craft-beverage **production + taproom + distribution**: batch/COGS, TTB/excise compliance, three-tier distribution, taproom P&L. Distinct from `restaurant-operations` and `cannabis-operations`. |

**Alternates considered, deprioritized:** pest-control-operations and
landscaping-lawn-care-operations (both largely served by `field-service-management`
+ `skilled-trades-contracting`); grant-management (served by `nonprofit-fundraising`);
podcast-production (thin as a standalone team — folds into P4).

---

## Per-candidate implementation approach & dependencies

All candidates follow the marketplace's proven **2–3-agent plugin shape** (see
`browser-extension-engineering` / `network-engineering` for the lean 2-agent
reference build): `plugin.json` + `README.md` + `CLAUDE.md` team constitution,
2+ agents with the full scenario-authoring frontmatter, a knowledge bank with at
least one **Mermaid decision tree** + a **dated** capability reference, 2–3 skills,
grep-able best-practices, and registration in `marketplace.json` +
`docs/architecture.md`. Every one **requires `ravenclaude-core@>=0.7.0`** and
carries retrieval-dated citations for volatile facts.

### P1 — computer-vision-engineering *(built this PR)*
- **Agents:** `cv-systems-architect` (task framing, model-family + accuracy/latency-budget + deployment-target selection, dataset/annotation strategy, eval design) and `cv-implementation-engineer` (pipeline build: preprocessing, training/fine-tuning or off-the-shelf, inference/serving, edge/real-time optimization).
- **Approach:** decision-tree knowledge (task → model family; cloud vs edge inference) + a dated 2026 model/tooling map (YOLO/DETR/SAM/vision-LLMs, ONNX/TensorRT/OpenVINO, annotation tooling). Skills: `frame-a-cv-task`, `design-cv-dataset-and-eval`, `optimize-cv-inference`.
- **Deps:** none beyond core. **Seams:** generic training/MLOps → `ml-engineering`; RAG/text → `ai-rag-engineering`; on-device firmware → `embedded-iot-engineering`; media pipelines → P2.

### P2 — streaming-media-engineering *(built this PR)*
- **Agents:** `streaming-media-architect` (live-vs-VOD, latency tier, protocol/packaging/DRM/CDN selection, QoE strategy) and `media-pipeline-engineer` (transcode ladder, packaging, player/ABR, CDN config, DRM integration).
- **Approach:** decision trees (latency tier → protocol; DRM matrix) + a dated 2026 codec/protocol/DRM/CDN reference (H.264/HEVC/AV1, HLS/LL-HLS/DASH/CMAF, WebRTC/WHIP/WHEP, Widevine/FairPlay/PlayReady). Skills: `design-streaming-delivery`, `build-transcode-ladder`, `diagnose-playback-qoe`.
- **Deps:** none beyond core. **Seams:** data streams → `data-streaming-engineering`; content production → `film-video-production`; CDN cost → `finops-cloud-cost`; player UI → `frontend-engineering`.

### P3 — telehealth-operations
- **Agents:** `telehealth-operations-lead`, `virtual-care-workflow-manager`, `telehealth-billing-compliance-advisor`.
- **Approach:** modality decision tree (sync/async/RPM/e-consult), a dated licensure/reimbursement reference (state compacts, CMS telehealth billing, originating-site rules). Advisory only, not legal/clinical; HIPAA-aware, no PHI.
- **Deps:** core. **Seams:** in-person practices (dental/optometry/PT/behavioral-health), `medical-revenue-cycle`, `regulatory-compliance`.

### P4 — creator-economy-operations
- **Agents:** `creator-business-lead`, `audience-growth-strategist`, `monetization-and-deals-advisor`.
- **Approach:** monetization-mix decision tree (ads/subscriptions/memberships/products/sponsorships), platform-portfolio + funnel model, a dated 2026 platform/payout reference. Advisory, no PII.
- **Deps:** core. **Seams:** `marketing-operations`, `ecommerce-dtc`, `developer-relations`.

### P5 — hardware-electronics-engineering
- **Agents:** `hardware-systems-architect`, `pcb-design-engineer`.
- **Approach:** decision trees (component/architecture selection; when to spin a board vs use a module), a dated EDA/fab/compliance reference (KiCad/Altium, JLCPCB/fab DFM rules, EMC/FCC/CE). Engineering decision-support, not certification.
- **Deps:** core. **Seams:** firmware → `embedded-iot-engineering`; enclosures/mechanical out of scope; RF/compliance verdicts flagged.

### P6 — self-storage-operations
- **Agents:** `self-storage-operations-lead`, `revenue-and-occupancy-manager`, `delinquency-and-lien-advisor`.
- **Approach:** revenue-management tree (street rate vs in-place, ECRI cadence), a dated ancillary/lien reference (state lien-law variance, tenant insurance/protection plans). Advisory, jurisdiction-specific lien rules dated; no tenant PII.
- **Deps:** core. **Seams:** `property-management`, `field-service-management`.

### P7 — tutoring-test-prep-operations
- **Agents:** `tutoring-center-lead`, `enrollment-and-scheduling-manager`, `tutor-utilization-and-outcomes-advisor`.
- **Approach:** delivery-model tree (1:1 / small-group / online / hybrid), tutor-economics model (utilization, pay vs bill rate), package/retainer revenue, outcomes tracking. Advisory; FERPA-aware, no student PII.
- **Deps:** core. **Seams:** `edtech-partner-success` (B2B vendor), `people-operations-hr`.

### P8 — llm-evaluation-and-guardrails-engineering
- **Agents:** `llm-eval-architect`, `guardrails-and-safety-engineer`.
- **Approach:** eval-strategy tree (offline benchmark vs LLM-as-judge vs human vs online A/B), guardrails matrix (input/output filters, injection defense, PII redaction, cost/latency SLOs). **Requires a sharp seam** to `claude-app-engineering` (build) and `ai-rag-engineering` (retrieval) to avoid overlap.
- **Deps:** core. **Seams:** `claude-app-engineering`, `ai-rag-engineering`, `ml-engineering`, `trust-and-safety`.

### P9 — catering-events-operations
- **Agents:** `catering-operations-lead`, `event-costing-and-beo-manager`, `event-staffing-and-logistics-advisor`.
- **Approach:** event-type tree (drop-off vs full-service vs venue), event food-cost & labor model, BEO + deposit/contract discipline. Advisory, no client PII.
- **Deps:** core. **Seams:** `restaurant-operations` (on-prem), `event-management` (the planner).

### P10 — brewery-winery-distillery-operations
- **Agents:** `craft-beverage-operations-lead`, `production-and-cogs-manager`, `distribution-and-compliance-advisor`.
- **Approach:** channel-mix tree (taproom vs self-distribution vs three-tier), batch-COGS model, a dated TTB/excise + three-tier reference. Advisory; excise/TTB rules dated, jurisdiction-specific.
- **Deps:** core. **Seams:** `restaurant-operations`, `manufacturing-operations`, `supply-chain-planning`.

---

## Prioritization rationale

1. **Demand × feasibility, weighted to demand.** The two P-tier picks are
   high-demand *engineering* disciplines the marketplace can author authoritatively
   today (durable mechanics, well-documented tooling). They also have the cleanest
   seams — each has an obvious "nearest neighbor" plugin whose scope it clearly does
   *not* overlap, which is the strongest signal of real whitespace.
2. **Engineering before verticals for the first build.** Engineering plugins reuse
   more of the existing knowledge-bank pattern and have less jurisdiction-specific,
   date-sensitive content to keep fresh, so they carry lower maintenance risk.
3. **Overlap risk pushes P8 down** despite high demand: LLM-eval sits adjacent to
   three existing AI plugins and needs a carefully drawn seam before it earns a slot.
4. **Verticals (P3, P6, P7, P9, P10) are high-feasibility but demand-medium**, and
   their value depends on dated, jurisdiction-specific facts (licensure, lien law,
   excise) that need a freshness discipline — best built once the engineering picks
   have validated the 2-agent lean shape in this PR.

## Blocker / scope note

Building **all 10** to the marketplace's quality bar (each: 2–3 fully-authored
agents, a Mermaid-backed knowledge bank, skills, best-practices, and gate-passing
manifests) is **multi-session work** — a single plugin at this depth is a
substantial authoring effort, and the CI gates (`check-frontmatter.py` scenario
schema, description parity, `check-marketplace-claims.py` structural checks,
layout + prettier) reject shallow shells. This PR therefore ships the **two
highest-priority plugins fully built and gate-passing**, plus this scoped research
doc for the remaining eight, rather than ten incomplete stubs. The eight are
sequenced above and can each be built in a follow-up pass using the P1/P2 builds
as the reference template.
