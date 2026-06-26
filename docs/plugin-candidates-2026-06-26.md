# Plugin candidates — 10 gaps in the RavenClaude marketplace (2026-06-26)

> Research write-up for the scheduled "identify 10 new plugins" routine. Method:
> enumerate the ~119 shipped plugins (`ls plugins/`, `marketplace.json`), map them
> to the disciplines they cover, then look for high-demand professional lanes with
> **no current owner and a clean seam** to the existing roster. Each candidate is
> scored on **Demand** (how often a consumer would reach for it) and **Feasibility**
> (how cleanly it fits the repo's decision-tree + agent pattern), then ranked.

## Method & scope check

The marketplace already covers the software-delivery chain, the three clouds, the
app-craft layer (backend/frontend/mobile/api/database/auth), data & AI, the
Microsoft stack, ~40 business/industry verticals, and most horizontal business
functions (finance, PM, HR, procurement, marketing-ops, sales-revops). So genuine
gaps are now **narrow horizontal functions** and **a few engineering sub-domains**,
not whole clusters. Each candidate below was checked against `ls plugins/` to
confirm no existing owner (e.g. `grep -iE 'pric|monet' plugins/` → none).

Overlap is called out explicitly where a candidate is *adjacent* to an existing
plugin — the test for a real gap is whether the new lane owns a question no current
agent answers (e.g. product-management owns *what to build*; nobody owns *what to
charge*).

## The 10 candidates

| # | Candidate | What it owns (the unowned question) | Demand | Feasibility | Closest existing (seam) |
|---|---|---|---|---|---|
| 1 | **pricing-monetization** | "What do we charge, and how do we package it?" — pricing model, price metric, packaging/tiers, willingness-to-pay, discount governance, SaaS monetization metrics | High | High | finance, product-management, sales-revops |
| 2 | **ux-research** | "Are we building the right thing, and how do we know?" — research-method selection, interviews, usability testing, survey design, synthesis, research ops/repository | High | High | product-management, web-design |
| 3 | **chief-of-staff-operations** | "How does the leader's office actually run?" — OKR/goal cadence, exec/board prep, cross-functional program orchestration, decision memos, operating rhythm | High | High | project-management, engineering-management |
| 4 | **corporate-tax-advisory** | "What's the tax treatment / exposure here?" — entity structure, tax provision (ASC 740), nexus & SALT, R&D credit, transfer-pricing literacy (advisory, not filing) | High | Medium | finance, accounting-bookkeeping, regulatory-compliance |
| 5 | **partnerships-channel-management** | "How do we grow through partners?" — partner-program design, channel/alliance/ISV motions, co-sell, deal registration, partner enablement & QBRs | Med-High | High | sales-revops, sales-engineering, developer-relations |
| 6 | **video-streaming-engineering** | "How do we deliver video at scale?" — codec selection (H.264/HEVC/AV1), packaging (HLS/LL-HLS/DASH/CMAF), WebRTC vs HTTP-streaming, DRM, ABR ladder, CDN/origin | Medium | High | backend-engineering, frontend-engineering, cloud plugins |
| 7 | **social-media-content-operations** | "How do we run organic social as a system?" — channel strategy, content calendar/repurposing, community management, creator/UGC ops, organic analytics | High | High | marketing-operations, developer-relations |
| 8 | **knowledge-management** | "How does the org find what it already knows?" — taxonomy/IA for internal knowledge, wiki/KB governance, findability, knowledge ops & decay, KCS | Medium | High | technical-writing-docs, search-relevance-engineering |
| 9 | **research-grants-administration** | "How do we win and steward sponsored funding?" — pre-award proposal/budget, post-award compliance (Uniform Guidance 2 CFR 200), effort reporting, F&A/indirect | Medium | Medium | nonprofit-fundraising, public-sector-govtech, clinical-trials |
| 10 | **networking-engineering** | "How is the network designed and secured?" — routing/switching, DNS, load balancing, TLS/PKI, zero-trust/segmentation, SD-WAN, observability of the wire | Medium | High | aws/azure/gcp-cloud (cloud-net only), security-engineering |

## Per-candidate detail

### 1. pricing-monetization  *(BUILD FIRST)*
- **Purpose/value:** the discipline of *what to charge and how to package it* — a
  recognized function (pricing strategy / monetization) that no current plugin owns.
  product-management owns *what to build*, sales-revops owns *how to sell & comp*,
  finance owns *the model* — none owns the price metric, the packaging, or the
  willingness-to-pay study.
- **Approach:** 2 agents (`pricing-strategist`, `monetization-analyst`); knowledge
  bank with a **pricing-model-selection decision tree** (subscription / usage /
  seat / tiered / freemium / hybrid), a **value-metric selection** tree, a 2026
  monetization-metrics reference (ARPA, NRR, expansion, discount leakage, the
  "rule of 40" caveat), and a WTP-method reference (Van Westendorp, conjoint,
  Gabor-Granger). Best-practices, packaging + price-change templates, scenarios.
- **Dependencies:** `ravenclaude-core@>=0.7.0`. Seams: model mechanics → finance;
  what-to-build → product-management; quota/comp → sales-revops; price-test stats →
  applied-statistics.
- **Why #1:** highest Demand × Feasibility, zero overlap, well-established public
  frameworks (no proprietary method), maps cleanly to the repo's decision-tree style.

### 2. ux-research
- **Purpose/value:** owns research-method selection and rigor. product-management's
  discovery-lead *uses* research; nobody owns the craft (recruiting, interview
  guides, usability protocols, survey validity, synthesis, a research repository).
- **Approach:** 2 agents (`ux-research-lead`, `research-ops-analyst`); a
  method-selection decision tree (generative vs evaluative, qual vs quant, moderated
  vs unmoderated), survey-validity + sample-size guidance (seam to applied-statistics),
  synthesis/affinity templates, ResearchOps repository pattern.
- **Dependencies:** `ravenclaude-core`. Seams → product-management (discovery),
  web-design (usability of the artifact), applied-statistics (survey stats).

### 3. chief-of-staff-operations
- **Purpose/value:** the operating system of a leader's office — OKR cadence, board
  & exec-staff prep, cross-functional program orchestration, decision memos, the
  weekly/monthly/quarterly operating rhythm. Distinct from project-management
  (single-project) and engineering-management (one team's people).
- **Approach:** 2 agents (`chief-of-staff`, `operating-cadence-analyst`); knowledge:
  OKR-vs-KPI tree, operating-rhythm reference, decision-memo + board-pack templates.
- **Dependencies:** `ravenclaude-core`. Seams → project-management, product-management,
  engineering-management, finance (board pack numbers).

### 4. corporate-tax-advisory
- **Purpose/value:** entity-level tax literacy — structure, the ASC 740 provision,
  nexus/SALT, R&D credit, sales-tax economic nexus, transfer-pricing basics. Advisory
  and educational, **not** return preparation or legal/tax advice.
- **Approach:** 2–3 agents; jurisdiction-aware with retrieval-dated, verify-at-use
  riders (mirrors `regulatory-compliance` discipline). Heavy on disclaimers.
- **Dependencies:** `ravenclaude-core`. Seams → finance (provision mechanics),
  accounting-bookkeeping (the books), regulatory-compliance (filing regimes).
- **Feasibility note (Medium):** jurisdiction/volatility raises the freshness +
  disclaimer bar; must follow the dated-citation pattern strictly.

### 5. partnerships-channel-management
- **Purpose/value:** revenue through partners — program design (referral / reseller /
  ISV / SI / co-sell), deal registration, partner tiers, enablement, partner QBRs.
- **Approach:** 2 agents; partner-motion-selection tree, program-design + co-sell
  templates, partner-health scoring (seam to customer-success-analytics).
- **Dependencies:** `ravenclaude-core`. Seams → sales-revops, sales-engineering,
  developer-relations (for dev/ISV ecosystems).

### 6. video-streaming-engineering
- **Purpose/value:** the media-delivery engineering lane — codec/protocol/DRM/ABR/CDN
  decisions for live and VOD. film-video-production owns *making* video (ops); nobody
  owns *delivering* it as software.
- **Approach:** 2 agents (`streaming-architect`, `streaming-implementation-engineer`);
  decision trees for codec, protocol (HLS / LL-HLS / DASH / WebRTC), and DRM; a 2026
  capability map (CMAF, AV1 adoption, low-latency).
- **Dependencies:** `ravenclaude-core`. Seams → backend/frontend-engineering, the
  cloud plugins (media services / CDN), security-engineering (DRM/token auth).

### 7. social-media-content-operations
- **Purpose/value:** organic social as a repeatable system — channel strategy,
  content calendar, repurposing pipeline, community management, creator/UGC ops,
  organic analytics. marketing-operations leans demand-gen/martech; this is the
  organic-content engine.
- **Approach:** 2 agents; channel-strategy tree, content-calendar + repurposing
  templates, community-response playbooks, organic-metrics reference.
- **Dependencies:** `ravenclaude-core`. Seams → marketing-operations, developer-relations,
  web-design (content/SEO).

### 8. knowledge-management
- **Purpose/value:** make the org's own knowledge findable and current — taxonomy/IA,
  KB/wiki governance, findability, knowledge decay/ops, KCS (Knowledge-Centered
  Service). technical-writing-docs owns *authoring*; search-relevance owns *the
  ranking engine*; nobody owns *the knowledge system*.
- **Approach:** 2 agents; taxonomy-design + KB-governance trees, KCS workflow,
  knowledge-audit/decay templates.
- **Dependencies:** `ravenclaude-core`. Seams → technical-writing-docs,
  search-relevance-engineering, customer-support-cx-operations (KCS in support).

### 9. research-grants-administration
- **Purpose/value:** sponsored-programs lifecycle — pre-award proposal/budget, post-award
  compliance (2 CFR 200 Uniform Guidance), effort reporting, F&A/indirect-cost recovery,
  sub-recipient monitoring. Distinct from nonprofit-fundraising (donor/development) and
  public-sector-govtech's grants-management-analyst (gov-side grant *programs*).
- **Approach:** 2 agents; pre-award vs post-award split, budget + compliance templates,
  Uniform-Guidance reference with dated citations.
- **Dependencies:** `ravenclaude-core`. Seams → nonprofit-fundraising, finance,
  clinical-trials (for research orgs), regulatory-compliance.
- **Feasibility note (Medium):** regulation-heavy; needs the dated-citation discipline.

### 10. networking-engineering
- **Purpose/value:** general network engineering independent of one cloud — routing/
  switching, DNS architecture, load balancing, TLS/PKI, zero-trust segmentation,
  SD-WAN, network observability. The cloud plugins own *their* VPC; nobody owns the
  portable networking craft.
- **Approach:** 2 agents (`network-architect`, `network-implementation-engineer`);
  decision trees for L4-vs-L7 load balancing, DNS strategy, and zero-trust segmentation.
- **Dependencies:** `ravenclaude-core`. Seams → aws/azure/gcp-cloud (cloud-native net),
  security-engineering (zero-trust/firewall), observability-sre.

## Prioritization rationale

Ranking = **Demand × Feasibility**, penalized for overlap with an existing plugin and
for freshness/disclaimer burden:

- **Tier 1 (build first): #1 pricing-monetization, #2 ux-research, #3 chief-of-staff-operations.**
  All High/High, zero-to-low overlap, built on stable public frameworks (no volatile
  vendor facts, no heavy regulatory disclaimer surface). pricing-monetization wins the
  top slot because the "what do we charge" question is asked constantly and is owned by
  *no* current agent.
- **Tier 2: #5 partnerships, #6 video-streaming, #7 social-media, #8 knowledge-management.**
  Solid gaps, slightly narrower demand or more adjacent to an existing plugin.
- **Tier 3: #4 corporate-tax-advisory, #9 research-grants-administration, #10 networking-engineering.**
  Real gaps, but each carries either a heavy freshness/disclaimer burden (tax, grants)
  or partial coverage from the cloud plugins (networking), lowering near-term ROI.

## Build status (this PR)

- **Built fully:** **#1 pricing-monetization** — 2 agents, skills, a 3-doc knowledge
  bank with decision trees, best-practices, templates, manifests, wired into
  `marketplace.json` and `docs/architecture.md`. See `plugins/pricing-monetization/`.
- **Documented for follow-up:** #2–#10 above, each with an approach + dependency outline
  ready to build in subsequent PRs (one plugin per PR keeps CI's count gates from
  colliding across concurrent plugin PRs — see `scripts/check-marketplace-claims.py`).

**Why one plugin fully rather than ten partially:** every plugin in this marketplace is
gate-enforced (frontmatter scenario schema, accurate agent/skill counts, architecture-doc
roster, ≤1024-char descriptions) and opinionated to a high bar. Ten half-built plugins
would fail those gates and dilute the catalog; one built to standard plus a researched
backlog is the higher-value, honest deliverable for an unattended run.
