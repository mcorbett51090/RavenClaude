# Twenty candidate plugins for RavenClaude — research, prioritization & build kickoff

_Authored 2026-06-08 by `claude`. Branch: `claude/gallant-tesla-hko33`._

## Purpose

Identify **20 new plugins not yet implemented** in the RavenClaude marketplace, with — for
each — purpose/value, a basic implementation approach, dependencies, and a demand × feasibility
priority. Then begin building the highest-priority one.

## Method & grounding (this-session checks)

1. **Enumerated the existing catalog** — `python3 -c "import json; …"` over
   `.claude-plugin/marketplace.json` returned **65 registered plugins**, and a `comm -23`
   against `ls plugins/` confirmed **disk == registry (zero drift)**. So every candidate below
   was checked for absence against the real, current set — not a guess.
2. **Studied two reference builds** — the lean vertical (`hospice-referral-sales`) and the
   software-cluster horizontal (`devops-cicd`) — to ground each "implementation approach" in the
   actual house pattern (4–6 agents w/ scenario frontmatter, 5–6 skills, 4–6 commands, 4 templates,
   a Mermaid decision-tree knowledge bank, ~12 best-practices, scenarios, 1 advisory hook, optional
   stdlib calculator / `.lsp.json`).
3. **Grounded the demand claim** for the top horizontal candidates with web search (June 2026):
   - **Platform engineering / IDP:** Gartner forecasts **80% of large software-engineering orgs
     will have platform teams by 2026** (up from 45% in 2022); **Backstage holds ≈89% IDP-portal
     share** with 270+ public adopters. (`gartner` via dev.to/roadie.io; `backstage.io`.)
   - **FinOps:** the Cloud FinOps market is **≈$15.77B in 2026, ~9.5–11.5% CAGR**, with board-level
     demand as AI-inference/token spend eclipses training. (`mordorintelligence`, `marketsandmarkets`,
     `data.finops.org`.)
   - **AI security remediation is an explicit unmet need** (only ~28% of devs use AI agents for
     vuln remediation despite security being a top concern) — but `security-engineering` already
     exists, so we route there rather than add a duplicate.
   - Source links are listed in [`sources.md`](./sources.md).

Anything below that is reasoned from the catalog gap rather than a cited market figure is marked
`[gap-analysis]`; volatile market figures carry their source and a re-verify-at-use rider.

---

## The catalog today (what the 20 must NOT duplicate)

65 plugins across: **core** (ravenclaude-core); **software-delivery** (api, backend, frontend,
mobile, database, auth, devops-cicd, qa-test-automation, cloud-native-kubernetes, terraform-iac,
observability-sre, security-engineering, web-design, technical-writing-docs,
experimentation-growth-engineering); **cloud** (aws, azure, gcp); **data & AI** (data-platform,
analytics-engineering, data-streaming, ml-engineering, data-governance-privacy, applied-statistics,
microsoft-fabric, tableau, claude-app-engineering); **Microsoft stack** (power-platform,
m365-copilot, microsoft-graph); **business/product** (finance, fintech-payments, product-management,
project-management, process-improvement, procurement-sourcing, customer-success-analytics,
freight-forwarding-sales, staffing-operations, regulatory-compliance); **industry verticals**
(commercial-real-estate, restaurant-operations, veterinary-practice, dental-practice,
medical-revenue-cycle, insurance-pc, nonprofit-fundraising, fleet-logistics, renewable-energy,
clinical-trials, ecommerce-dtc, cannabis-operations, skilled-trades-contracting,
precision-agriculture, legal-small-firm, game-development, film-video-production, architecture-aec,
senior-care-operations, hospice-referral-sales, edtech-partner-success); plus salesforce,
ai-coding-model-guidance, team-portfolio.

---

## The 20 candidates

Grouped by tier (the prioritization rationale is in the next section). Every one is verified
**absent** from the 65.

### Tier 1 — horizontal technical-platform gaps (highest demand × feasibility × fit)

| # | Plugin | Purpose & value | Implementation approach | Dependencies |
|---|---|---|---|---|
| 1 | **platform-engineering-idp** | The "platform-as-a-product" layer above CI/CD: internal developer platforms, Backstage/IDP portals, golden paths & software templates, self-service infra (Crossplane/score), paved roads, developer-experience (DevEx) metrics, platform team topologies. **Demand:** Gartner 80%-by-2026; Backstage ≈89% share. | 4 agents (platform-product-lead, idp-portal-engineer, golden-path-engineer, devex-metrics-engineer); 5 skills; Mermaid trees (buy-vs-build IDP, golden-path scope, self-service boundary); ~12 best-practices; templates (golden-path spec, Backstage `catalog-info.yaml`, paved-road RFC); advisory hook; `.lsp.json` (YAML). | ravenclaude-core. Seams → devops-cicd, cloud-native-kubernetes, observability-sre, technical-writing-docs. |
| 2 | **finops-cloud-cost** | Cross-cloud cost engineering & governance: the FinOps Framework (inform/optimize/operate), unit economics, showback/chargeback & tagging, rightsizing/commitments (RIs/SPs/CUDs), **AI/token & GenAI-inference cost governance**, anomaly detection, budgets/alerts. **Demand:** $15.77B market, board-level. | 4 agents (finops-practice-lead, cost-optimization-engineer, cost-allocation-engineer, ai-cost-governance-engineer); 5 skills; trees (commitment-vs-on-demand, allocation model, rightsizing); ~12 best-practices; templates (tagging policy, showback model, FinOps maturity scorecard); hook (flags untagged/`:latest`/no-budget); stdlib `finops_calc.py` (RI break-even, unit-cost, savings). | ravenclaude-core. Seams → aws/azure/gcp-cloud (each touches FinOps; this owns it cross-cloud), claude-app-engineering (token cost). |
| 3 | **search-relevance-engineering** | The retrieval/search layer: Elasticsearch/OpenSearch, vector + **hybrid (BM25 + dense) search**, embeddings, chunking, reranking, relevance tuning & evaluation (nDCG/MRR), the RAG retrieval tier. Fills the gap claude-app-engineering only touches at the app surface. `[gap-analysis]` | 4 agents (search-architect, relevance-engineer, vector-retrieval-engineer, search-eval-engineer); 5 skills; trees (lexical-vs-vector-vs-hybrid, chunking strategy, rerank-or-not); best-practices; templates (relevance-judgment set, index mapping); hook; `search_eval.py` (nDCG/MRR/recall@k). | ravenclaude-core. Seams → claude-app-engineering (RAG app), data-platform, ml-engineering. |
| 4 | **embedded-iot-firmware** | Hardware-adjacent engineering entirely uncovered today: embedded C/C++/Rust, RTOS (FreeRTOS/Zephyr), MCU peripherals, low-power design, device-to-cloud (MQTT), OTA updates, secure boot. `[gap-analysis]` | 4 agents (embedded-architect, firmware-engineer, rtos-engineer, iot-connectivity-engineer); 5 skills; trees (bare-metal-vs-RTOS, OTA strategy, power budget); best-practices; templates (HAL layering, OTA rollback plan); hook (flags blocking delays in ISRs, `malloc` in hot paths). | ravenclaude-core. Seams → security-engineering (secure boot), aws/azure-cloud (IoT Core/Hub). |
| 5 | **localization-i18n-engineering** | i18n/l10n engineering: string extraction, ICU MessageFormat, pluralization, RTL/bidi, locale-aware formatting, pseudo-localization, TMS integration, l10n CI gates. `[gap-analysis]` | 3 agents (i18n-architect, l10n-pipeline-engineer, localization-qa-engineer); 5 skills; trees (library choice, key strategy, machine-vs-human translation); best-practices; templates (string catalog, pseudo-loc gate); hook (flags hardcoded user-facing strings, string concatenation). | ravenclaude-core. Seams → frontend-engineering, mobile-engineering, technical-writing-docs. |

### Tier 2 — horizontal business/operations gaps

| # | Plugin | Purpose & value | Implementation approach | Dependencies |
|---|---|---|---|---|
| 6 | **revenue-operations** (RevOps) | Lead-to-cash operations: CRM-as-process (SFDC/HubSpot admin discipline), pipeline hygiene & stage definitions, territory/quota/comp design, forecasting methodology, sales-funnel analytics, GTM data model. Distinct from product-management (what/why) and customer-success-analytics (post-sale health). `[gap-analysis]` | 5 agents (revops-lead, crm-operations-architect, sales-comp-and-territory-analyst, pipeline-forecast-engineer, gtm-data-analyst); skills; trees (forecast method, comp-plan shape, lead-routing); best-practices; templates (stage definitions, comp plan, territory model); hook; `revops_calc.py` (quota attainment, coverage, win-rate). | ravenclaude-core. Seams → salesforce, customer-success-analytics, data-platform, finance. |
| 7 | **marketing-operations-demand-gen** | The martech/demand-gen layer: campaign ops, marketing automation (lifecycle/email/nurture), multi-touch attribution, lead scoring, MQL→SQL handoff, SEO/content ops, marketing analytics. web-design touches SEO content; nothing owns marketing ops. `[gap-analysis]` | 4 agents (marketing-ops-lead, demand-gen-strategist, marketing-automation-engineer, attribution-analyst); skills; trees (attribution model, channel mix, lead-score design); best-practices; templates (campaign brief, nurture flow, UTM taxonomy); hook. | ravenclaude-core. Seams → web-design, experimentation-growth-engineering, revenue-operations, data-platform. |
| 8 | **people-operations-hr** | Internal HR/People ops (NOT a staffing-agency business — that's staffing-operations): hiring pipelines & structured interviews, onboarding, performance & calibration, comp bands & leveling, HRIS, policy, people analytics. `[gap-analysis]` | 4 agents (people-ops-lead, talent-acquisition-strategist, performance-and-comp-analyst, people-analytics-engineer); skills; trees (level/comp band, build-vs-buy ATS, performance model); best-practices; templates (scorecard, leveling matrix, onboarding plan); hook (flags biased JD language, PII in plaintext). | ravenclaude-core. Seams → staffing-operations, finance, data-platform. |
| 9 | **supply-chain-planning** | The plan layer between buy and move: S&OP, demand forecasting, inventory & safety-stock, MRP, replenishment, supplier capacity. procurement-sourcing buys, freight/fleet move — nobody plans. `[gap-analysis]` | 4 agents (supply-chain-planner, demand-planning-analyst, inventory-optimization-engineer, sop-process-lead); skills; trees (forecast method, inventory policy, make-vs-buy); best-practices; templates (S&OP deck, safety-stock model); hook; `supply_calc.py` (EOQ, safety stock, reorder point, fill rate). | ravenclaude-core. Seams → procurement-sourcing, freight-forwarding-sales, fleet-logistics, applied-statistics. |
| 10 | **customer-support-cx-operations** | Contact-center / support operations: deflection & self-service, CSAT/CES/NPS programs, knowledge-base & macros, SLA/queue/staffing (Erlang), QA scorecards, AI-agent deflection design. data-platform only normalizes support tickets. `[gap-analysis]` | 4 agents (cx-ops-lead, support-quality-analyst, knowledge-and-deflection-strategist, contact-center-workforce-analyst); skills; trees (channel strategy, deflection-vs-staff, escalation design); best-practices; templates (QA scorecard, macro library, SLA matrix); hook; `cx_calc.py` (Erlang C staffing, deflection ROI, CSAT). | ravenclaude-core. Seams → data-platform (support normalization), customer-success-analytics, claude-app-engineering (AI deflection). |

### Tier 3 — high-demand industry verticals not yet covered

| # | Plugin | Purpose & value | Implementation approach | Dependencies |
|---|---|---|---|---|
| 11 | **wealth-management-advisory** | RIA / financial-advisor practice: financial planning, portfolio review & rebalancing narrative, client review prep, suitability / Reg BI, prospecting & AUM growth. finance = corporate FP&A — distinct buyer. `[gap-analysis]` | 5 agents (advisory-practice-lead, financial-planning-specialist, portfolio-review-analyst, client-relationship-manager, advisory-compliance-advisor); skills; trees; best-practices; templates (financial plan, client review, IPS); hook (flags guarantees/return promises, PII). | ravenclaude-core. Seams → finance, regulatory-compliance. |
| 12 | **accounting-firm-cpa** | Public-accounting/CPA-firm ops: tax-season workflow, Client Accounting Services (CAS), engagement & workpaper management, audit-firm ops, advisory. finance = in-house corporate — distinct. `[gap-analysis]` | 5 agents (firm-practice-lead, tax-workflow-strategist, cas-engagement-lead, audit-engagement-lead, firm-advisory-lead); skills; trees; best-practices; templates (engagement letter, PBC list, workpaper index); hook. | ravenclaude-core. Seams → finance, regulatory-compliance, medical-revenue-cycle (billing patterns). |
| 13 | **retail-store-operations** | Brick-and-mortar retail: merchandising & planograms, inventory/POS, labor scheduling, shrink/loss prevention, omnichannel (BOPIS), store KPIs. ecommerce-dtc is online-only. `[gap-analysis]` | 5 agents (store-ops-lead, merchandising-analyst, inventory-and-replenishment-analyst, labor-scheduling-analyst, loss-prevention-advisor); skills; trees; best-practices; templates (planogram brief, labor model); hook; `retail_calc.py` (GMROI, sell-through, shrink). | ravenclaude-core. Seams → ecommerce-dtc, supply-chain-planning, procurement-sourcing. |
| 14 | **hospitality-hotels** | Hotel/lodging ops: revenue management (RevPAR/ADR/occupancy), front desk & reservations, OTA/channel management, housekeeping, guest experience/reputation. restaurant-operations is F&B-only. `[gap-analysis]` | 5 agents (hotel-ops-lead, revenue-manager, reservations-and-channel-analyst, guest-experience-lead, housekeeping-and-rooms-analyst); skills; trees; best-practices; templates (rate plan, channel mix); hook; `hotel_calc.py` (RevPAR, ADR, occupancy, displacement). | ravenclaude-core. Seams → restaurant-operations, marketing-operations-demand-gen. |
| 15 | **property-management-residential** | Residential PM: leasing & tenant lifecycle, maintenance/work-order ops, rent collection & delinquency, turnover, fair-housing compliance. commercial-real-estate is CRE investing/brokerage. `[gap-analysis]` | 4 agents (pm-ops-lead, leasing-strategist, maintenance-operations-analyst, pm-compliance-advisor); skills; trees; best-practices; templates (lease workflow, turn checklist, work-order SLA); hook (fair-housing language flags). | ravenclaude-core. Seams → commercial-real-estate, skilled-trades-contracting, field-service-management. |
| 16 | **behavioral-mental-health-practice** | Outpatient behavioral/mental-health clinic: intake & assessment workflow, treatment planning, telehealth ops, 42 CFR Part 2 + HIPAA, measurement-based care, billing. Generic RCM exists; behavioral health is distinct (Part 2, MBC). `[gap-analysis]` | 5 agents (practice-ops-lead, intake-and-scheduling-analyst, clinical-documentation-advisor, telehealth-operations-lead, behavioral-billing-compliance-advisor); skills; trees; best-practices; templates (intake packet, treatment plan, no-show policy); hook (PHI/Part-2 flags). | ravenclaude-core. Seams → medical-revenue-cycle, senior-care-operations, regulatory-compliance. |
| 17 | **construction-general-contractor** | GC project delivery: estimating/takeoff, bidding, CPM scheduling, submittals/RFIs, change orders, safety, closeout. architecture-aec = design; skilled-trades = a single-trade sub business. `[gap-analysis]` | 5 agents (gc-project-lead, estimating-and-takeoff-analyst, scheduling-engineer, submittal-rfi-coordinator, jobsite-safety-advisor); skills; trees; best-practices; templates (bid package, schedule of values, RFI/CO log); hook; `construction_calc.py` (markup, SOV, earned value). | ravenclaude-core. Seams → architecture-aec, skilled-trades-contracting, project-management. |
| 18 | **automotive-dealership** | Dealership ops: F&I, fixed ops (service & parts), inventory/floor-plan, BDC/CRM, sales desking, compliance. Uncovered. `[gap-analysis]` | 5 agents (dealership-ops-lead, fixed-ops-analyst, fni-advisor, inventory-and-desking-analyst, dealership-compliance-advisor); skills; trees; best-practices; templates (desking worksheet, fixed-ops KPI); hook; `dealer_calc.py` (gross, F&I PVR, days-supply). | ravenclaude-core. Seams → fleet-logistics, finance, marketing-operations-demand-gen. |
| 19 | **public-sector-govtech** | Government/civic-tech delivery: public procurement (RFP/RFI), grants management, FOIA/records, **Section 508/WCAG accessibility for gov**, citizen-services design, FedRAMP/StateRAMP posture. Uncovered. `[gap-analysis]` | 4 agents (govtech-delivery-lead, public-procurement-strategist, grants-management-analyst, gov-accessibility-and-records-advisor); skills; trees; best-practices; templates (RFP response, grant narrative, 508 VPAT); hook. | ravenclaude-core. Seams → nonprofit-fundraising, web-design (a11y), regulatory-compliance, technical-writing-docs. |
| 20 | **field-service-management** | FSM dispatch ops (HVAC/plumbing/elevator/medical-device service): scheduling & dispatch, technician utilization, first-time-fix, parts/truck-stock, mobile workforce, SLAs. skilled-trades = a contracting-business's sales; fleet-logistics = vehicles; FSM dispatch is distinct. `[gap-analysis]` | 4 agents (fsm-ops-lead, dispatch-and-scheduling-engineer, technician-productivity-analyst, parts-and-inventory-analyst); skills; trees; best-practices; templates (dispatch board, SLA matrix, PM schedule); hook; `fsm_calc.py` (utilization, first-time-fix, MTTR, route density). | ravenclaude-core. Seams → skilled-trades-contracting, fleet-logistics, customer-support-cx-operations. |

---

## Prioritization rationale (demand × feasibility × marketplace fit)

Scored on three axes, 1–5: **Demand** (market/usage evidence), **Feasibility** (how cleanly it fits
the house pattern + how self-contained the knowledge is), **Fit** (does it strengthen the existing
cluster via clean seams, or sit orphaned).

| Rank | Plugin | Demand | Feasibility | Fit | Why this rank |
|---|---|---|---|---|---|
| **1** | **platform-engineering-idp** | 5 (Gartner 80%, Backstage 89%) | 5 | 5 | **Strongest cited demand, cleanest seam** (sits directly above devops-cicd + cloud-native + observability-sre + technical-writing-docs), and the RavenClaude repo is *itself* a golden-path/paved-road artifact → dogfood-relevant. **Build first.** |
| 2 | finops-cloud-cost | 5 ($15.77B, board-level) | 5 | 5 | Board-level demand; the 3 cloud plugins each touch FinOps but none owns it cross-cloud; a stdlib calc gives concrete value. |
| 3 | revenue-operations | 4 | 4 | 5 | Pairs with the existing salesforce + customer-success-analytics + finance triangle; common SMB/consulting ask. |
| 4 | customer-support-cx-operations | 4 | 4 | 4 | data-platform already normalizes support tickets — this is the operations brain on top; AI-deflection is timely. |
| 5 | search-relevance-engineering | 4 | 3 | 4 | High demand (RAG everywhere) but knowledge is fast-moving; closes a real gap above claude-app-engineering. |
| 6 | marketing-operations-demand-gen | 4 | 4 | 4 | Completes the GTM trio with revops; clean seams to web-design + experimentation. |
| 7 | supply-chain-planning | 3 | 4 | 5 | Slots cleanly between procurement-sourcing and freight/fleet; strong stdlib calc. |
| 8 | people-operations-hr | 3 | 4 | 4 | Broad horizontal demand; distinct from staffing-operations. |
| 9–10 | construction-gc, retail-store-operations | 3 | 4 | 4 | Large industries, clean vertical pattern, good calc surface. |
| 11–15 | hospitality-hotels, property-management-residential, wealth-management-advisory, accounting-firm-cpa, field-service-management | 3 | 4 | 3–4 | Solid verticals with clear buyers; rank below horizontals because individual demand is narrower. |
| 16–20 | behavioral-mental-health, automotive-dealership, public-sector-govtech, localization-i18n, embedded-iot-firmware | 2–3 | 3–4 | 3 | Genuine gaps; either narrower demand (govtech, embedded) or heavier specialized knowledge (i18n, embedded, Part-2 behavioral) → later. |

**Tie-breaker doctrine:** horizontals that strengthen the existing software/cloud/data cluster beat
standalone verticals, because (a) the marketplace's center of gravity is technical, (b) they reuse
the cluster's seams and so compound in value, and (c) their demand is cited, not just inferred.

---

## Progress on initial builds

- **#1 `platform-engineering-idp` — BUILD STARTED this session.** See the plugin under
  `plugins/platform-engineering-idp/` and the CHANGELOG. Built to the house standard (agents with
  scenario-authoring frontmatter, skills, commands, templates, a Mermaid decision-tree knowledge
  bank, best-practices, scenarios, an advisory hook), registered in `marketplace.json`, and run
  through the validation suite (JSON, frontmatter gate, shell `-n` + executable, prettier, layout
  allow-list).
- **#2–#20 — specified above, not yet built.** Each is a self-contained follow-on PR using the same
  scaffold.

## Blockers

- **Scope vs. depth (the honest one):** each RavenClaude plugin is ≈30–50 meticulously-authored
  files with deep, cited knowledge banks. Building **all** top-priority plugins to that depth in one
  session is not feasible without sacrificing the per-file quality the gates and house style demand.
  Decision: **build #1 to full, gate-passing depth** rather than scaffold several shallowly; ship the
  remaining 19 as this researched, prioritized roadmap. No tooling/access blockers were hit —
  marketplace registry, layout allow-list (standard `plugins/*/**` globs already cover a new plugin),
  and the validation scripts all work in this environment.
