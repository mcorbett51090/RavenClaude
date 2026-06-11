# Plugin candidate research — 10 new RavenClaude plugins (2026-06)

> Research output for the "10 new plugins" task. The marketplace already ships **100**
> plugins covering most engineering, healthcare, sales/ops, and vertical-industry domains.
> This doc enumerates **10 gaps** that are genuinely uncovered, prioritizes them by user
> demand × technical feasibility, and records the build status of each.

> **Status (2026-06-11): research kept; the 3 P0 plugins were NOT merged.** The P0 plugins were
> scaffolded to gate-passing standard on the [`#409`](https://github.com/mcorbett51090/RavenClaude/pull/409)
> branch but **deliberately not shipped** — they're speculative (chosen against a demand heuristic,
> not a real engagement), and the marketplace's direction is proof-of-craft + build-on-real-demand,
> not catalog breadth (100 plugins is already plenty). This doc is kept as the **gap map** for when a
> real DevRel / higher-ed / PT (or any P1/P2) engagement lands; the scaffolded P0 code is recoverable
> from the closed `#409` branch in minutes. "scaffolded, parked" below = built-but-held, not in the marketplace.

## How the gaps were found

Inventoried all 100 existing plugins (`.claude-plugin/marketplace.json`) and grouped them by
super-domain (cloud/devops, data/ML, vertical-healthcare, vertical-finance, sales/marketing-ops,
industry-operations). Then looked for **high-demand professional roles with no home** in the
current roster — checking each candidate against the closest existing plugin to confirm it is a
real gap, not an overlap. A candidate only made the list if it (a) is a distinct role/domain, (b)
has clear, recurring demand, and (c) fits the established plugin template (specialist agents +
skills + cited knowledge + gated frontmatter).

## The 10 candidates

| # | Plugin | Gap it fills | Closest existing (why it's not a dup) | Priority |
|---|---|---|---|---|
| 1 | **developer-relations** | DevRel / developer-advocacy / DX program | `technical-writing-docs` is docs-only; `product-management` is product-side. Neither owns advocacy, community funnel, or DX activation metrics. | **P0 — scaffolded, parked** |
| 2 | **higher-education-administration** | College/university admin: enrollment, financial aid, retention, registrar | `k12-school-administration` is K-12 only; `edtech-partner-success` is vendor-side. No higher-ed institution operator. | **P0 — scaffolded, parked** |
| 3 | **physical-therapy-practice** | Outpatient PT/rehab clinic ops, documentation, units, denials | `dental-practice` / `veterinary-practice` / `medical-revenue-cycle` cover other clinic types; PT has its own 8-minute-rule / plan-of-care / KX-modifier rules. | **P0 — scaffolded, parked** |
| 4 | **investor-relations** | Public-company IR: earnings, disclosure, shareholder comms, consensus | `finance` is internal FP&A; `regulatory-compliance` is financial-regulatory AML/KYC. Neither owns the street-facing IR function. | P1 |
| 5 | **mergers-acquisitions-advisory** | Corp dev / M&A: sourcing, diligence, valuation, integration | `finance` (FP&A) and `wealth-management-ria` (personal) don't cover deal process or PMI. | P1 |
| 6 | **content-marketing-seo** | Editorial calendar, content strategy, organic/technical SEO | `marketing-operations` is martech/ops plumbing; `search-relevance-engineering` is search-ranking engineering, not content/SEO marketing. | P1 |
| 7 | **telecom-network-operations** | Telecom NOC / OSS-BSS / network ops | `observability-sre` is software SRE; `cloud-native-kubernetes` is app infra. No carrier-network operator. | P2 |
| 8 | **utilities-operations** | Electric/water/gas utility ops: outage, grid, metering, AMI | `renewable-energy` is generation/project-finance only; no T&D / distribution-utility operator. | P2 |
| 9 | **optometry-eyecare-practice** | Eye-care clinic + optical retail dispensing | Same clinic-ops family as dental/vet but distinct exam-to-dispense + optical-retail economics. | P2 |
| 10 | **franchise-operations** | Franchisor development & multi-unit franchising | `restaurant-operations` / `retail-store-operations` are single-concept operators, not the franchise system (FDD, royalties, unit economics across franchisees). | P2 |

## Per-candidate implementation approach & dependencies

All candidates follow the established marketplace template (see `plugins/field-service-management/`
for the reference shape) and inherit `ravenclaude-core` protocols. Each ships: **4 agents** (lead +
3 function specialists) with the full scenario-authoring frontmatter schema, **3 skills**, a
**decision-tree knowledge bank**, **4–6 best-practices**, **3 commands**, **2 templates**, an
**advisory anti-pattern hook** (`hooks.json` + `*.sh`), and a stdlib-only **calculator script**.
Dependencies are limited to `python3` + `jq` (already required repo-wide); no external services.

1. **developer-relations** — agents: `devrel-lead`, `developer-advocate`, `docs-and-dx-engineer`,
   `community-and-ecosystem-manager`. Calc: time-to-first-value, activation funnel, content ROI.
2. **higher-education-administration** — agents: `higher-ed-administration-lead`,
   `enrollment-and-financial-aid-strategist`, `student-success-and-retention-analyst`,
   `academic-operations-and-compliance-coordinator`. Calc: yield, net-tuition-revenue, retention.
3. **physical-therapy-practice** — agents: `pt-practice-lead`,
   `clinical-documentation-and-compliance-specialist`, `scheduling-and-patient-flow-analyst`,
   `billing-and-reimbursement-analyst`. Calc: 8-minute-rule units, visit utilization, no-show rate.
4. **investor-relations** — agents: IR lead, earnings/disclosure strategist, shareholder-targeting
   analyst, ESG/governance-comms coordinator. Calc: consensus dispersion, share-of-voice, ownership mix.
5. **mergers-acquisitions-advisory** — agents: corp-dev lead, valuation analyst, diligence lead,
   integration (PMI) manager. Calc: accretion/dilution, synergy phasing, deal IRR.
6. **content-marketing-seo** — agents: content strategy lead, SEO engineer, editorial-ops manager,
   content-performance analyst. Calc: topical-authority coverage, content decay, organic-traffic value.
7. **telecom-network-operations** — agents: network-ops lead, NOC/incident engineer, capacity/RF
   planner, OSS-BSS integration analyst. Calc: availability/MTTR, capacity headroom, churn-by-quality.
8. **utilities-operations** — agents: utility-ops lead, outage/reliability engineer (SAIDI/SAIFI),
   metering/AMI analyst, grid-planning coordinator. Calc: reliability indices, load factor, non-tech loss.
9. **optometry-eyecare-practice** — agents: eyecare-practice lead, clinical-exam/coding specialist,
   optical-retail/dispensing analyst, scheduling/recall analyst. Calc: capture rate, optical margin, recall yield.
10. **franchise-operations** — agents: franchise-system lead, franchise-development/sales analyst,
    unit-economics analyst, field-operations/compliance coordinator. Calc: unit economics, royalty
    yield, validation/AUV benchmarking.

## Prioritization rationale

- **P0 (scaffolded, parked — held pending real demand):** widest, most-repeated demand and the cleanest fit to the established
  template. DevRel is a top-requested tech function with no home; higher-ed and PT each extend a
  proven plugin family (school-admin, clinic-ops) into an obviously-missing adjacent role.
- **P1:** strong demand, slightly more specialized audience (IR, M&A, content/SEO).
- **P2:** valuable but narrower audience or heavier domain-knowledge surface (carrier networks,
  distribution utilities, optical retail, franchising) — best authored after the P0/P1 set proves
  the template extensions.

## Build status

- 🅿️ **Scaffolded & gated, then parked — NOT in the marketplace** (2026-06-11):
  `developer-relations`, `higher-education-administration`, `physical-therapy-practice` were built to
  gate-passing standard on the [`#409`](https://github.com/mcorbett51090/RavenClaude/pull/409) branch
  (4 agents + 3 skills + knowledge + hook + calc each, passing the frontmatter/JSON/layout/claims
  gates) but **deliberately not merged** — speculative, no real engagement. They are **not** registered
  in `marketplace.json` or `docs/architecture.md` on `main`. The scaffolded code lives on the closed
  `#409` branch and is recoverable in minutes the day a real engagement needs one.
- 📋 **Documented, not built:** candidates 4–10 above. Each has a roster + calc outline ready to
  scaffold from the same template when real demand appears.

Decision rationale: proof-of-craft + build-on-real-demand over catalog breadth (the marketplace is
already at 100 plugins). This doc is the durable **gap map** that turns "what's missing" into a fast
scaffold the moment a real DevRel / higher-ed / PT / IR / M&A / … engagement lands.
