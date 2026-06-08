# Twenty New Plugin Candidates — Gap Analysis & Build Kickoff

**Date:** 2026-06-08
**Author:** plugin-research pass (Claude Code, agent-readable)
**Audience:** Matt Corbett, working ON the marketplace.
**Status:** Working document. Candidate #1 (`platform-engineering`) is being built in the same branch as this doc; the rest are scoped for follow-on passes.

---

## 1. Method

The marketplace already ships **65 plugins** (see [`.claude-plugin/marketplace.json`](../../.claude-plugin/marketplace.json)), including the
"20 underserved-market plugins" batch shipped in PRs #305/#307/#308. So the bar for a *new* candidate is genuine
white space — a domain or discipline with no existing home and a clean seam to the plugins that already exist.

I inventoried all 65 existing plugins, grouped them into clusters (core/meta, software-delivery chain, cloud,
app-craft, data & AI, Microsoft stack, business/product, and ~22 SMB verticals), then looked for:

- **Horizontal engineering disciplines** that are recognized practices in 2026 but have no plugin (e.g. internal
  developer platforms, localization, embedded/IoT).
- **Business/ops functions** adjacent to existing ones but distinct (e.g. RevOps vs. customer-success-analytics;
  GRC vs. financial regulatory-compliance; people-ops vs. staffing-operations).
- **SMB verticals** that match the marketplace's proven vertical pattern but aren't covered (e.g. wealth-management
  RIA vs. corporate finance; behavioral-health vs. dental/vet; residential property mgmt vs. commercial RE).

Each candidate is scored on the same five criteria the existing roadmap uses (see
[`../plugin-roadmap-analysis.md`](../plugin-roadmap-analysis.md)): **demand**, **differentiation**,
**feasibility** (can it be authored from established, citable practice without a live engagement),
**seam-cleanliness** (does it slot next to existing plugins without overlap), and **founder-fit** (does it
lean on Matt's positioning). 1–5 each; higher is better.

---

## 2. The twenty candidates

### Tier 1 — build first (horizontal engineering, high demand, clean seams, author-from-practice)

| # | Plugin | Purpose & value | Implementation approach | Dependencies / seams | Score (D/Diff/Feas/Seam/Fit) |
|---|---|---|---|---|---|
| 1 | **platform-engineering** | The internal-developer-platform (IDP) discipline: platform-as-product, Team Topologies, golden paths/paved roads, developer portals (Backstage/Port/Cortex), self-service provisioning, and DORA/DevEx adoption metrics. The "paved road" layer above CI/CD and Kubernetes. | 3 agents (platform-architect, developer-portal-engineer, golden-paths-and-adoption-engineer), a decision-tree knowledge bank (build-vs-buy IDP, paved-road-vs-guardrail), ~10 best-practices, skills, commands, 1 advisory hook, scenarios. | Seams: pipelines → `devops-cicd`; clusters → `cloud-native-kubernetes`; SLOs → `observability-sre`; IaC modules → `terraform-iac`. Requires `ravenclaude-core@>=0.7.0`. | 5/4/5/5/4 |
| 2 | **cybersecurity-grc** | Security **governance, risk & compliance** — SOC 2, ISO 27001/27701, NIST CSF/800-53, risk registers, control mapping, vendor/third-party risk, evidence collection, audit readiness. Distinct from `security-engineering` (AppSec/threat modeling) and `regulatory-compliance` (financial regulators). | 3–4 agents (grc-architect, control-and-evidence-engineer, third-party-risk-analyst, audit-readiness-lead), control-framework crosswalk knowledge, risk-register + SoA templates, decision trees (which framework, control mapping). | Seams: AppSec verdicts → `security-engineering`; financial-reg → `regulatory-compliance`; data-subject mechanics → `data-governance-privacy`. | 5/4/5/5/4 |
| 3 | **revops** (revenue operations) | The B2B revenue engine: lead-to-cash funnel, CRM hygiene, territory/quota/comp design, pipeline & forecast methodology, sales-marketing-CS handoffs, the RevOps data model. Distinct from `customer-success-analytics` (retention) and `salesforce` (platform build). | 3 agents (revops-architect, pipeline-and-forecast-analyst, gtm-systems-engineer), funnel-metric glossary, forecast-methodology decision trees, comp/territory templates, a stdlib forecast/coverage calculator. | Seams: CS health → `customer-success-analytics`; CRM build → `salesforce`; warehouse → `data-platform`. | 5/4/4/4/3 |
| 4 | **esg-sustainability-reporting** | Corporate sustainability & ESG disclosure: GHG accounting (Scopes 1/2/3), CSRD/ESRS, ISSB/IFRS S1-S2, SEC climate rule, materiality assessment, emissions-factor methodology, assurance-readiness. Timely (insurer/procurement-driven, like the idea-board's finding). | 3 agents (esg-reporting-architect, ghg-accounting-analyst, disclosure-and-assurance-lead), framework-crosswalk knowledge, materiality + inventory templates, an emissions calculator. | Seams: financial-reporting → `finance`; data lineage → `data-governance-privacy`; financial regulators → `regulatory-compliance`. | 4/4/4/4/4 |
| 5 | **localization-i18n** | Software & content localization engineering: i18n architecture (ICU MessageFormat, locale data, RTL, pluralization), translation-management workflow (TMS, string extraction, pseudo-localization), and localization QA. | 2–3 agents (i18n-architect, localization-engineer, localization-qa), decision trees (library choice, key strategy), string-catalog + pseudo-loc templates. | Seams: UI implementation → `frontend-engineering`/`mobile-engineering`; docs → `technical-writing-docs`. | 4/4/5/5/2 |

### Tier 2 — strong second wave (adjacent functions & high-fit verticals)

| # | Plugin | Purpose & value | Implementation approach | Dependencies / seams | Score |
|---|---|---|---|---|---|
| 6 | **wealth-management-ria** | Personal financial advisory / RIA practice: financial planning, portfolio construction & rebalancing, IPS authoring, fiduciary/Reg-BI conduct, client review prep. Distinct from corporate `finance`. | 3 agents (financial-planner, portfolio-analyst, compliance-and-client-review-lead), planning + IPS templates, a retirement/withdrawal calculator. | Seams: corporate FP&A → `finance`; securities regs → `regulatory-compliance`. | 4/4/3/4/4 |
| 7 | **people-ops-hr** | HR / People operations for SMBs: hiring & onboarding, performance & comp frameworks, policy/handbook authoring, employment-compliance basics, HRIS data hygiene. Distinct from `staffing-operations` (the staffing *business*). | 3 agents (people-ops-generalist, talent-acquisition-lead, total-rewards-analyst), handbook + job-ladder templates, comp-band calculator. | Seams: staffing-agency ops → `staffing-operations`; payroll/GL → `finance`. | 4/3/4/4/2 |
| 8 | **manufacturing-operations** | Discrete/process manufacturing ops: production planning (MRP/MPS), shop-floor/MES, OEE & throughput, quality (SPC, NCR/CAPA), inventory & S&OP. | 3 agents (production-planner, shop-floor-and-oee-analyst, quality-and-capa-lead), OEE + MRP templates, a takt/OEE calculator. | Seams: lean methods → `process-improvement`; procurement → `procurement-sourcing`; logistics → `fleet-logistics`. | 4/4/3/4/2 |
| 9 | **construction-field-management** | Construction project delivery (field side): RFIs, submittals, change orders, daily logs, schedule of values/pay apps, punch lists, safety. Distinct from `architecture-aec` (design). | 3 agents (project-engineer, cost-and-change-controls-lead, field-and-safety-coordinator), RFI/submittal/CO templates, pay-app calculator. | Seams: design/BIM → `architecture-aec`; PM craft → `project-management`. | 4/4/3/4/2 |
| 10 | **property-management-residential** | Residential property management: leasing & tenant lifecycle, maintenance/work-orders, rent roll & delinquency, owner reporting, fair-housing basics. Distinct from `commercial-real-estate`. | 3 agents (leasing-and-tenant-ops, maintenance-coordinator, owner-reporting-analyst), lease-abstract + owner-statement templates. | Seams: commercial RE → `commercial-real-estate`; accounting → `finance`. | 4/4/3/4/2 |
| 11 | **behavioral-health-practice** | Outpatient behavioral/mental-health practice ops: intake, treatment planning, clinical documentation (DAP/SOAP), insurance auth, no-show/scheduling, 42 CFR Part 2/HIPAA. | 3 agents (practice-ops, clinical-documentation-specialist, billing-and-auth-lead), note + treatment-plan templates. | Seams: revenue cycle → `medical-revenue-cycle`; senior care → `senior-care-operations`. | 4/4/3/4/2 |
| 12 | **performance-engineering** | System performance & capacity: load/stress/soak testing (k6/Gatling/Locust), profiling & flame graphs, capacity planning, performance budgets at the system level. Distinct from `frontend` Core Web Vitals and `observability-sre`. | 3 agents (perf-architect, load-testing-engineer, profiling-and-capacity-engineer), test-plan + budget templates, decision trees (test type, bottleneck triage). | Seams: web vitals → `frontend-engineering`; SLOs → `observability-sre`; DB tuning → `database-engineering`. | 4/4/4/4/3 |

### Tier 3 — backlog (real white space, lower immediate pull or narrower fit)

| # | Plugin | Purpose & value | Implementation approach | Dependencies / seams | Score |
|---|---|---|---|---|---|
| 13 | **embedded-iot-engineering** | Firmware/edge: RTOS, C/C++/Rust on MCUs, device comms (MQTT/BLE/LoRa), OTA, power budgeting, fleet provisioning. | 3 agents (firmware-architect, embedded-engineer, iot-connectivity-engineer), decision trees (RTOS-vs-bare-metal, protocol choice). | Seams: cloud ingest → `data-streaming-engineering`/cloud plugins. | 3/5/4/5/2 |
| 14 | **content-and-growth-marketing** | Content strategy, SEO program, lifecycle/email, demand-gen analytics. Broader than `web-design`'s content-strategist. | 3 agents (content-strategist, seo-program-lead, lifecycle-marketing-engineer). | Seams: marketing-site → `web-design`; experiments → `experimentation-growth-engineering`. | 4/3/4/3/2 |
| 15 | **legal-ops-clm** | Corporate legal operations & contract lifecycle: intake, playbooks, clause libraries, redline review, obligation/renewal tracking. Distinct from `legal-small-firm` (a law-firm business). | 3 agents (legal-ops-lead, contract-review-specialist, obligations-analyst), playbook + clause-library templates. | Seams: law-firm ops → `legal-small-firm`; procurement contracts → `procurement-sourcing`. | 4/4/3/4/2 |
| 16 | **public-sector-grants** | Government/nonprofit grants & compliance: grant search, proposal authoring, budget narratives, 2 CFR/Uniform Guidance, sub-recipient monitoring, reporting. Distinct from `nonprofit-fundraising` (donor side). | 3 agents (grant-strategist, proposal-writer, grants-compliance-analyst). | Seams: donor fundraising → `nonprofit-fundraising`; finance → `finance`. | 3/4/3/4/2 |
| 17 | **hospitality-hotel-operations** | Lodging ops: front desk/PMS, revenue management (RevPAR/ADR/occupancy), housekeeping, channel/OTA mix, guest experience. Distinct from `restaurant-operations`. | 3 agents (hotel-ops-lead, revenue-manager, guest-experience-analyst), a RevPAR/forecast calculator. | Seams: restaurant F&B → `restaurant-operations`. | 3/4/3/4/2 |
| 18 | **retail-store-operations** | Brick-and-mortar retail: merchandising/planograms, inventory & replenishment, labor scheduling, shrink, store P&L. Distinct from `ecommerce-dtc`. | 3 agents (store-ops-lead, merchandising-analyst, inventory-and-labor-planner). | Seams: online channel → `ecommerce-dtc`; sourcing → `procurement-sourcing`. | 3/4/3/4/2 |
| 19 | **data-science-research** | Exploratory data science (vs. `ml-engineering` MLOps): EDA, notebook hygiene, feature engineering, classical modeling, reproducible research, result communication. | 2 agents (data-scientist, research-reproducibility-engineer). | Seams: significance → `applied-statistics`; productionizing → `ml-engineering`. | 4/3/4/3/3 |
| 20 | **insurance-life-health-benefits** | Life/health/benefits side of insurance (vs. `insurance-pc` P&C): plan design, underwriting basics, benefits administration, ACA/ERISA basics, enrollment. | 3 agents (benefits-advisor, underwriting-analyst, enrollment-and-compliance-lead). | Seams: P&C → `insurance-pc`; HR benefits admin → `people-ops-hr` (#7). | 3/4/3/4/2 |

---

## 3. Prioritization rationale

The build order is **horizontal-before-vertical, author-from-practice-before-needs-an-engagement**:

1. **Horizontal engineering plugins (1, 2, 5, 12)** score highest because they (a) serve every consumer regardless
   of industry, (b) can be authored to a high bar from established, citable 2026 practice without a live client, and
   (c) slot cleanly next to the existing software-delivery cluster. They are the marketplace's proven strength.
2. **`platform-engineering` (#1) is the single best first build:** it is the most-recognized missing discipline in the
   software-delivery chain (the marketplace has CI/CD, K8s, IaC, observability, and security — but not the
   platform-as-product layer that ties them into golden paths), it has the cleanest seams (every adjacent plugin
   already exists to route to), and it needs no domain access to author well.
3. **`cybersecurity-grc` (#2)** is the strongest founder-fit horizontal: it compounds with Matt's
   `regulatory-compliance` credibility and the marketplace's governance assets (tribunal, posture dial, audit
   substrate from the idea-board), and SOC 2 / ISO 27001 demand is broad across SMB software buyers.
4. **Adjacent business functions and high-fit verticals (3, 4, 6–11)** follow once the horizontal wave lands, ordered
   by demand × seam-cleanliness. They mirror the existing vertical pattern, so they're low-risk to author but add less
   leverage than the horizontals.
5. **Tier 3** is real white space but either narrower (embedded/IoT, data-science-research) or lower immediate pull;
   parked behind a wake condition, the same discipline the idea-board applies to the competitor-analysis plugin —
   deepen/build when a real engagement exercises the need.

**Founder-fit note (Closebook alignment):** none of these compete with the Closebook commercial wedge from the
[idea board](../idea-board.md); they extend the *proof-of-craft surface area* (breadth) the same way the existing
65 do. `cybersecurity-grc` and `esg-sustainability-reporting` additionally reinforce the governance/assurance
positioning that Closebook and Track B3 lean on.

---

## 4. Build progress (this branch)

| Candidate | Status | Notes |
|---|---|---|
| #1 `platform-engineering` | **Building now** — setup + core agents + knowledge + best-practices + tests | Scaffolded to the marketplace's standard plugin shape (plugin.json, CLAUDE.md, README, agents with full scenario-authoring frontmatter, decision-tree knowledge bank, best-practices, skills, commands, advisory hook, scenarios, templates, CHANGELOG); marketplace entry + version bump. Validated against the AGENTS.md test suite (JSON validity, `bash -n`, prettier, frontmatter gate). |
| #2–#20 | **Scoped, not built** | This document is the durable backlog. Each is build-ready from the scope above; promote per the prioritization order as capacity allows. |

### Blockers / notes

- **No blockers encountered** building #1: all paths match existing `.repo-layout.json` allow-list globs
  (`plugins/*/...`), so no layout-manifest change was needed, and the plugin uses only the established file shapes.
- **Scope discipline:** building all 20 to the marketplace's depth bar (each is a 3–4-agent team with knowledge,
  best-practices, scenarios, and tests) is a multi-pass effort, not a single session. The right deliverable for this
  pass is the full candidate analysis + prioritization (this doc) plus one complete, gate-passing reference build
  (#1) that the rest can be modeled on — rather than 20 half-built plugins that would fail CI and break a consumer's
  `/plugin marketplace update`.

---

## 5. References

- [`../../.claude-plugin/marketplace.json`](../../.claude-plugin/marketplace.json) — the catalog of the 65 existing plugins.
- [`../plugin-roadmap-analysis.md`](../plugin-roadmap-analysis.md) — the original five-criteria ranking method this doc reuses.
- [`../idea-board.md`](../idea-board.md) — strategic-idea status board; the "20 underserved-market plugins" line and the Closebook wedge.
- [`../best-practices/agent-scenario-authoring.md`](../best-practices/agent-scenario-authoring.md) — the gated agent frontmatter schema every new agent must carry.
- [`../../AGENTS.md`](../../AGENTS.md) — "Adding a new plugin" steps + the pre-PR test suite this build is validated against.
