# Ten new plugin candidates for RavenClaude — research, prioritization, and build plan

**Date:** 2026-06-16
**Author:** Claude Code (scheduled routine)
**Status:** Proposal + first build (developer-relations) landed in the accompanying PR

## Why this doc

The marketplace ships ~101 plugins across the software-delivery chain, the cloud trio,
app craft, data & AI, the Microsoft stack, and ~50 business/clinical verticals. This
doc surveys the remaining **gaps** — common use cases, integrations, and disciplines
with no dedicated plugin — proposes ten candidates, and prioritizes them by **user
demand × technical feasibility × gap-cleanliness × fit with the marketplace's
software/business center of gravity.**

Gap-confirmation method: every candidate name below was checked against `plugins/`
(directory absent) and grep'd against existing plugin content for overlapping coverage
(2026-06-16). Where an adjacent plugin exists, the candidate's distinct scope and the
seam to the neighbor are called out.

## The ten candidates

| # | Plugin | Purpose & value | Implementation approach | Dependencies / seams |
|---|--------|-----------------|-------------------------|----------------------|
| 1 | **developer-relations** | DevRel program craft: developer advocacy, the developer funnel (awareness → activation → retention), quickstart/sample ergonomics, community health, and DevRel metrics that aren't vanity. High demand, software-adjacent, clean gap. | 4 agents (lead, advocate, docs-and-samples, community-manager), 5 skills (strategy, quickstart authoring, content pipeline, community health, metrics), a developer-funnel decision-tree knowledge doc, templates, advisory anti-pattern hook. | `ravenclaude-core`; seams to `technical-writing-docs` (reference docs), `product-management` (feedback loop), `marketing-operations` (campaigns). |
| 2 | **open-source-stewardship** | Maintainer workflows: issue/PR triage, semver + changelog + release discipline, RFC process, community health files (CONTRIBUTING/COC/SECURITY), license compliance, funding/governance. Clean gap; this repo *is* a marketplace, so dogfoodable. | 3–4 agents (maintainer-lead, triage-and-release-engineer, community-governance, license-compliance), skills for triage, release cutting, RFC authoring. | `ravenclaude-core`, `technical-writing-docs`, `devops-cicd`. |
| 3 | **technical-seo-engineering** | The *engineering* side of SEO: Core Web Vitals, crawl budget, render strategy (CSR/SSR/ISR), structured data (schema.org/JSON-LD), sitemaps/robots, i18n SEO, log-file analysis. Distinct from `web-design` (visual) and `marketing-operations` (campaigns). | 3 agents (seo-engineer, structured-data-specialist, site-performance-analyst), skills for CWV audit, schema authoring, crawl/render diagnosis. | `frontend-engineering`, `web-design`, `marketing-operations`, `performance-engineering`. |
| 4 | **itsm-service-management** | ITIL-aligned IT service management: incident/problem/change/request workflows, CMDB, service catalog, SLAs/OLAs, major-incident command. Distinct from `observability-sre` (telemetry/reliability engineering) — this is the enterprise-IT process layer. | 4 agents (service-manager, incident-commander, change-and-problem-manager, service-catalog-owner), skills for major-incident comms, change-risk assessment, post-incident review. | `observability-sre`, `devops-cicd`, `people-operations-hr`. |
| 5 | **geospatial-gis-engineering** | Spatial data engineering: PostGIS, vector/raster, coordinate reference systems, tiling/serving (vector tiles), routing, remote sensing, geocoding. Touched by `precision-agriculture` but no general GIS plugin. | 3 agents (gis-engineer, spatial-data-pipeline-engineer, remote-sensing-analyst), skills for CRS hygiene, tile pipeline, spatial query tuning. | `data-platform`, `backend-engineering`, `data-science-research`. |
| 6 | **email-deliverability-engineering** | Getting mail to the inbox: SPF/DKIM/DMARC/BIMI, sending reputation + IP/domain warmup, bounce/complaint handling, ESP integration, transactional-vs-marketing separation, seed testing. Niche but high-pain gap. | 3 agents (deliverability-engineer, email-auth-specialist, sending-reputation-analyst), skills for DMARC rollout, warmup planning, bounce-loop handling. | `backend-engineering`, `marketing-operations`, `security-engineering`. |
| 7 | **conversational-ai-voice** | Voice agents & IVR: telephony (SIP/WebRTC), ASR/TTS, turn-taking/barge-in/endpointing, latency budgets, dialog state, escalation-to-human. Distinct from `ai-rag-engineering` (text retrieval) and `claude-app-engineering` (general LLM apps). | 3 agents (voice-agent-architect, telephony-integration-engineer, dialog-and-prompt-engineer), skills for latency budgeting, turn-taking design, eval harness. | `ai-rag-engineering`, `claude-app-engineering`, `customer-support-cx-operations`. |
| 8 | **bioinformatics-genomics** | NGS pipelines (alignment, variant calling), Nextflow/Snakemake, BioPython/Bioconductor, reproducible research, HPC/cloud batch, FAIR data. Deep research gap. Higher build risk — benefits from SME review. | 3 agents (bioinformatics-pipeline-engineer, computational-biologist, reproducible-research-steward), skills for pipeline scaffolding, variant-QC, environment pinning. | `data-science-research`, `data-platform`, `aws-cloud`/`gcp-cloud`. |
| 9 | **robotics-engineering** | ROS2, motion planning, perception, real-time control, sim (Gazebo/Isaac), safety. Adjacent to `embedded-iot-engineering`. Deep specialist — SME review recommended. | 3 agents (robotics-systems-engineer, perception-and-planning-engineer, controls-and-safety-engineer), skills for ROS2 node design, sim-to-real, safety-case authoring. | `embedded-iot-engineering`, `ml-engineering`. |
| 10 | **higher-education-administration** | University/college operations: enrollment management, financial aid, registrar/SIS, accreditation, retention. `k12-school-administration` + `edtech-partner-success` exist; higher-ed is distinct (aid, accreditation, credit-hour). | 3–4 agents (registrar, financial-aid-officer, enrollment-manager, accreditation-coordinator), skills for aid packaging, accreditation self-study, retention analysis. | `k12-school-administration`, `edtech-partner-success`, `people-operations-hr`. |

## Prioritization rationale

Scoring on four axes (H/M/L) and grouping into build tiers:

| Plugin | Demand | Feasibility | Gap-clean | Fit | Tier |
|--------|--------|-------------|-----------|-----|------|
| developer-relations | H | H | H | H | **1 — build now** |
| open-source-stewardship | H | H | H | H | **1** |
| technical-seo-engineering | H | H | M | H | **1** |
| itsm-service-management | M | H | M | M | 2 |
| geospatial-gis-engineering | M | M | H | M | 2 |
| email-deliverability-engineering | M | H | H | M | 2 |
| conversational-ai-voice | H | M | M | H | 2 |
| bioinformatics-genomics | M | L | H | L | 3 — needs SME |
| robotics-engineering | M | L | H | L | 3 — needs SME |
| higher-education-administration | M | M | M | M | 3 |

- **Tier 1** is software/DevRel-adjacent: high demand, content I can author authoritatively
  without external SME validation, and clean gaps. These are the right first builds.
- **Tier 2** is feasible but either narrower in demand or with an adjacent plugin whose
  seam must be drawn carefully (ITSM↔SRE, voice↔RAG).
- **Tier 3** are deep specialist domains (genomics, robotics) where shipping authoritative
  best-practices responsibly needs subject-matter-expert review before merge — flagged so
  they are *planned*, not rushed.

## What this PR builds

Per the routine's instruction to "build the highest-priority plugins first," this PR
delivers **#1, `developer-relations`, complete** — manifest, team constitution (CLAUDE.md),
README, 4 agents (full scenario-authoring frontmatter), 5 skills, a developer-funnel
decision-tree knowledge doc, best-practices, templates, two slash commands, and an advisory
anti-pattern hook — wired into `marketplace.json` and the `docs/architecture.md` roster, and
verified against the repo's CI gates (frontmatter strict-YAML + scenario schema + 300-char
cap, layout allow-list, marketplace claims structural check, prettier, markdown links,
version-pin parity).

**Scope honesty:** ten *complete* plugins at this repo's quality bar (the `finance` plugin
is ~91 files) is not achievable in a single routine run without dropping below the bar, so
the remaining nine are specified above as a sequenced roadmap (Tier 1 next: `open-source-stewardship`,
`technical-seo-engineering`) rather than shipped as thin stubs. Each is a self-contained
follow-up PR.
