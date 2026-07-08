# Plugin candidates — 2026-07-08 gap analysis (continuation)

> Second research pass of the recurring "10 new plugins" routine. The first pass
> ([`plugin-candidates-2026-07.md`](plugin-candidates-2026-07.md), 2026-07-05) built
> `graphql-engineering` (now merged to `main`) and left a roadmap of nine more.
> This pass re-runs the gap analysis against the **now-larger** roster (140 plugins),
> surfaces two **higher-demand engineering gaps the first pass missed**, folds the
> first pass's un-built roadmap items forward, and **builds the two new P0 gaps**
> in this change set.
>
> _Method: enumerated all `plugins/<p>/` directories, confirmed each candidate is
> not already a dedicated plugin, and assigned the seams that keep it disjoint from
> its neighbors. Demand reads are engineering judgment `[estimate]`, not measured stats._

## What changed since the first pass

- **Built & merged:** `graphql-engineering` (the first pass's P0).
- **Still open from the first pass's roadmap:** chaos-engineering-resilience,
  serverless-engineering, technical-seo, ux-research, prompt-engineering-evaluation,
  design-systems-engineering, feature-flags-progressive-delivery, payroll-operations,
  pharmacovigilance-drug-safety — none of these have been built yet.
- **New this pass:** two engineering layers with **higher demand and cleaner seams**
  than most of the open roadmap — the *data-trust* layer and the *event-collection*
  layer — neither of which the first pass identified. These become the new P0s.
- **Landed in parallel (PR #573), while this pass was in flight:** `franchise-operations`
  (candidate #10 below), plus `llm-evaluation-engineering` and `chiropractic-practice`.
  Candidate #10 is therefore **already built on `main`** — kept in the table below for
  the record, but treat it as done, not open. The marketplace is now 144 plugins after
  this change (142 on `main` + the two P0s here).

## The 10 candidates (this pass)

Priority = **demand × feasibility**. The two P0s are new; the rest carry forward the
first pass's roadmap (with two vertical adds) so this document is a single current backlog.

| # | Plugin | Gap it fills | Demand `[est]` | Feasibility | Priority |
|---|---|---|---|---|---|
| 1 | **data-quality-observability** | "Is the data correct/fresh/complete & trustworthy?" — contracts, tests, freshness/volume/schema/distribution monitors, data-incident response. No owner today. | High | High | **P0 — built** |
| 2 | **martech-event-instrumentation** | The event-collection / CDP layer — tracking plan, event taxonomy, identity model, CDP & collection architecture, consent-by-design, reverse ETL. No owner today. | High | High | **P0 — built** |
| 3 | **chaos-engineering-resilience** | Fault injection, game days, resilience proofs; complements `observability-sre` (provoke vs observe). | High | High | P1 |
| 4 | **technical-seo-engineering** | Crawlability, indexation, structured data, render-for-search, migration SEO; only touched inside `web-design`. | Med-High | High | P1 |
| 5 | **headless-cms-engineering** | Composable/headless content platforms (Contentful/Sanity/Strapi/Payload) — distinct from the `wordpress-cms-engineering` monolith. | Med-High | High | P1 |
| 6 | **serverless-engineering** | Cross-cloud serverless patterns (FaaS, event-driven, cold starts) — the cloud plugins are provider-specific. | High | High | P2 |
| 7 | **feature-flags-progressive-delivery** | Flag lifecycle, canary/ring rollout, kill-switches, flag debt; `devops-cicd` ships releases but not flag governance. | Med | High | P2 |
| 8 | **self-storage-operations** | High-margin SMB vertical (unit-mix, dynamic pricing/ECRI, delinquency & lien, ancillary revenue). No sibling. | Med (vertical) | High | P2 |
| 9 | **hoa-community-association-management** | HOA/condo association management (governance, reserves, assessments, CC&R enforcement). No sibling. | Med (vertical) | High | P3 |
| 10 | **franchise-operations** | Franchisor/multi-unit-franchisee operations (unit economics, brand-standard audits, royalties/FDD literacy). No sibling. | Med (vertical) | High | P3 |

**Deferred (first-pass roadmap, still valid, lower this pass):** ux-research,
prompt-engineering-evaluation, design-systems-engineering, payroll-operations (PII-heavy,
jurisdictional), pharmacovigilance-drug-safety (regulated). See the first-pass doc for
their agent shapes and disclaimers.

## Prioritization rationale

- **Why the two new P0s outrank the open roadmap.** `data-quality-observability` and
  `martech-event-instrumentation` each own a layer that *every* data/product org already
  operates but that no plugin covers, and each has a **razor-clean seam** to its neighbors
  (data-trust sits beside data-platform/analytics-engineering/data-orchestration; the
  event-collection layer sits beneath analytics-engineering/experimentation/marketing).
  High demand, no legal/medical/dual-use sensitivity, and the content is authorable to the
  cited/`verify-at-use` bar. That combination beats chaos/serverless (a little cloud-plugin
  overlap) and the regulated verticals.
- **P1** are the highest-value carry-forwards: chaos (clean SRE complement), technical-SEO
  (real engineering surface web-design only grazes), headless-CMS (mainstream composable-content
  architecture distinct from WordPress).
- **P2/P3** trade a bit of feasibility (serverless↔cloud overlap) or per-plugin demand
  (verticals) for breadth; each still has a clean boundary.

## Implementation approach & dependencies (per candidate)

Every plugin follows the house 2-agent template (confirmed against `data-orchestration`):
`2 agents · 3 skills · 2 knowledge files (a Mermaid decision tree + a dated 2026 reference)
· 2 templates · CLAUDE.md (11 sections) · README.md · .claude-plugin/plugin.json`, registered
in `.claude-plugin/marketplace.json` and the `docs/architecture.md` Status table, requiring
`ravenclaude-core@>=0.7.0`. Only the plugin-specific shape is called out.

1. **data-quality-observability** — *built this change.* Agents: `data-quality-architect`
   (approach & tooling choice — contracts vs tests vs monitors; dbt tests / Great Expectations
   / Soda / Elementary / managed observability), `data-quality-engineer` (implement checks &
   monitors, wire into CI/orchestration, run data-incident response). Trees: tooling selection ·
   where checks run (in-transform / post-load gate / independent monitor). Seams →
   data-platform, analytics-engineering, data-orchestration, data-governance-privacy.
2. **martech-event-instrumentation** — *built this change.* Agents: `event-taxonomy-architect`
   (tracking plan, taxonomy, identity model, CDP & collection-architecture choice),
   `instrumentation-engineer` (SDK/server-side tracking, typed/schema-validated events in CI,
   consent wiring, destinations/reverse ETL, stream QA). Trees: CDP/collection selection ·
   client vs server vs hybrid. Seams → marketing-operations, analytics-engineering,
   experimentation-growth-engineering, data-governance-privacy, data-platform.
3. **chaos-engineering-resilience** — Agents: `resilience-architect`, `chaos-experiment-engineer`.
   Hard seam to `observability-sre` (no chaos without steady-state signals). Tooling
   (Gremlin/AWS FIS/LitmusChaos/Chaos Mesh) `verify-at-use`.
4. **technical-seo-engineering** — Agents: `technical-seo-architect`, `seo-implementation-engineer`.
   Boundary: NOT general web build → `web-design`; NOT paid/demand-gen → `marketing-operations`.
   Ranking-signal specifics `verify-at-use`.
5. **headless-cms-engineering** — Agents: `content-architecture-strategist`,
   `headless-cms-implementation-engineer`. Boundary: NOT the WordPress monolith →
   `wordpress-cms-engineering`; rendering → `frontend-engineering`.
6. **serverless-engineering** — Agents: `serverless-architect`, `serverless-function-engineer`.
   Cross-cloud *patterns*; provider IaC → the cloud plugins.
7. **feature-flags-progressive-delivery** — Agents: `progressive-delivery-architect`,
   `feature-flag-engineer`. Boundary: pipeline → `devops-cicd`; A/B stats →
   `experimentation-growth-engineering`.
8. **self-storage-operations** — Agents: `storage-operations-lead`,
   `revenue-and-occupancy-analyst`. Lien/auction law state-specific → dated + `verify-at-use`;
   not legal advice. Seams → property-management, commercial-real-estate, finance.
9. **hoa-community-association-management** — Agents: `association-manager-lead`,
   `reserves-and-assessments-analyst`. CC&R/state statutes jurisdictional → dated; not legal
   advice. Seams → property-management, finance, legal-small-firm.
10. **franchise-operations** — Agents: `franchise-operations-lead`, `unit-economics-analyst`.
    FDD/Item 19 references dated; not legal/financial advice. Seams → restaurant-operations,
    retail-store-operations, finance.

## Build progress (this change)

| Plugin | Status |
|---|---|
| data-quality-observability | **Built** — 2 agents, 3 skills, 2 knowledge files, 2 templates, CLAUDE.md/README/plugin.json; registered in marketplace.json + architecture.md; gates run locally. |
| martech-event-instrumentation | **Built** — same anatomy; registered + gated. |
| candidates 3–10 | Specified above (+ the first-pass roadmap) as an implementation-ready backlog. |

**Why two built, not ten:** each plugin is a dozen-plus files that must pass strict CI
gates (frontmatter scenario-schema, roster/count claims, whole-tree prettier, the gate-audit
meta-test) and hold the cited/`verify-at-use` quality bar. Two production-quality plugins plus
a current backlog is the higher-value, lower-risk deliverable for one unattended pass; the
backlog makes builds 3–10 mechanical follow-ups.

---

_Last reviewed: 2026-07-08 by `claude`. Continues [`plugin-candidates-2026-07.md`](plugin-candidates-2026-07.md)._
