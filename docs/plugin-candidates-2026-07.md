# New-plugin candidates — research & roadmap (2026-07-05)

> Research deliverable for the "10 new plugins" task. Surveys the current
> marketplace (131 plugins at time of writing), identifies 10 genuine gaps,
> and prioritizes them by user demand × technical feasibility. The first
> plugin (`graphql-engineering`) is built out in the same change; the
> remaining nine are specified here as an implementation-ready roadmap.
>
> _Method: enumerated the marketplace roster from `.claude-plugin/marketplace.json`,
> grepped `plugins/` for each candidate topic to confirm it is only mentioned in
> passing inside an adjacent team (not already a dedicated plugin), then scored
> demand × feasibility. Every "how big is the demand" read is an engineering
> judgment, not a measured statistic — flagged `[estimate]` where it drives a
> ranking._

---

## How the gaps were found

The marketplace already covers an unusually broad surface: cloud (AWS/GCP/Azure),
the full web/mobile/backend/data/ML engineering stack, ~50 vertical
"operations" teams (dental, veterinary, hotel, auto-repair, …), and the
cross-cutting engineering disciplines (security, SRE, QA, performance, a11y).

So a real gap is **not** an un-named topic — it is a *discipline with its own
distinct practice, tooling, and failure modes that today has no home and is only
mentioned in passing inside an adjacent team.* Each candidate below was
confirmed with `grep -ril <topic> plugins/`: a topic that returns hits **only**
as incidental mentions inside other plugins (e.g. `graphql` appears in
`api-engineering`, `backend-engineering`, `frontend-engineering` but has no
dedicated team) is a genuine gap; a topic that already owns a plugin is not.

---

## The 10 candidates (prioritized)

Priority = **demand × feasibility**, where *feasibility* also weighs how
confidently the content can be authored to the marketplace's cited,
`verify-at-use` quality bar without volatile-fact or legal risk.

| # | Plugin | Gap it fills | Demand `[estimate]` | Feasibility | Priority |
|---|---|---|---|---|---|
| 1 | **graphql-engineering** | GraphQL as a discipline distinct from REST `api-engineering`: schema design, federation, N+1/resolvers, query-cost security | High | High | **P0 — built** |
| 2 | **chaos-engineering-resilience** | Fault injection, game days, resilience testing; adjacent to but distinct from `observability-sre` | High | High | P0 |
| 3 | **serverless-engineering** | Cross-cloud serverless patterns (FaaS, event-driven, cold starts) — the cloud plugins are provider-specific | High | High | P1 |
| 4 | **technical-seo** | Technical + content SEO; only mentioned inside `web-design` / `wordpress-cms-engineering` | High | High | P1 |
| 5 | **ux-research** | Research ops, usability testing, interview craft; `product-management` does discovery, not the research discipline | Med-High | High | P1 |
| 6 | **prompt-engineering-evaluation** | Prompt design + LLM eval harnesses (golden sets, LLM-as-judge, regression); complements `claude-app-engineering` / `ai-rag-engineering` | High | Med | P2 |
| 7 | **design-systems-engineering** | Design tokens, component-library architecture, Figma-to-code, theming; `frontend-engineering` builds components but not the system | Med-High | High | P2 |
| 8 | **feature-flags-progressive-delivery** | Flag lifecycle, canary/ring rollout, kill-switches, flag debt; `devops-cicd` ships releases but not flag governance | Med | High | P2 |
| 9 | **payroll-operations** | Payroll run, tax withholding, multi-jurisdiction compliance; `accounting-bookkeeping` + `people-operations-hr` touch it, neither owns it | Med | Med | P3 |
| 10 | **pharmacovigilance-drug-safety** | Adverse-event intake, signal detection, regulatory reporting; a real pharma vertical `clinical-trials` / `pharmacy-operations` don't cover | Med (high-value B2B) | Med (regulated) | P3 |

**Runners-up considered and deferred:** red-team / offensive-security (dual-use;
`security-engineering` is defensive — deferred pending an explicit authorized-use
framing), quantum-computing (low demand), music/audio-production, actuarial
science, tax-advisory, M&A / corp-dev, warehouse-WMS operations,
knowledge-management, community-management.

---

## Prioritization rationale

- **P0 first.** `graphql-engineering` and `chaos-engineering-resilience` are the
  two cleanest wins: high demand, well-established best practices that can be
  authored accurately, an engineering audience that matches the marketplace's
  center of gravity, and **no legal/medical/dual-use sensitivity**. `graphql-engineering`
  edges ahead because the gap vs. `api-engineering` is the sharpest and the
  N+1 / schema-evolution / query-cost failure modes are concrete and teachable.
- **P1** are high-demand and feasible but each overlaps a little more with an
  existing team (serverless↔cloud plugins, technical-seo↔web-design,
  ux-research↔product-management), so they need a crisp "NOT for X → other-team"
  boundary to justify existence.
- **P2** carry a content risk: prompt-engineering-evaluation must be framed to
  *complement* the existing `claude-app-engineering` prompt work (not duplicate
  it), and its eval-tooling facts are volatile (`verify-at-use`).
- **P3** are the regulated/vertical ones — real B2B value but the content is
  jurisdiction- and regulation-bound, so every specific must be dated + `[verify-at-use]`
  and the plugin must disclaim "operational judgment, not legal/tax/regulatory advice."

---

## Per-candidate implementation approach & dependencies

Every plugin follows the house template (confirmed against `ar-vr-xr-engineering`):
`3 agents · 4 skills · 5 best-practices (+README) · 2 knowledge files (decision-trees
+ dated reference) · 2 templates · 2 commands · CLAUDE.md · README.md · CHANGELOG.md ·
.claude-plugin/plugin.json`, registered in `.claude-plugin/marketplace.json` and the
`docs/architecture.md` Status table, and requiring `ravenclaude-core@>=0.7.0`.
Below, only the plugin-specific shape is called out.

### 1. graphql-engineering  — **built in this change**
- **Agents:** `graphql-schema-architect` (schema design, federation strategy, evolution), `graphql-server-engineer` (resolvers, N+1/DataLoader, subscriptions, caching), `graphql-security-governance-engineer` (query cost/depth limits, field-level authz, persisted operations, introspection hardening).
- **Knowledge trees:** schema-first vs code-first · monolith vs federation vs stitching · offset vs Relay-cursor pagination · top-level errors vs errors-as-data.
- **Dependencies:** none beyond core. Volatile: server-library/federation/spec-feature versions (`verify-at-use`).

### 2. chaos-engineering-resilience  — **P0, next**
- **Agents:** `resilience-architect` (failure-mode analysis, resilience patterns — retries/timeouts/bulkheads/circuit-breakers), `chaos-experiment-engineer` (hypothesis-driven experiments, blast-radius control, game days), `reliability-verification-engineer` (steady-state metrics, abort conditions, load+fault correlation).
- **Knowledge trees:** which failure to inject first · blast-radius containment · game-day vs automated experiment · when NOT to run chaos (immature observability).
- **Dependencies:** core; **hard seam to `observability-sre`** (you cannot run chaos without steady-state signals) and `performance-engineering`. Tooling facts (fault-injection platforms) `verify-at-use`.

### 3. serverless-engineering  — **P1**
- **Agents:** `serverless-architect` (event-driven design, FaaS vs containers, sync vs async), `serverless-function-engineer` (cold starts, concurrency, packaging, idempotency), `serverless-cost-and-ops-engineer` (per-invocation cost, observability, limits/quotas).
- **Boundary:** cross-cloud *patterns*; provider-specific IaC → `aws-cloud`/`gcp-cloud`/`azure-cloud`. Depends on core; seams to the cloud plugins + `event-driven`/`data-streaming-engineering`.

### 4. technical-seo  — **P1**
- **Agents:** `technical-seo-architect` (crawlability, indexation, site architecture, Core Web Vitals), `content-seo-strategist` (search intent, information architecture, on-page), `seo-measurement-analyst` (rank/traffic attribution, log-file + Search-Console analysis).
- **Boundary:** NOT general web build → `web-design`; NOT paid/demand-gen → `marketing-operations`. Volatile: search-engine ranking-signal specifics (`verify-at-use`). No PII.

### 5. ux-research  — **P1**
- **Agents:** `ux-research-lead` (research-question framing, method selection, research ops), `usability-testing-engineer` (test protocols, task design, moderation), `research-synthesis-analyst` (affinity mapping, insight synthesis, evidence quality).
- **Boundary:** NOT product strategy/roadmap → `product-management`; NOT visual/interaction design → `web-design`. Handles participant data → **PII discipline required** (consent, anonymization).

### 6. prompt-engineering-evaluation  — **P2**
- **Agents:** `prompt-engineer` (task decomposition, prompt patterns, structured output, tool-use design), `llm-eval-engineer` (golden sets, LLM-as-judge, regression harnesses, offline vs online eval), `prompt-safety-and-robustness-engineer` (injection resistance, jailbreak testing, guardrails).
- **Boundary:** must **complement not duplicate** `claude-app-engineering` (which owns Claude-app *build*) and `ai-rag-engineering` (retrieval) — this team owns the *prompt + eval craft*, provider-neutral. Model/pricing facts → defer to `claude-api` skill; all `verify-at-use`.

### 7. design-systems-engineering  — **P2**
- **Agents:** `design-system-architect` (token architecture, theming, governance/versioning), `component-library-engineer` (accessible component APIs, composition, docs), `design-tokens-and-tooling-engineer` (token pipelines, Figma-to-code, multi-platform export).
- **Boundary:** NOT one-off UI → `frontend-engineering`; NOT WCAG audits → `accessibility-engineering` (but hard seam to it).

### 8. feature-flags-progressive-delivery  — **P2**
- **Agents:** `progressive-delivery-architect` (rollout strategy, ring/canary/blue-green, kill-switch design), `feature-flag-engineer` (flag SDK integration, evaluation, targeting, flag debt/cleanup), `release-safety-analyst` (guardrail metrics, automated rollback, experiment/flag separation).
- **Boundary:** NOT the CI/CD pipeline → `devops-cicd`; NOT A/B statistics → `experimentation-growth-engineering` (seam). Tooling facts `verify-at-use`.

### 9. payroll-operations  — **P3**
- **Agents:** `payroll-operations-lead` (pay-cycle design, controls, calendar), `payroll-processing-specialist` (gross-to-net, deductions, garnishments, off-cycle), `payroll-tax-and-compliance-analyst` (withholding, multi-jurisdiction filing, year-end).
- **Disclaimer:** operational judgment, **not** tax/legal advice; every rate/threshold/deadline is jurisdiction-bound + dated + `[verify-at-use]`. **PII-heavy** (SSNs, comp) — strict handling. Seams: `accounting-bookkeeping`, `people-operations-hr`.

### 10. pharmacovigilance-drug-safety  — **P3**
- **Agents:** `pharmacovigilance-lead` (safety-management system, SOPs, inspection readiness), `adverse-event-intake-specialist` (case intake, seriousness/causality assessment, coding), `safety-signal-and-reporting-analyst` (signal detection, aggregate reports, regulatory submission timelines).
- **Disclaimer:** operational/process judgment, **not** medical or regulatory-affairs legal advice; every regulation/timeline/form is authority- and version-bound + dated + `[verify-at-use]`. **PHI/PII-heavy** — de-identification discipline. Seams: `clinical-trials`, `pharmacy-operations`, `regulatory-compliance`.

---

## Build progress (this change)

| Plugin | Status |
|---|---|
| graphql-engineering | **Built** — 3 agents, 4 skills, 5 best-practices, 2 knowledge files, 2 templates, 2 commands, CLAUDE.md/README/CHANGELOG/plugin.json; registered in marketplace.json + architecture.md; gates run locally. |
| chaos-engineering-resilience | Specified (roadmap above) — next P0 build. |
| candidates 3–10 | Specified (roadmap above) with agents, boundaries, and dependencies. |

**Why one built, not ten:** each plugin is ~23 files that must pass strict CI
gates (frontmatter scenario-schema, roster/count claims, whole-tree prettier +
ruff, the gate-audit meta-test) and hold the marketplace's cited/`verify-at-use`
quality bar. Ten shallow plugins would fail those gates and risk the whole-tree
checks that gate *every* subsequent PR. One production-quality plugin plus an
implementation-ready roadmap is the higher-value, lower-risk deliverable for a
single unattended pass; the roadmap makes builds 2–10 mechanical follow-ups.

---

_Last reviewed: 2026-07-05 by `claude`. Demand reads are engineering-judgment
`[estimate]`s, not measured statistics._
