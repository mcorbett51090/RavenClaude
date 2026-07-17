# New plugin candidates — research & prioritization (2026-07-17)

> **Scope of the run:** identify 10 RavenClaude plugins not yet implemented, prioritize by
> demand × feasibility, and build the highest-priority ones. This doc is the research +
> prioritization record; the built plugins land under `plugins/` in the same PR.

## Method

The marketplace already ships **166 plugins** (see [`architecture.md`](architecture.md) roster). To find
genuine gaps rather than near-duplicates, every candidate below was checked against the existing
`plugins/*/.claude-plugin/plugin.json` descriptions and the `plugins/` directory listing — all ten
return **zero** dedicated matches. Incidental mentions inside adjacent plugins (e.g. "dunning" inside
`fintech-payments-engineering`, "tax" inside `accounting-bookkeeping`, "home" inside
`senior-care-operations`) were confirmed to be passing references, not coverage, and the **seam** to the
nearest existing plugin is stated for each candidate.

Selection favored candidates that are (a) broadly demanded, (b) cleanly distinct from the nearest
existing plugin, and (c) either standards-anchored (low volatile-claim risk) or high-novelty engineering
gaps where the core framings are stable even as the tooling churns.

## The 10 candidates

| #  | Plugin | Purpose & value | Nearest existing (seam) | Demand | Feasibility |
|----|--------|-----------------|-------------------------|--------|-------------|
| 1  | **ai-agent-engineering** | The systems layer that builds production agentic/LLM-agent systems: agent topology (single-agent ReAct, planner/executor, multi-agent, workflow/graph), tool/function-call contract design, memory & context strategy, guardrails, retries/timeouts/idempotency, cost & latency budgets, tracing/observability, and the agent-eval harness. | `ai-rag-engineering` (retrieval), `prompt-engineering` (the prompt craft), `llm-evaluation-engineering` (eval methodology) → ai-agent-engineering *composes* prompts, retrieval, tools, and evals into a running agent. | **Very high** — the single hottest developer topic in 2026; no dedicated coverage. | High — core framings (topologies, tool contracts, guardrails, eval loops) are stable; volatile framework/pricing specifics carry a retrieval date. |
| 2  | **home-health-care-operations** | Home-health / home-care agency operations: skilled home health (Medicare, OASIS, PDGM, plan of care, physician certification) + private-duty/non-medical care, intake & eligibility, scheduling & EVV (Cures Act), caregiver staffing, billing/RCM, and survey/CoP readiness + quality (HHCAHPS, VBP, Star ratings). | `hospice-referral-sales` (end-of-life referral), `senior-care-operations` (facility-based), `medical-revenue-cycle` (hospital/physician RCM) → home-health owns care delivered *in the home* and the agency that delivers it. | **High** — large, fast-growing, underserved SMB vertical. | High — established ops shape; volatile CMS/PDGM/OASIS/EVV specifics carry a retrieval date. |
| 3  | **tax-preparation-practice** | A CPA/EA tax-preparation & planning practice: individual (1040) and business (1120/1120-S/1065) returns, seasonal busy-season workflow, organizers & engagement letters, prep→review→e-file pipeline, extensions & estimates, IRS/state notice response & representation, and light planning (entity/QBI/timing). | `accounting-bookkeeping` (write-up/close), `wealth-management-ria` (investment advisory), `finance` (corporate FP&A) → this owns *tax-return preparation* and the practice that produces it. Distinct from the never-built *corporate-tax-practice* (ASC 740 provision) candidate. | **High** — very large SMB professional-services vertical, sharply seasonal. | Medium-high — tax rules are volatile/jurisdictional; strict retrieval-date + verify-at-use + not-tax-advice discipline applied throughout. |
| 4  | **hoa-community-association-management** | Community-association management (HOAs, condo/COA, POA): board governance & fiduciary support, the annual budget & assessment, reserve studies & reserve funding, covenant/CC&R enforcement & architectural review, delinquency/lien collections, vendor & common-area maintenance, meetings/records, and developer transition. | `property-management` (rental/tenant/lease ops for a landlord), `residential-real-estate-brokerage` (buy/sell) → this owns the *common-interest community association* and its shared governance, not rental units. | **High** — ~30%+ of U.S. housing sits in a community association; large management-company market. | High — evergreen governance/financial mechanics; volatile state statute/lien/reserve specifics carry a retrieval date. |
| 5  | **subscription-billing-revenue** | The subscription billing & revenue *system*: plan/catalog model (flat/tiered/per-seat/usage/hybrid), proration & lifecycle, billing-platform selection (Stripe Billing/Chargebee/Zuora/Recurly/Metronome), webhooks & idempotency, dunning & failed-payment recovery, entitlements, usage metering/rating, and revenue recognition (ASC 606) + MRR/ARR reporting. | `pricing-monetization` (pricing *strategy*), `fintech-payments-engineering` (payment *rails*), `finance` (FP&A) → this owns the system that turns a price into a recurring invoice, a collection, and recognized revenue. | **High** — near-universal need for any recurring-revenue business. | High — the plumbing (catalog, proration, dunning, idempotency, rev-rec) is stable; volatile ASC 606/tax/provider-API specifics carry a retrieval date. |
| 6  | **landscaping-lawn-care-operations** | Landscape/lawn-care field business: recurring service contracts & route density, crew scheduling & productivity, seasonal (mow/fertilizer/snow) service mix, chemical-application licensing & records, estimating & job costing, equipment, and customer retention. | `field-service-management` (generic dispatch), `skilled-trades-contracting` (construction trades), `precision-agriculture` (large-farm agronomy) → a distinct route-density seasonal green-industry vertical. | Medium | High — well-bounded; reuses the field-service ops shape. |
| 7  | **pest-control-operations** | Pest-control field business: recurring service programs, route optimization, applicator licensing & pesticide-use records/compliance, IPM protocols, inspection/treatment documentation, and callback/warranty handling. | `field-service-management` (generic), `skilled-trades-contracting` → a distinct licensed-applicator recurring-service vertical with chemical-compliance depth. | Medium | High — well-bounded; volatile state pesticide-reg specifics carry a retrieval date. |
| 8  | **pet-grooming-boarding-daycare** | Pet-care services business (grooming, boarding, daycare, kennel): booking & capacity/kennel management, vaccination-record compliance, service packages & pricing, staff scheduling, incident/liability handling, and retention. | `veterinary-practice` (medical care) → this owns *non-medical pet services*, capacity, and boarding operations, not clinical care. | Medium | High — well-bounded SMB vertical. |
| 9  | **catering-operations** | Off-premise & event catering business: menu & package design, banquet event orders (BEOs), food-cost & recipe costing, event staffing & logistics, rentals, and kitchen production planning. | `restaurant-operations` (on-premise service), `event-management` (event planning/production) → this owns off-premise food production & delivery logistics. | Medium | High — reuses restaurant/ops cost mechanics. |
| 10 | **credit-union-operations** | Member-owned credit-union operations: field-of-membership growth, share/deposit & consumer-lending operations, member experience, NCUA regulatory & exam readiness, and CDFI/low-income-designation programs. | `fintech-payments-engineering` (rails/code), `regulatory-compliance` (AML/OFAC), `finance` (FP&A) → a distinct member-owned depository-institution business layer. | Medium | Medium — volatile NCUA/regulatory specifics need a dedicated research pass + heavy verify-at-use. |

## Prioritization rationale

**Build first (Tier 1 — this PR): #1–#5** (ai-agent-engineering, home-health-care-operations,
tax-preparation-practice, hoa-community-association-management, subscription-billing-revenue).

They score highest on the demand × feasibility product:

- **ai-agent-engineering** is the single hottest developer gap in the roster — production agent
  systems are what the market is building right now, and the marketplace covered retrieval (RAG),
  prompts, and eval methodology but had no plugin for *composing* them into a running agent.
- **home-health-care**, **tax-preparation**, and **hoa-community-association** are three large,
  underserved SMB/professional-services verticals, each cleanly distinct from its nearest neighbor
  (home-health vs hospice/senior-care; tax-prep-practice vs bookkeeping; HOA vs landlord property
  management). The healthcare and tax domains carry volatile regulatory content, handled with the
  repo's retrieval-date + verify-at-use + not-advice discipline.
- **subscription-billing-revenue** is a near-universal engineering need whose seam to the existing
  `pricing-monetization` (strategy) and `fintech-payments-engineering` (rails) plugins is crisp: it
  owns the billing *system* and revenue recognition, not the pricing or the payment rail.

**Tier 2 (#6–#10): scoped, not built this run.** The four field/SMB verticals (landscaping, pest
control, pet-care, catering) are well-bounded and cheap to add next by reusing the field-service /
restaurant ops shape; credit-union-operations carries heavier NCUA/regulatory content that warrants a
dedicated research pass to hit the repo's citation discipline. They are documented here so the next run
can pick them up without re-deriving the gap analysis.

## Implementation approach (per plugin)

Each Tier-1 plugin follows the established **2-agent** plugin shape (the `treasury-management` /
`serverless-engineering` template): a strategy/architecture agent + an execution/operations agent,
**3 skills**, a **2-doc knowledge bank** (a Mermaid decision tree + a dated 2026 patterns/reference
doc), and **2 templates**. Each agent carries the full scenario-authoring frontmatter schema
(`audience` / `works_with` / `scenarios` / `quickstart`) the `check-frontmatter.py` gate requires, an
explicit least-privilege `tools:` allowlist, and a `description` ≤ 300 chars. Every plugin
`requires ravenclaude-core@>=0.7.0`, is registered in `.claude-plugin/marketplace.json` and the
`docs/architecture.md` Status roster, is counted in the root `README.md` "ships **N plugins**" line, and
its paths already match the standard `plugins/*/…` globs in `.repo-layout.json`.

### Dependencies

No new runtime dependencies. The plugins are markdown + JSON manifests consumed by Claude Code's
built-in marketplace mechanism; the only build-time dependencies are the existing CI toolchain (`jq`,
`python3`, `pyyaml`, `prettier`, `ruff`) already present in the devcontainer. Volatile domain specifics
(CMS/PDGM/OASIS/EVV, IRS forms & thresholds, state HOA/condo statutes, ASC 606, LLM framework/pricing)
are treated as verify-at-use with a retrieval date rather than hard-coded facts.
