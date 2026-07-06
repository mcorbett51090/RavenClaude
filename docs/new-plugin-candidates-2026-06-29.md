# New plugin candidates — research & prioritization (2026-06-29)

> Routine-generated gap analysis of the RavenClaude marketplace. Surveys the **~120 plugins** already shipped (`plugins/` + `.claude-plugin/marketplace.json`), identifies under-served domains, and proposes **10 net-new plugin candidates** with purpose, value, implementation approach, dependencies, and a demand × feasibility prioritization.
>
> **Scope honesty:** building 10 plugins to this repo's standard (each: `plugin.json` + `CLAUDE.md` + `README.md` + multiple agents with the full scenario-authoring frontmatter schema + skills + a citation-grounded knowledge bank + best-practices + templates + an advisory hook, all passing the frontmatter / layout / prettier / version-sync / gate-audit CI gates) is a multi-PR effort, not a single unattended run. This routine ships the **#1 priority built end-to-end** (`network-engineering`) and scopes the remaining nine here as implementation-ready outlines.

## Method

1. Enumerated existing plugins from the directory tree and `marketplace.json`.
2. Clustered them (software-delivery, cloud, app-craft, data/AI, Microsoft stack, business/product, and ~40 verticals).
3. Checked each candidate against existing **agent names** (the orchestrator routing key — must be globally unique; `scripts/check-frontmatter.py` enforces it) and existing plugin scopes to avoid duplication.
4. Scored candidates on **demand** (how often the domain shows up in real consulting/eng work) × **feasibility** (stable, well-documented domain knowledge → low hallucination risk → high build quality).

## What is already well covered (so these are NOT candidates)

- **Software delivery / platform:** devops-cicd, observability-sre, security-engineering, qa-test-automation, cloud-native-kubernetes, terraform-iac, platform-engineering-idp, developer-tooling, performance-engineering, realtime-collaboration-engineering.
- **Cloud:** aws-cloud, azure-cloud, gcp-cloud, finops-cloud-cost. (These own **VPC-level** networking — see the gap note for `network-engineering`.)
- **App craft:** backend, frontend, mobile, desktop, database, api, auth-identity, browser-extension, email, cli-tooling, embedded-iot, wordpress-cms, localization-i18n, accessibility, game-development.
- **Data / AI:** data-platform, data-orchestration, data-streaming, analytics-engineering, ml-engineering, ai-rag-engineering, data-science-research, applied-statistics, search-relevance, data-governance-privacy, microsoft-fabric, tableau, claude-app-engineering, ai-coding-model-guidance.
- **Microsoft stack:** power-platform, microsoft-365-copilot, microsoft-graph.
- **Verticals (40+):** healthcare (dental, optometry, PT, vet, pharmacy, behavioral-health, hospice, senior-care, clinical-trials, medical-revenue-cycle), real estate (commercial, property-mgmt, mortgage), legal (ops-clm, small-firm), finance (corporate, fintech-payments, wealth-management-ria, accounting-bookkeeping, insurance P&C + life/health), and many operations verticals (restaurant, retail, hotel, manufacturing, construction, fleet-logistics, field-service, event-management, automotive-dealership, cannabis, etc.).

## The 10 candidates

| # | Candidate | One-line purpose | Gap evidence |
|---|---|---|---|
| 1 | **network-engineering** | Enterprise/campus/DC/WAN network craft: routing & switching, firewalls, DNS/DHCP/IPAM, load balancing, SD-WAN, zero-trust network access. | Cloud plugins own **VPC-level** networking only; `service-mesh-networking-engineer` owns east-west service mesh. No plugin owns L2/L3 physical + enterprise network design. |
| 2 | **tax-advisory** | US tax preparation & planning for SMBs/individuals: entity choice, deductions/credits, quarterly estimates, multi-state nexus, year-end planning. | `accounting-bookkeeping` & `finance` own books/close/FP&A; neither owns tax return prep or tax-planning strategy. |
| 3 | **content-marketing-social** | Content & social-media execution: editorial calendar, channel-native content, SEO content briefs, community management, performance loop. | `marketing-operations` is strategy/martech-ops; `web-design/content-strategist` is on-site copy. No execution-layer content/social plugin. |
| 4 | **public-relations-comms** | Corporate comms & PR: press releases, media relations, crisis comms, exec/internal comms, messaging frameworks. | No comms/PR plugin; marketing-operations doesn't own earned media or crisis comms. |
| 5 | **ar-vr-spatial-engineering** | Spatial computing: Unity/Unreal XR, OpenXR, visionOS/Quest, hand/eye tracking, spatial UX, comfort/perf budgets. | `game-development` owns game craft; no XR/spatial-computing plugin. |
| 6 | **utilities-operations** | Electric/water/gas utility ops: outage management, AMI/metering, GIS asset mgmt, regulatory (NERC/PUC), demand response. | `renewable-energy` is generation/development; no T&D / utility-operations plugin. |
| 7 | **telecom-operations** | Carrier/ISP ops: OSS/BSS, provisioning, network ops, plant records, FCC/USF compliance, broadband deployment (BEAD). | No telecom plugin; cloud/network plugins don't cover carrier OSS/BSS. |
| 8 | **chiropractic-practice** | Single-provider chiropractic clinic ops (mirrors dental/optometry/PT pattern): scheduling, SOAP notes, billing/coding, care plans. | Fits the proven single-provider-practice plugin family; chiropractic not yet covered. |
| 9 | **childcare-operations** | Daycare/preschool ops: enrollment & ratios, licensing compliance, subsidy billing (CCDF), curriculum, family comms. | No childcare/early-education-operations plugin. |
| 10 | **media-streaming-engineering** | Video/audio streaming: encoding/transcoding (ABR/HLS/DASH), CDN, DRM, low-latency live, player QoE. | `film-video-production` is production; no streaming-delivery engineering plugin. |

## Per-candidate implementation approach & dependencies

All candidates follow the established plugin shape and **require `ravenclaude-core@>=0.7.0`** (inherit the Capability Grounding + Structured Output protocols, Team Lead routing, comfort-posture, decision-review). Engineering plugins seam to the relevant cloud/devops plugins; verticals seam to finance/accounting/legal for cross-cutting concerns. Each ships ≥1 advisory `PreToolUse` hook flagging domain anti-patterns and a citation-grounded knowledge bank with Mermaid decision trees.

1. **network-engineering** — 2 agents (`network-architect`, `network-operations-engineer`). Knowledge: a topology/segmentation decision tree + a routing-protocol selection tree + a 2026 capability map. Skills: design-network-topology, select-routing-protocol, design-segmentation-and-zero-trust, troubleshoot-connectivity, plan-network-change. Hook: flag risky configs (any/any firewall rules, telnet, no change window). Seams: cloud VPCs → aws/azure/gcp-cloud; service mesh → realtime-collaboration/k8s; security verdicts → security-engineering. **Names verified unique** (`network-engineer` is azure's; mine differ).
2. **tax-advisory** — 2 agents (`tax-strategist`, `tax-prep-specialist`). Knowledge: entity-selection tree, deduction/credit reference (dated, IRS-cited), multi-state nexus primer. Disclaimer hook: "educational, not tax advice; cite the form/section." Seam: books/close → accounting-bookkeeping; modeling → finance. **Dependency risk:** tax law is volatile → every figure carries a retrieval date + re-verify rider (the `ai-coding-model-guidance` freshness pattern).
3. **content-marketing-social** — 2 agents (`content-strategist-marketing` [note: `content-strategist` is taken by web-design → must rename], `social-media-manager`). Knowledge: channel-playbook map, editorial-calendar template. Seam: martech/automation → marketing-operations; on-site copy → web-design.
4. **public-relations-comms** — 2 agents (`pr-strategist`, `comms-writer`). Templates: press release, crisis-comms holding statement, messaging house. Seam: paid/owned → marketing-operations.
5. **ar-vr-spatial-engineering** — 2 agents (`xr-architect`, `xr-implementation-engineer`). Knowledge: platform-choice tree (Unity vs Unreal vs native; Quest vs visionOS), comfort/perf-budget reference. Seam: game loop → game-development; 3D math/perf → performance-engineering.
6. **utilities-operations** — 3 agents (ops-lead, outage/DMS, metering/AMI). Knowledge: NERC/PUC compliance map, GIS asset model. Seam: generation → renewable-energy; geospatial → geospatial-engineering.
7. **telecom-operations** — 2–3 agents (network-ops, OSS/BSS, regulatory). Knowledge: BEAD/USF map, provisioning flow. Seam: physical network → network-engineering (candidate #1).
8. **chiropractic-practice** — clone the optometry/PT plugin scaffold; 1–2 agents (practice-ops, clinical-documentation). Seam: revenue cycle → medical-revenue-cycle.
9. **childcare-operations** — 2 agents (center-ops, compliance/licensing). Knowledge: state-licensing + CCDF subsidy map. Seam: payroll/HR → people-operations-hr.
10. **media-streaming-engineering** — 2 agents (streaming-architect, streaming-implementation). Knowledge: codec/protocol map (HLS/DASH/CMAF/LL-HLS), DRM tree. Seam: CDN/infra → cloud plugins; production → film-video-production.

## Prioritization (demand × feasibility)

| Rank | Candidate | Demand | Feasibility | Rationale |
|---|---|---|---|---|
| **1** | **network-engineering** | High | High | Broad, stable, well-documented engineering domain; clean seam story beside cloud/devops/security; low hallucination risk → buildable to full quality in one pass. **→ BUILT this routine.** |
| 2 | tax-advisory | High | Medium | High demand, but tax law is volatile → heavier freshness/disclaimer discipline; needs careful citation. |
| 3 | content-marketing-social | High | High | Common SMB ask; stable craft. Naming collision to resolve (`content-strategist`). |
| 4 | media-streaming-engineering | Medium | High | Stable engineering domain; clear gap. |
| 5 | ar-vr-spatial-engineering | Medium | Medium | Emerging; platform specifics (visionOS) are fast-moving. |
| 6 | public-relations-comms | Medium | High | Stable craft; smaller surface. |
| 7 | chiropractic-practice | Medium | High | Proven single-provider scaffold; lower marginal novelty. |
| 8 | childcare-operations | Medium | Medium | Real demand; licensing varies sharply by state (freshness cost). |
| 9 | utilities-operations | Medium | Medium | Valuable but regulatory-heavy and niche. |
| 10 | telecom-operations | Low-Med | Medium | Narrower audience; depends partly on #1. |

## Progress this routine

- **#1 `network-engineering` — BUILT** end-to-end and included in this PR (agents, skills, knowledge bank, best-practices, templates, advisory hook, marketplace registration).
- **#2–#10 — scoped** above with implementation outlines, dependencies, and naming-collision notes; ready to pick up as follow-up PRs in priority order.

### Blocker / honest scope note

Ten full plugins cannot be built to this repo's quality bar (and pass every CI gate) in a single unattended routine — each is a substantial multi-file build with a citation-grounded knowledge bank. The deliberate choice was **depth over breadth**: ship the highest-priority plugin complete and verified rather than ten thin stubs that would fail the frontmatter/scenario-schema gate. The remaining nine are documented to be immediately actionable.
