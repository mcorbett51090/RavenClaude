# Ten new-plugin candidates for RavenClaude — research, prioritization, and initial buildout

**Date:** 2026-06-14
**Author:** Claude (agentic session)
**Status:** proposal + initial build (2 of 10 built this session)

## Method

The marketplace already ships ~100 plugins. I enumerated the current roster
(`.claude-plugin/marketplace.json`) and looked for **genuine gaps** — roles and
domains with real, recurring demand that are *not* already covered and that fill
a clean seam between existing plugins (so they don't cannibalize an existing
plugin's scope). Each candidate below names the **existing plugins it is NOT**,
because the house rule is that a new plugin earns its place only when it is
distinct from everything already shipped.

Demand and feasibility are scored 1–5. **Feasibility** here means "buildable to
the marketplace quality bar with no external dependency beyond `ravenclaude-core`"
— every candidate is advisory (it produces plans/artifacts, it doesn't operate a
live external system), which is the cheapest, safest plugin shape.

## The 10 candidates

| # | Plugin | Purpose & value | Distinct from | Demand | Feasibility |
|---|--------|-----------------|---------------|:---:|:---:|
| 1 | **technical-program-management** | Cross-team program delivery: program charter, dependency mapping, RAID/critical-path risk, launch-readiness & go/no-go, exec status comms. | `project-management` (single project/plan), `engineering-management` (people/teams) | 5 | 5 |
| 2 | **developer-relations** | Developer advocacy & DX: getting-started/time-to-first-success audits, sample-app & SDK quickstart design, content strategy, community health, DX metrics, product-feedback loop. | `technical-writing-docs` (reference docs), `marketing-operations` (demand gen), `product-management` (what to build) | 5 | 5 |
| 3 | **ux-research** | Research ops: study design, interview & usability-test guides, participant recruiting, synthesis/affinity mapping, research-repository hygiene, evidence→decision traceability. | `product-management` (prioritization), `web-design` (visual/IA), `accessibility-engineering` (WCAG) | 4 | 5 |
| 4 | **technical-seo-content** | Technical SEO + content engineering: crawlability/indexation, Core Web Vitals-for-SEO, structured data (schema.org), internal-linking, SERP/AEO-GEO content strategy. | `search-relevance-engineering` (internal site search/ranking), `marketing-operations` (campaigns), `web-design` (build) | 4 | 5 |
| 5 | **open-source-stewardship** | OSS maintainership: issue/PR triage, contributor onboarding & CLA/DCO, semver release management, governance & licensing, coordinated security disclosure (CVE), community health files. | `devops-cicd` (pipelines), `engineering-management` (internal teams), `cybersecurity-grc` (org compliance) | 4 | 5 |
| 6 | **llmops-evaluation** | LLM eval & prompt-ops: offline/online eval-set design, LLM-as-judge rubrics, regression suites, prompt versioning/A-B, red-teaming, drift & cost/latency monitoring. | `ai-rag-engineering` (retrieval systems), `ml-engineering` (classical ML lifecycle), `ai-coding-model-guidance` (which coding model to use) | 5 | 4 |
| 7 | **technical-due-diligence** | Tech DD for M&A / VC: code-quality & architecture assessment, security & license posture, scalability & key-person risk, a weighted scorecard + red-flag memo. | `finance` (financial DD/valuation), `security-engineering` (build-time security), `architecture-aec` (buildings, unrelated) | 3 | 4 |
| 8 | **robotics-engineering** | Robotics: ROS 2 architecture, motion planning & control, perception/sensor fusion, safety (ISO 10218 / functional safety), sim-to-real, fleet ops. | `embedded-iot-engineering` (MCU firmware/connectivity), `ml-engineering` (model training) | 3 | 4 |
| 9 | **bioinformatics** | Computational biology: NGS pipelines (Nextflow/Snakemake), variant calling & QC, reproducibility/containers, reference-data provenance, FAIR data. | `clinical-trials` (trial ops/biostatistics), `data-science-research` (general DS), `pharmacy-operations` (dispensing) | 3 | 4 |
| 10 | **creator-economy-production** | Content-business ops: multi-channel content calendar, podcast/YouTube/newsletter production pipelines, audience funnel & monetization, sponsorship & rights. | `film-video-production` (crewed shoots/post), `marketing-operations` (brand demand gen) | 3 | 4 |

## Implementation approach (shared shape)

Every candidate follows the marketplace's proven advisory-plugin anatomy, so the
implementation approach is the same skeleton, differing only in content:

- `.claude-plugin/plugin.json` — name, version `0.1.0`, ≤1024-char description,
  `keywords`, `requires: ravenclaude-core@>=0.7.0`.
- `CLAUDE.md` (team constitution) + `README.md` + `CHANGELOG.md`.
- `agents/` — 3 specialist agents, each with the full scenario-authoring schema
  (`audience` / `works_with` / `scenarios` / `quickstart`) and a ≤300-char
  description (the two gated frontmatter contracts).
- `skills/<name>/SKILL.md` — the repeatable procedures.
- `knowledge/` — a decision-tree doc (Mermaid) + a domain playbook.
- `best-practices/` (with `README.md`) — the opinionated house rules.
- `templates/` — the artifacts the agents fill in.
- `commands/` — slash-command entry points.
- `hooks/` — one advisory anti-pattern hook (`bash -euo pipefail`, executable) +
  `hooks.json` wired with `${CLAUDE_PLUGIN_ROOT}`.
- `scenarios/` — worked end-to-end examples.

**Dependencies:** all 10 are advisory and depend only on `ravenclaude-core`
(for the dispatch playbook, Capability Grounding, decision-review tribunal). None
bundle an MCP server or require external credentials, which keeps feasibility high
and avoids the `x-mcpAttribution` / NOTICE.md gate.

## Prioritization rationale

Ranked by `demand × feasibility`, then by **seam cleanliness** (how unambiguously
the plugin avoids overlapping an existing one — overlap is the main risk in a
100-plugin marketplace) and **breadth of audience**:

1. **technical-program-management** (25) — TPM is one of the most common senior IC
   roles in tech; the seam vs `project-management`/`engineering-management` is
   crisp (program-of-projects + cross-team dependencies, not a single plan and not
   people management). Pure advisory. **→ built this session.**
2. **developer-relations** (25) — universally demanded by any company with an API/SDK;
   the "fix the product before writing around it" feedback loop is a distinctive,
   defensible angle vs docs/marketing. Pure advisory. **→ built this session.**
3. **ux-research** (20) — high demand, very clean seam, but slightly narrower than
   1–2; next in the queue.
4. **technical-seo-content** (20) — strong demand; the AEO/GEO angle is timely.
5. **open-source-stewardship** (20) — high value for any eng org shipping OSS.
6. **llmops-evaluation** (20) — hottest topic and most on-brand for an AI shop, but
   scored one lower on feasibility/seam because it borders three existing AI plugins
   and needs careful boundary work to avoid cannibalizing them — worth doing, worth
   doing *carefully*.
7–10. **technical-due-diligence, robotics-engineering, bioinformatics,
   creator-economy-production** — solid, distinct, but narrower audiences; build
   after the broad-demand tier.

## What was built this session

The two highest-priority candidates were built to the full marketplace quality
bar (agents with gated frontmatter, skills, knowledge decision-trees, best-
practices, templates, commands, an advisory hook, and a worked scenario):

- ✅ `plugins/technical-program-management/`
- ✅ `plugins/developer-relations/`

Both are registered in `.claude-plugin/marketplace.json` and the
`docs/architecture.md` Status table, and pass the local gate suite
(`scripts/check-frontmatter.py`, `scripts/check-md-links.py`,
`python3 -m json.tool`, `bash -n`, prettier on the JSON).

## Blockers / honest scope note

Building all 10 plugins to this marketplace's depth (each ~20+ richly-authored
files) is more than one session can do *well*; the house ethos is explicitly
quality over quantity ("don't ship a blank card"). So this session delivers the
**full research + prioritization for all 10** and a **complete, gate-passing build
of the top 2**, with candidates 3–10 fully scoped above and ready to pick up in
priority order. That is a deliberate quality choice, not a tooling blocker — no
gate, credential, or capability prevented building more; the constraint is author
time per high-quality plugin.
