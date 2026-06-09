# Ten new-plugin candidates for RavenClaude — research, prioritization, and build status

> **Date:** 2026-06-09 · **Author:** Claude Code (autonomous task) · **Status:** research + initial build
>
> Task: research and identify 10 new plugins not yet in the marketplace, prioritize by user demand and technical feasibility, and build out the highest-priority first. This doc is the research deliverable; the first build ships alongside it.

## Method

The marketplace already carries **98 plugins** (see `.claude-plugin/marketplace.json`). To avoid proposing duplicates I enumerated the existing set and looked for *genuine gaps* — roles and disciplines that (a) a real practitioner is accountable for, (b) don't already have an owning plugin, and (c) fit the marketplace's "specialist team + house opinions + knowledge bank + calculator" pattern. Each candidate below names the **closest existing plugin(s)** and the **seam** that keeps it disjoint, exactly as the house rules require (AGENTS.md §"House rules").

## Coverage map (what already exists, so we don't duplicate)

- **App craft:** backend / frontend / mobile / api / database / auth-identity
- **Platform & ops:** devops-cicd, cloud-native-kubernetes, terraform-iac, observability-sre, platform-engineering-idp, performance-engineering, finops-cloud-cost, qa-test-automation, security-engineering, cybersecurity-grc
- **Cloud:** aws / azure / gcp
- **Data & AI:** data-platform, analytics-engineering, data-streaming, ml-engineering, ai-rag-engineering, data-science-research, applied-statistics, data-governance-privacy, microsoft-fabric, tableau
- **Specialized eng:** blockchain-web3, embedded-iot, game-development, accessibility-engineering, localization-i18n, search-relevance-engineering, api-engineering
- **Product/PM:** product-management, project-management, process-improvement, experimentation-growth-engineering
- **Business verticals:** finance, fintech-payments, wealth-management-ria, insurance (p&c + l&h), mortgage, regulatory-compliance, accounting-bookkeeping, sales-revops, marketing-operations, customer-support-cx, people-operations-hr, procurement-sourcing, supply-chain-planning, legal-ops-clm, legal-small-firm, plus ~25 deep industry verticals (dental, veterinary, pharmacy, hotel, restaurant, automotive-dealership, etc.)

## The 10 candidates (prioritized)

Scoring: **Demand** (how often a real practitioner needs this) × **Feasibility** (how cleanly it grounds in durable knowledge without volatile facts) × **Disjointness** (low overlap with existing plugins). 1–5 each; Priority = sum.

| # | Candidate | Demand | Feas. | Disjoint | Priority | Closest existing → seam |
|---|---|---|---|---|---|---|
| 1 | **engineering-management** | 5 | 5 | 4 | 14 | people-operations-hr (generic HR) → EM owns the *engineering* craft of leading engineers |
| 2 | **ux-research** | 5 | 5 | 4 | 14 | product-management (discovery), web-design (UX *design*) → owns research *methods/ops* |
| 3 | **sales-engineering** | 4 | 5 | 4 | 13 | sales-revops (the funnel) → owns *pre-sales technical* (demos, POCs, security questionnaires) |
| 4 | **developer-relations-devrel** | 4 | 4 | 4 | 12 | marketing-operations, technical-writing-docs → owns advocacy, community, sample apps, CFPs |
| 5 | **engineering-onboarding-enablement** | 4 | 4 | 4 | 12 | people-operations-hr, technical-writing-docs → owns dev onboarding ramp + internal enablement |
| 6 | **quantitative-trading** | 4 | 3 | 4 | 11 | wealth-management-ria, finance → owns strategy research + backtest rigor + execution |
| 7 | **release-management** | 3 | 4 | 3 | 10 | devops-cicd → owns release trains, change mgmt, versioning, rollout/rollback comms |
| 8 | **chaos-engineering-resilience** | 3 | 4 | 3 | 10 | observability-sre → owns fault injection, game days, steady-state hypotheses |
| 9 | **knowledge-management-ops** | 3 | 4 | 3 | 10 | technical-writing-docs → owns org knowledge lifecycle, taxonomy, runbook hygiene |
| 10 | **bioinformatics-genomics** | 3 | 3 | 5 | 11 | clinical-trials, data-science-research → owns NGS pipelines, variant calling, reproducibility |

### Per-candidate brief

**1. engineering-management** — Eng-leadership craft for a team lead / EM / director: structured 1:1s, growth frameworks and performance reviews (calibration, promo packets), hiring loops (structured interviews, scorecards, debrief), team-health/morale signals, and tech-debt vs roadmap trade-offs. *Approach:* 4 agents (lead + people-growth + delivery-execution + technical-health), DORA-done-right knowledge, a calc for span-of-control / on-call load / promo-readiness. *Deps:* none beyond ravenclaude-core. **← built in this PR.**

**2. ux-research** — Research methods & ResearchOps for a UX researcher / PM doing discovery: method selection (generative vs evaluative, qual vs quant), interview-guide and usability-test design, survey design that avoids leading questions, synthesis (affinity mapping, JTBD), and a research repository. *Approach:* 3–4 agents, method-selection decision tree, sample-size/confidence calc. *Deps:* ravenclaude-core; seams to product-management + web-design + applied-statistics.

**3. sales-engineering** — Pre-sales / solutions engineering: discovery (MEDDICC-style technical qualification), demo scripting (demo-to-win, "tell-show-tell"), POC/pilot success criteria, technical RFP + security-questionnaire responses, and value engineering. *Deps:* seams to sales-revops + security-engineering + api-engineering.

**4. developer-relations-devrel** — Developer advocacy: sample-app/quickstart craft, conference talk + CFP authoring, community health metrics, docs feedback loops, and DevRel ROI measurement (the eternal attribution problem). *Deps:* seams to technical-writing-docs + marketing-operations + api-engineering.

**5. engineering-onboarding-enablement** — Ramp engineering: a 30/60/90 onboarding arc for engineers, "good first issue" pipelines, internal-tool docs, golden-path paved roads, and enablement metrics (time-to-first-PR, time-to-first-oncall). *Deps:* seams to platform-engineering-idp + technical-writing-docs + people-operations-hr.

**6. quantitative-trading** — Strategy research and backtest rigor: avoiding lookahead/survivorship/overfit bias, walk-forward validation, position sizing (Kelly, vol targeting), transaction-cost modeling, and execution. *Deps:* seams to finance + wealth-management-ria + applied-statistics. *Risk:* must stay educational/engineering — no investment advice.

**7. release-management** — Release trains, change management (CAB-lite), semver discipline, feature-flag-gated rollout/rollback, and release-notes/comms. *Deps:* overlaps devops-cicd (the *pipeline*) — this owns the *process and comms*.

**8. chaos-engineering-resilience** — Steady-state hypotheses, blast-radius-bounded fault injection, game-day design, and resilience patterns validated by experiment. *Deps:* overlaps observability-sre (the *telemetry*) — this owns the *experiments*.

**9. knowledge-management-ops** — Org knowledge lifecycle: taxonomy/IA for an internal KB, runbook hygiene, doc-rot detection, search-able org memory, and KM metrics. *Deps:* overlaps technical-writing-docs (external/product docs) — this owns *internal* knowledge ops.

**10. bioinformatics-genomics** — NGS pipeline engineering: read alignment, variant calling, Nextflow/Snakemake reproducibility, reference-genome/build hygiene, and FAIR data. *Deps:* most disjoint of the set; seams to data-science-research + clinical-trials. *Risk:* narrower audience, more volatile tooling facts.

## Prioritization rationale

- **#1 engineering-management and #2 ux-research top the list** because they are **domain-neutral** (every software org has them), **high-demand**, and **highly feasible** (durable craft knowledge, no volatile vendor facts that rot). They also have **clean seams** — neither duplicates an existing plugin, both compose with several.
- **#3–#5** (sales-engineering, DevRel, onboarding-enablement) are the next tier: high feasibility, slightly narrower audiences, all domain-neutral.
- **#6 quant-trading and #10 bioinformatics** score on disjointness but carry **subject-matter risk** (advice boundaries / volatile tooling) that demands more careful knowledge-bank grounding.
- **#7–#9** are real but overlap an existing plugin enough that they ship as the *process* layer beside an existing *mechanism* layer — valuable, but lower marginal coverage.

## Build status (this PR)

- **#1 engineering-management — BUILT.** Full plugin to the marketplace quality bar: 4 agents (scenario-schema complete), 5 skills + 5 commands, 4-file knowledge bank (KPI glossary, economics, context, Mermaid decision trees), 8 best-practice rules, 4 templates, a 3-scenario bank, a stdlib calculator (`engineering_management_calc.py`), and 1 advisory hook. Registered in `marketplace.json`; globs already covered by `.repo-layout.json`.
- **#2–#10 — SCOPED, NOT YET BUILT.** Each existing plugin is ~35 files of carefully-grounded content; building all ten to the marketplace's depth bar is a multi-session effort. The honest blocker is **scope-per-quality-bar**, not capability. Each candidate above carries enough detail (agents, knowledge, seams, deps) to scaffold in a follow-up PR. Recommended order is the priority ranking; #2 (ux-research) is the next build.

## Blockers / notes

- **No technical blockers** were hit (git, layout gate, frontmatter gate all green for the #1 build).
- The only constraint is **breadth vs depth**: this marketplace's bar is high enough that ten shallow plugins would fail the frontmatter/scenario gates and dilute quality. One complete, gate-passing plugin plus a fully-scoped research doc is the higher-value deliverable; the remaining nine are ready to build in priority order.
