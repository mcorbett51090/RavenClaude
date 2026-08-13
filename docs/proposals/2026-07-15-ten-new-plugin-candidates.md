# Ten new-plugin candidates for RavenClaude — research, prioritization, and build status (2026-07-15)

> **Date:** 2026-07-15 · **Author:** Claude Code (autonomous scheduled routine) · **Status:** research + initial build
>
> Task: research and identify 10 plugins **not yet implemented**, prioritize by user demand and technical feasibility, and build out the highest-priority first. This doc is the research deliverable; this pass ships **two** full, gate-passing plugins alongside it — `prompt-engineering` and `database-reliability-engineering`.

## Method & prior art

The marketplace already carries **164 plugins** (`.claude-plugin/marketplace.json`). Five prior candidate passes exist, and the backlog they surfaced has largely been **consumed** — `cli-tooling-engineering`, `developer-relations`, `computer-vision-engineering`, `grants-management`, `geospatial-engineering`, and `trust-and-safety` all now ship, alongside the `data-orchestration` / `developer-tooling` / `startup-fundraising` built on 2026-06-21. So this pass surfaces a **net-new slate** — all 10 candidates below are absent from every prior proposal and confirmed unbuilt (`plugins/<name>/` does not exist).

For each candidate I name the **closest existing plugin(s)** and the **seam** that keeps it disjoint, per AGENTS.md § "House rules" (no overlap, no re-skin).

## Coverage gaps this pass targets

- **AI / LLM app craft:** `ai-rag-engineering` (retrieval), `llm-evaluation-engineering` (measurement), `ai-coding-model-guidance` (model choice), `ai-red-teaming` (attack) all ship — **gap: no owner of the _prompt & context_ itself** (pattern selection, context-window engineering, the output contract, prompt eval/regression, prompt-injection defense at the prompt layer). → **prompt-engineering (built)**.
- **Data infrastructure:** `database-engineering` owns schema/query *design* — **gap: no owner of the production database as a _reliability_ surface** (HA/failover, backup/PITR, zero-downtime migrations, DB on-call), distinct from `observability-sre` (service-level SRE). → **database-reliability-engineering (built)**.
- **Verticals & operations:** broad coverage exists, but several high-demand lanes remain unowned — healthcare-at-home, warehouse/WMS operations, retail banking, social-media management, tax practice, HOA management, collections, podcast production (see the table).

## The 10 candidates (prioritized)

Scoring: **Demand** (how often a real practitioner needs it) × **Feasibility** (durable craft, not volatile facts that rot) × **Disjoint** (low overlap with an existing plugin). 1–5 each; Priority = sum.

| #  | Candidate | Demand | Feas. | Disjoint | Priority | Closest existing → seam |
| -- | --------- | ------ | ----- | -------- | -------- | ----------------------- |
| 1 | **prompt-engineering** ✅ *(built here)* | 5 | 4 | 5 | 14 | ai-rag (retrieval) / llm-evaluation (measure) / ai-coding-model-guidance (which model) / ai-red-teaming (attack) → owns **the prompt & context**: pattern selection, context-window engineering, output contract, prompt eval/regression, prompt-injection defense |
| 2 | **database-reliability-engineering** ✅ *(built here)* | 5 | 5 | 4 | 14 | database-engineering (schema/query design) / observability-sre (service SRE) → owns the **production DB as a reliability surface**: HA/failover, backup/PITR, zero-downtime migrations, DB on-call |
| 3 | **home-health-agency-operations** | 4 | 4 | 4 | 12 | senior-care-operations (residential) / hospice-referral-sales (referral) → skilled home-health agency ops: OASIS, PDGM episode economics, visit scheduling, survey readiness (NOT clinical/legal advice) |
| 4 | **warehouse-wms-operations** | 4 | 4 | 4 | 12 | fleet-logistics (move) / supply-chain-planning (plan) → the four walls: slotting, pick/pack/ship, inventory accuracy/cycle-counting, labor & dock/yard, WMS choice |
| 5 | **social-media-management** | 4 | 3 | 4 | 11 | marketing-operations / creator-economy-operations → agency/brand social ops: content calendar, platform mix, community management, paid+organic, social analytics (platform facts volatile → dated) |
| 6 | **retail-banking-operations** | 3 | 4 | 4 | 11 | fintech-payments-engineering (rails) / treasury-management (corp) / regulatory-compliance (AML) → branch & deposit operations: account lifecycle, BSA/branch ops, fraud/dispute ops (NOT legal advice) |
| 7 | **tax-preparation-practice** | 4 | 3 | 4 | 11 | accounting-bookkeeping (books) / finance (FP&A) → tax-prep firm ops: engagement/workflow, season capacity, review/e-file QC, IRS-notice handling (NOT tax advice; code is volatile → dated) |
| 8 | **hoa-community-association-management** | 3 | 4 | 4 | 11 | property-management (rental) → association management: board governance, reserve studies, assessments/collections, covenant enforcement, meetings (NOT legal advice) |
| 9 | **podcast-production** | 3 | 4 | 4 | 11 | creator-economy-operations (biz) / film-video-production (video) / streaming-media-engineering (delivery) → audio show production: workflow, recording/edit, RSS/distribution, monetization ops |
| 10 | **debt-collections-operations** | 3 | 3 | 4 | 10 | medical-revenue-cycle (medical AR) / fintech-payments → collections agency ops: strategy/segmentation, contact cadence, FDCPA-aware workflow, payment plans (NOT legal advice; reg volatile → dated) |

### Per-candidate brief — purpose, approach, dependencies

**1. prompt-engineering** *(BUILT)* — The prompt/context layer no AI plugin owned. *Purpose:* task→prompt decomposition, prompting-pattern selection (zero/few-shot, CoT, decomposition, role, self-consistency), context-window engineering (what to include/retrieve/compress, lost-in-the-middle ordering, token budget), the output-format contract (JSON mode / tool-calling / grammar + validate/repair), prompt eval & regression with a CI gate, and prompt-injection/jailbreak defense at the prompt layer. *Approach:* 3 agents (prompt-architect, prompt-implementation-engineer, prompt-reliability-engineer), 4 skills, a 4-tree Mermaid knowledge doc + a dated 2026 reference, 5 best-practices, 2 templates. *Deps:* ravenclaude-core; seams to ai-coding-model-guidance/claude-api (model), ai-rag-engineering (retrieval), llm-evaluation-engineering (eval at scale), ai-red-teaming (attack), backend/claude-app-engineering (the app).

**2. database-reliability-engineering** *(BUILT)* — The production-DB reliability layer distinct from schema/query design. *Purpose:* HA topology & failover from RPO/RTO, backup/PITR + restore verification, disaster recovery, capacity planning, connection pooling; zero-downtime expand-contract migrations, backfills, replication management & failover drills, upgrades; DB on-call (triage of lock contention / replication lag / connection storms / runaway queries / disk-full / failover), DB SLOs, blameless postmortems. *Approach:* 3 agents (dbre-architect, database-operations-engineer, database-incident-responder), 4 skills, a 4-tree Mermaid knowledge doc + a dated 2026 reference, 5 best-practices, 2 templates. *Deps:* ravenclaude-core; seams to database-engineering (schema), observability-sre (service SLO), terraform-iac/cloud (provisioning), data-orchestration (pipelines), security-engineering/auth-identity (access), incident-response-dfir (DB security incident).

**3. home-health-agency-operations** *(next build)* — Skilled home-health agency operations. *Purpose:* OASIS assessment workflow, PDGM episode economics (case-mix, LUPA thresholds, comorbidity), visit scheduling & clinician utilization, referral-to-admission, survey/CoP readiness. *Approach:* 3 agents (agency-operations-lead, clinical-intake-scheduler, home-health-compliance-advisor), 4 skills, 4 Mermaid trees + dated reference, 5 best-practices, 2 templates. *Deps:* ravenclaude-core; seams to senior-care-operations, hospice-referral-sales, medical-revenue-cycle. **ADVISORY only — not clinical/legal advice; no PHI; CMS/PDGM/CoP specifics jurisdictional + dated.**

**4. warehouse-wms-operations** *(next build)* — Distribution-center "four walls" operations. *Purpose:* slotting & storage strategy, receive/putaway/pick/pack/ship flow, inventory accuracy & cycle counting, labor management & engineered standards, dock/yard, WMS selection. *Approach:* 3 agents (warehouse-operations-lead, inventory-accuracy-manager, fulfillment-flow-engineer), 4 skills, 4 Mermaid trees + dated reference, 5 best-practices, 2 templates. *Deps:* ravenclaude-core; seams to fleet-logistics (transport), supply-chain-planning (plan), retail-store-operations, manufacturing-operations.

**5. social-media-management** — Agency/brand social operations (distinct from `marketing-operations` demand-gen and `creator-economy-operations` solo-creator P&L). *Purpose:* content calendar & platform mix, community management, organic+paid coordination, social analytics & reporting, crisis/escalation. *Risk:* platform facts volatile → dated. *Deps:* marketing-operations, creator-economy-operations, brand-identity-studio.

**6. retail-banking-operations** — Branch & deposit operations (distinct from `fintech-payments-engineering` rails, `treasury-management` corporate, `regulatory-compliance` AML program). *Purpose:* account lifecycle, deposit/branch operations, fraud & dispute (Reg E/Z) ops, BSA front-line. *Deps:* fintech-payments-engineering, treasury-management, regulatory-compliance. **NOT legal advice.**

**7. tax-preparation-practice** — Tax-prep firm operations (distinct from `accounting-bookkeeping` books and `finance` FP&A). *Purpose:* engagement & document workflow, season capacity planning, preparer/review/e-file QC, IRS-notice handling, pricing. *Risk:* tax code volatile + jurisdictional → dated. *Deps:* accounting-bookkeeping, finance. **NOT tax advice.**

**8. hoa-community-association-management** — Community-association management (distinct from `property-management` rental ops). *Purpose:* board governance & meetings, reserve studies & funding, assessment billing & collections, covenant enforcement, vendor management. *Deps:* property-management, accounting-bookkeeping. **NOT legal advice.**

**9. podcast-production** — Audio-show production (distinct from `creator-economy-operations` biz, `film-video-production` video, `streaming-media-engineering` delivery infra). *Purpose:* show/episode workflow, recording & edit pipeline, RSS/distribution, guest ops, monetization. *Deps:* creator-economy-operations, audio-dsp-engineering, film-video-production.

**10. debt-collections-operations** — Collections-agency operations (distinct from `medical-revenue-cycle` medical AR). *Purpose:* account strategy & segmentation, contact cadence, FDCPA-aware workflow, payment plans & settlements, compliance QA. *Risk:* FDCPA/Reg F volatile → dated. *Deps:* medical-revenue-cycle, fintech-payments-engineering, regulatory-compliance. **NOT legal advice.**

## Prioritization rationale

- **Built this pass (top tier, 14/14).** Both are **technical plugins for this marketplace's core developer audience**, both fill a clean structural gap, and both are durable-craft (volatile facts isolated to a dated reference doc):
  - **prompt-engineering (14)** — the single highest-demand gap for a *Claude Code* marketplace: every team building on an LLM writes prompts, yet the four neighboring AI plugins owned model-choice, retrieval, eval-at-scale, and attack — not the prompt itself. Pattern selection, context budgeting, output contracts, and prompt-layer injection defense are evergreen craft.
  - **database-reliability-engineering (14)** — universal demand (any team with a production database) and the most durable craft on the slate (HA, backups, expand-contract migrations, incident triage are decade-stable). The clean seam to `database-engineering` (design) vs this (reliability) mirrors the real DBA/DBRE split.
- **home-health-agency-operations (12)** and **warehouse-wms-operations (12)** are the recommended **next builds** — high-demand vertical/ops lanes, durable operational craft with volatile specifics safely dateable, and clean seams.
- The remaining candidates (5–10, all 10–11) are real and valuable but each carries either a narrower audience or more volatile/jurisdictional facts (platform algorithms, tax code, FDCPA), so they slot below and ship in priority order.

## Build status (this PR)

- **#1 prompt-engineering — BUILT.** 3 agents (full scenario-authoring frontmatter, each description ≤300 chars, `prompt-implementation-engineer` named to avoid the ravenclaude-core `prompt-engineer` collision), 4 skills, a 4-tree Mermaid knowledge doc + a dated 2026 reference, 5 best-practices, 2 templates, CLAUDE.md + README + CHANGELOG. Registered in `marketplace.json` and the `docs/architecture.md` roster.
- **#2 database-reliability-engineering — BUILT.** 3 agents (full frontmatter, descriptions ≤300 chars, names unique), 4 skills, a 4-tree Mermaid knowledge doc + a dated 2026 reference, 5 best-practices, 2 templates, CLAUDE.md + README + CHANGELOG. Registered in catalog + roster.
- **#3–#10 — SCOPED, NOT YET BUILT.** Each existing plugin is ~20–45 files of cited, CI-gated content (agents must carry the full scenario-authoring frontmatter; descriptions are length-capped; agent names must be globally unique; relative links must resolve). Each candidate above carries enough detail (agents, skills, knowledge, seams, deps, disclaimers) to scaffold in a follow-on PR, in the priority order above.

## Blockers / notes

- **No hard blockers.** One expected friction: the initial `prompt-engineer` agent name **collided** with ravenclaude-core's existing `prompt-engineer` (the frontmatter gate enforces global agent-name uniqueness). Resolved by renaming to `prompt-implementation-engineer` and updating all in-plugin references — a good example of why the gate exists.
- The strict gates (frontmatter/scenario schema, ≤300-char agent descriptions, global agent-name uniqueness, marketplace-claims structural check + accurate agent/skill counts, layout allow-list, relative-link resolution, prettier, ruff, version-pin parity) all run locally and were validated before pushing.
- **The real constraint remains breadth vs depth.** Ten shallow plugins would fail the frontmatter/scenario gates and dilute the marketplace. Two complete, gate-passing plugins plus this fully-scoped, prioritized roadmap is the higher-value deliverable — the same conclusion every prior pass reached, and the pattern this repo endorses. The remaining eight are ready to build in priority order.
