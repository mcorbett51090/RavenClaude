# Plugin candidates — 10 gaps vs. the current roster (2026-07-07)

> Research write-up for the "identify 10 new plugins" routine. Method: enumerated the current
> plugin roster (`ls plugins/` → **139** plugins as of this date), mapped it against common
> Claude Code use-cases / integrations / feature requests, and isolated domains with **genuine
> demand** that no existing plugin owns. Each candidate names the closest existing plugin(s) and
> the **seam** that keeps it distinct (the marketplace's house rule: a new plugin must not
> duplicate an existing one — it must own a distinct decision surface).
>
> This doc is planning content under `docs/` (commits straight to `main` per AGENTS.md), included
> here in the build branch so the candidates and the initial buildout land together.

## How these were prioritized

Two axes, each scored 1–5, `demand × feasibility` = priority score:

- **Demand** — how often the use-case shows up (developer surveys, the shape of existing
  engineering plugins, vertical-SaaS market size, "is this a job a team runs every week?").
- **Feasibility** — how cleanly it fits the established plugin pattern (2–4 agents, 3–5 skills,
  a decision-tree knowledge bank, best-practices) **without** needing live integrations,
  secrets, or MCP servers this marketplace doesn't ship. High feasibility = pure
  markdown/knowledge, no runtime deps.

Everything here is **advisory decision-support** built on the `ravenclaude-core` constitution —
no plugin needs network access, credentials, or an MCP server to deliver its value, which is why
feasibility is uniformly high. Volatile facts (pricing, regulatory thresholds, payer rules) carry
retrieval dates + `verify-at-use` markers, per the marketplace's accuracy discipline.

## The 10 candidates

| # | Candidate | Category | Closest existing → the seam | Demand | Feas. | Score | Tier |
|---|---|---|---|---|---|---|---|
| 1 | **llm-evaluation-engineering** | AI/ML eng | `ai-rag-engineering` (retrieval), `ai-coding-model-guidance` (model pick), `ml-engineering` (classical training), `experimentation-growth-engineering` (product A/B) → **none owns offline+online LLM eval, LLM-as-judge, guardrails, regression gates** | 5 | 5 | 25 | **P0 — built** |
| 2 | **chiropractic-practice** | Healthcare vertical | `physical-therapy-rehab-clinic`, `dental-practice`, `optometry-eyecare-practice` → **distinct DC scope, subluxation/CMT coding, active-vs-maintenance-care ABN, cash/wellness-plan model** | 4 | 5 | 20 | **P0 — built** |
| 3 | **franchise-operations** | Business ops | `restaurant-operations`, `retail-store-operations`, `field-service-management` → **franchisor↔franchisee system: FDD/Item-19, royalty & ad-fund, multi-unit P&L, brand-standard audits, unit economics for a new-unit decision** | 4 | 5 | 20 | **P0 — built** |
| 4 | **prompt-engineering** | AI/ML eng | `ai-coding-model-guidance`, `ai-rag-engineering`, candidate #1 → **prompt design/versioning/optimization as a craft: structured prompting, few-shot vs fine-tune, prompt regression, token/cost shaping** | 4 | 5 | 20 | P1 |
| 5 | **technical-seo-engineering** | Web eng | `web-design`, `search-relevance-engineering` (internal search), `marketing-operations`, `frontend-engineering` → **crawlability, Core Web Vitals for ranking, structured data/schema.org, SERP/index coverage, JS-render SEO** | 4 | 5 | 20 | P1 |
| 6 | **grant-management-nonprofit** | Nonprofit ops | `nonprofit-fundraising` (pre-award/donors), `regulatory-compliance` → **post-award federal grant admin: OMB Uniform Guidance (2 CFR 200), allowability, indirect-cost/de-minimis, time-and-effort, subrecipient monitoring, SF-425/closeout** | 3 | 5 | 15 | P1 |
| 7 | **funeral-home-deathcare-operations** | Vertical ops | `senior-care-operations`, `hospice-referral-sales` → **at-need & pre-need arrangements, FTC Funeral Rule/GPL, merchandise & service P&L, preneed trust/insurance, families-in-grief service model** | 3 | 4 | 12 | P2 |
| 8 | **bioinformatics-engineering** | Sci/eng | `clinical-trials`, `data-platform`, `ml-engineering` → **genomics/NGS pipelines: reference & variant calling, workflow managers (Nextflow/Snakemake/WDL), FAIR data, reproducibility & provenance** | 3 | 4 | 12 | P2 |
| 9 | **catering-events-operations** | Vertical ops | `restaurant-operations`, `event-management`, `hotel-hospitality-operations` → **off-premise catering: BEO, per-head food-cost & labor for events, proposal-to-contract, rentals/staffing logistics, event-day timeline** | 3 | 4 | 12 | P2 |
| 10 | **utilities-water-wastewater-operations** | Infrastructure | `renewable-energy`, `field-service-management`, `esg-sustainability-reporting`, `public-sector-govtech` → **regulated water/wastewater utility: SDWA/NPDES compliance, rate case & cost-of-service, asset management/CIP, non-revenue-water, SCADA ops** | 3 | 3 | 9 | P2 |

**Prioritization rationale.** The three P0s maximize `demand × feasibility` **and** span the three
audiences this marketplace serves (an **engineering** team, a **healthcare** practice, a
**multi-unit business**), so the initial buildout demonstrates breadth rather than three variants
of one thing. #1 is the single highest-demand gap — LLM evaluation is now table-stakes for any team
shipping AI features and nothing in the roster owns it. #2 and #3 are the cleanest vertical/business
gaps: each has a large operator population and a decision surface (clinical-coding scope; the
franchisor↔franchisee economic contract) that no neighbor covers. P1s are strong, near-ready
follow-ons; P2s are real but either narrower in audience (#7, #10) or need more specialized knowledge
banks (#8) that warrant their own build pass.

## Per-candidate implementation approach & dependencies

Common pattern (all 10): `ravenclaude-core@>=0.7.0` dependency; 2 agents (a strategy/operations lead
+ a specialist), 3 skills, one decision-tree knowledge bank (Mermaid tree + a dated reference), 5
best-practices, README + CLAUDE constitution. **No runtime dependencies** beyond `jq`/`python3`
(already required by CI). No MCP servers, no secrets, no network.

1. **llm-evaluation-engineering** — agents `eval-strategy-lead` (what to measure, eval design,
   online/offline split, ship-gate) + `eval-harness-engineer` (dataset curation, LLM-as-judge rubric
   design + bias controls, CI regression harness, guardrails/red-team). Knowledge: an
   eval-method decision tree (rule-based vs model-graded vs human) + a dated 2026 tooling/method map.
2. **chiropractic-practice** — agents `chiropractic-practice-lead` (throughput, care plans,
   cash/wellness-plan model, retention) + `chiro-billing-compliance-specialist` (CMT/E&M coding,
   medical necessity & active-vs-maintenance, ABN, documentation). Knowledge: a
   billing-and-medical-necessity decision tree + a dated payer/coding reference.
3. **franchise-operations** — agents `franchise-operations-strategist` (FDD/Item-19 literacy,
   royalty/ad-fund economics, new-unit go/no-go, franchisor↔franchisee relationship) +
   `multi-unit-performance-manager` (multi-unit P&L, brand-standard audits, labor/COGS, manager
   scorecards). Knowledge: a new-unit/expand decision tree + a dated franchise-economics reference.
4. **prompt-engineering** — reuse #1's harness seam; agents for prompt design + prompt-optimization/
   regression. Depends on nothing new.
5. **technical-seo-engineering** — agents for SEO architecture + technical-crawl/CWV. Knowledge:
   a render-strategy (SSR/SSG/CSR) × crawlability tree + a dated ranking-signal reference.
6. **grant-management-nonprofit** — agents for award administration + compliance/audit (Uniform
   Guidance). Knowledge: an allowability/allocability decision tree + a dated 2 CFR 200 reference.
7. **funeral-home-deathcare-operations** — agents for arrangement/operations + Funeral-Rule
   compliance & preneed. Knowledge: an at-need-vs-preneed tree + a dated FTC-Rule/GPL reference.
8. **bioinformatics-engineering** — agents for pipeline architecture + reproducibility/data
   management. Knowledge: a workflow-manager selection tree + a dated tool/reference-genome map.
9. **catering-events-operations** — agents for sales/proposal + event-ops/BEO. Knowledge: a
   staffing-and-food-cost model tree + a dated benchmark reference.
10. **utilities-water-wastewater-operations** — agents for regulatory/compliance + asset/rate
    operations. Knowledge: a compliance-and-CIP-priority tree + a dated SDWA/NPDES reference.

## Build status (this routine)

- **Built & wired** (this PR): #1 `llm-evaluation-engineering`, #2 `chiropractic-practice`,
  #3 `franchise-operations` — each with 2 agents, 3 skills, a decision-tree knowledge bank, and
  5 best-practices, added to `marketplace.json` + `docs/architecture.md`.
- **Identified & specced** (follow-on passes): #4–#10 above, ready to build against the same
  pattern.

No blockers encountered. The three P0 plugins pass the local gate suite
(`check-frontmatter.py`, `check-md-links.py`, `check-marketplace-claims.py --structural-only`,
prettier, `audit-gates.sh`).
