# New-plugin candidates & roadmap — 2026-06-13

> Research output for the "identify 10 new plugins" task. Surveys the current marketplace (~99 plugins), identifies 10 genuine gaps, prioritizes them, and outlines an implementation approach + dependencies for each. **#1 (`email-engineering`) is built in this same change**; the other 9 are scoped here as the build queue.
>
> _Author: `claude`. Method: enumerated the existing `plugins/` roster + `.claude-plugin/marketplace.json` to find non-overlapping gaps, weighted by demand (how often the capability is needed by the marketplace's engineer/consultant audience) and feasibility (clean seams to existing plugins, RFC/standards-grounded so the knowledge bank is durable)._

## How candidates were chosen

The marketplace is already broad: the full software-delivery chain, three clouds, app-craft layers (backend/frontend/mobile/database/api/auth), data & AI, the Microsoft stack, and ~50 business verticals. So a good candidate is **not** "another vertical" — it's a **named engineering or operational craft that recurs across many of those verticals and currently has no home**, with a clean seam to what exists (it *deepens*, never *duplicates*).

Each candidate below states the gap, why it's not already covered, the build approach, dependencies/seams, and a demand×feasibility score.

## Prioritization summary

| # | Candidate | Gap type | Demand | Feasibility | Priority | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | **email-engineering** | Eng craft | High | High | **P0** | ✅ **BUILT (this PR)** |
| 2 | **llm-application-security** | Eng craft | High | High | **P0** | Queued |
| 3 | **developer-experience-build-systems** | Eng craft | High | Med-High | **P1** | Queued |
| 4 | **graph-knowledge-engineering** | Eng craft | Med-High | High | **P1** | Queued |
| 5 | **chaos-resilience-engineering** | Eng craft | Med | High | **P1** | Queued |
| 6 | **geospatial-gis-engineering** | Eng craft | Med | Med | P2 | Queued |
| 7 | **computer-vision-engineering** | Eng craft | Med | Med | P2 | Queued |
| 8 | **developer-relations-devrel** | Ops craft | Med | High | P2 | Queued |
| 9 | **open-source-stewardship** | Ops craft | Med | High | P2 | Queued |
| 10 | **payroll-and-tax-operations** | Vertical | Med | Med | P2 | Queued |

**Build order rationale:** P0s are high-demand engineering crafts with RFC/standards-grounded knowledge (durable, low-maintenance) and clean seams. `email-engineering` went first because it's the most concrete and self-contained. `llm-application-security` is the strongest remaining 2026-demand gap (AI security is the year's dominant theme and only partially covered by `security-engineering` + `claude-app-engineering`). P1s are high-value crafts with slightly narrower audiences; P2s are valuable but either narrower (geospatial/CV) or further from the marketplace's engineer-first center (devrel/OSS/payroll).

---

## 1. email-engineering — ✅ BUILT (this PR)

The systems that put mail in the inbox: SPF/DKIM/DMARC alignment + rollout, deliverability/reputation/warm-up, ESP integration with idempotent webhooks, MJML templates, bounce/complaint suppression, one-click unsubscribe. See `plugins/email-engineering/`. Seams: `marketing-operations` (campaign), `backend-engineering` (infra), `api-engineering` (contract), the cloud plugins (DNS/SES), `security-engineering` (secrets/webhooks).

---

## 2. llm-application-security (P0)

**Gap.** AI red-teaming and LLM application security. `security-engineering` covers classic appsec; `claude-app-engineering` builds Claude apps; neither owns the **OWASP LLM Top 10** discipline (prompt injection, insecure output handling, training-data/RAG poisoning, excessive agency, system-prompt leakage, jailbreak testing, guardrail design). This is arguably 2026's highest-demand security gap.

**Build approach.** 3 agents: `llm-threat-modeler` (OWASP LLM Top 10 threat model, trust boundaries around tools/RAG), `prompt-injection-defense-engineer` (input/output handling, allow-listing tools, sandboxing, the "treat model output as untrusted" discipline), `llm-red-teamer` (jailbreak/eval harness, attack catalog, guardrail testing). Knowledge: OWASP LLM Top 10 decision tree, an attack-pattern catalog, a guardrail-selection tree, a dated 2026 tooling map. Script: a stdlib prompt-injection test-corpus runner. Hook: flags unsanitized model output flowing into a tool/eval/shell.

**Dependencies/seams.** `security-engineering` (verdicts), `claude-app-engineering` (the build surface — this secures it), `ai-rag-engineering` (RAG poisoning), `data-governance-privacy` (PII in prompts). Requires `ravenclaude-core@>=0.7.0`.

**Demand High / Feasibility High** — standards-grounded (OWASP), self-contained, the marketplace already ships the apps this would secure.

## 3. developer-experience-build-systems (P1)

**Gap.** Monorepo tooling and build performance: Nx/Turborepo/Bazel/pnpm workspaces, remote build caching, affected-graph test selection, codegen, local dev environment (devcontainers, Tilt). `platform-engineering-idp` covers the *platform/golden-path* layer and `devops-cicd` the *pipeline*, but neither owns the **build-system + monorepo + DX inner-loop** craft.

**Build approach.** 3 agents: `monorepo-architect` (workspace topology, dependency boundaries, Nx vs Turborepo vs Bazel decision), `build-performance-engineer` (caching, incremental/affected builds, cold-vs-warm CI), `dev-environment-engineer` (devcontainers, reproducible local setup, task runners). Knowledge: monorepo-tool decision tree, caching-strategy tree, dated 2026 tooling map. Script: a stdlib build-timing/affected-graph analyzer.

**Dependencies/seams.** `platform-engineering-idp` (golden paths), `devops-cicd` (the pipeline that runs the build), `frontend/backend-engineering` (the code it builds). High demand, slightly more volatile tooling (re-verify riders).

## 4. graph-knowledge-engineering (P1)

**Gap.** Graph databases and knowledge graphs: Neo4j/Cypher, property-graph modeling, graph algorithms (pathfinding, centrality, community), RDF/SPARQL, and **GraphRAG**. `database-engineering` is OLTP/relational; `ai-rag-engineering` is vector RAG; neither owns graph data modeling or graph-augmented retrieval.

**Build approach.** 2-3 agents: `graph-data-modeler` (property-graph vs RDF, when a graph beats relational, supernode/anti-patterns), `cypher-query-engineer` (Cypher/Gremlin/SPARQL, traversal performance, indexing), optional `graphrag-engineer` (knowledge-graph construction + graph-augmented retrieval). Knowledge: graph-vs-relational decision tree, modeling-pattern catalog, dated tooling map. Script: a stdlib Cypher/graph-shape linter.

**Dependencies/seams.** `database-engineering` (the relational seam — "when NOT a graph"), `ai-rag-engineering` (GraphRAG hands off here), `data-platform`. High feasibility (Cypher mechanics are stable).

## 5. chaos-resilience-engineering (P1)

**Gap.** Deliberate fault injection and resilience verification: hypothesis-driven chaos experiments, game days, failure-mode catalogs, steady-state metrics, blast-radius control. `observability-sre` defines SLOs and runs incidents *reactively*; this is the *proactive* "break it on purpose to prove it survives" craft.

**Build approach.** 2 agents: `chaos-experiment-designer` (hypothesis, steady-state definition, blast-radius limits, abort conditions), `resilience-test-engineer` (fault injection — latency/error/resource/zone-failure, game-day runbooks). Knowledge: chaos-experiment decision tree, failure-mode catalog (FMEA-style), dated tooling map (Litmus/Chaos Mesh/Gremlin/AWS FIS). Script: a stdlib experiment-plan/steady-state checker. Hook: flags a chaos experiment with no abort condition or blast-radius limit.

**Dependencies/seams.** `observability-sre` (steady-state metrics + the SLOs it verifies), `cloud-native-kubernetes` (where faults are injected), the cloud plugins (FIS). High feasibility, well-grounded (Principles of Chaos Engineering).

## 6. geospatial-gis-engineering (P2)

**Gap.** Spatial data and mapping: PostGIS, coordinate systems/projections (SRID, datum), spatial indexing (GiST, R-tree), tiling (vector tiles, MVT), routing/isochrones, and web mapping (Mapbox/MapLibre/Leaflet/deck.gl). No current plugin touches geospatial.

**Build approach.** 2 agents: `geospatial-data-engineer` (PostGIS modeling, projections, spatial joins/indexes), `mapping-application-engineer` (tiling, the map-rendering stack, large-dataset viz). Knowledge: projection/SRID decision tree, spatial-index tree, dated tooling map. Script: a stdlib GeoJSON/WKT validator + bbox/SRID sanity checker.

**Dependencies/seams.** `database-engineering` (PostGIS sits on Postgres), `frontend-engineering` (the map UI), `data-platform`. Medium demand (domain-specific), medium feasibility (broad surface).

## 7. computer-vision-engineering (P2)

**Gap.** Production computer vision: detection/segmentation/classification/OCR model selection, annotation pipelines + data quality, augmentation, edge/on-device deployment, and CV-specific evaluation (mAP, IoU). `ml-engineering` is general MLOps; CV has enough distinct craft (annotation, augmentation, edge inference, vision metrics) to warrant its own plugin.

**Build approach.** 2 agents: `cv-model-engineer` (task→architecture selection, transfer learning, the vision-metric that matters), `vision-data-pipeline-engineer` (annotation tooling, label quality, augmentation, dataset versioning). Knowledge: task→architecture decision tree, annotation-strategy tree, dated model/tooling map. Script: a stdlib annotation-format (COCO/YOLO) validator.

**Dependencies/seams.** `ml-engineering` (the MLOps lifecycle it specializes), `embedded-iot-engineering` (edge deployment), `data-platform`. Medium demand, medium feasibility (fast-moving models → strong re-verify riders).

## 8. developer-relations-devrel (P2)

**Gap.** Developer advocacy as an operational craft: developer-journey mapping, sample-app/quickstart strategy, DevRel metrics (activation, time-to-first-call), community management, technical content programs, and developer-feedback loops to product. `technical-writing-docs` writes the docs; `marketing-operations` runs campaigns; neither owns DevRel.

**Build approach.** 2 agents: `devrel-strategist` (developer journey, funnel/activation metrics, content portfolio), `community-and-advocacy-lead` (community programs, sample apps, feedback-to-product loop). Knowledge: developer-journey map, DevRel-metric tree, content-type decision tree. Templates: quickstart spec, DevRel metrics dashboard, community playbook.

**Dependencies/seams.** `technical-writing-docs` (docs), `api-engineering` (the dev portal/SDK it advocates), `product-management` (feedback loop), `marketing-operations`. High feasibility (no volatile API surface), medium demand.

## 9. open-source-stewardship (P2)

**Gap.** Running an OSS project well: licensing & compliance (license compatibility, SBOM, attribution), contributor experience (CONTRIBUTING, good-first-issues, triage), release management & changelogs, security disclosure (SECURITY.md, CVE/advisory process), governance, and sustainability/funding. Scattered hints exist but no owner.

**Build approach.** 2 agents: `oss-governance-advisor` (license compatibility, governance model, SBOM/attribution), `maintainer-experience-engineer` (contributor onboarding, triage automation, release/changelog discipline, security disclosure). Knowledge: license-compatibility decision tree, release-strategy tree, disclosure-process tree. Templates: CONTRIBUTING, SECURITY.md, release checklist, governance doc. Script: a stdlib license/SBOM compatibility checker.

**Dependencies/seams.** `security-engineering` (disclosure/advisories), `devops-cicd` (release automation), `technical-writing-docs` (contributor docs), `legal-ops-clm` (license interpretation boundary). High feasibility.

## 10. payroll-and-tax-operations (P2)

**Gap.** Payroll processing and employment tax: multi-state/multi-jurisdiction withholding, payroll tax filing (941/940, state), W-2/1099 issuance, garnishments, benefits/deduction handling, and payroll reconciliation. `people-operations-hr` covers HR; `accounting-bookkeeping` covers the books; `finance` covers FP&A; payroll-specific tax mechanics fall between them.

**Build approach.** 2 agents: `payroll-operations-specialist` (pay cycles, deductions, garnishments, reconciliation), `employment-tax-specialist` (multi-state withholding, filing calendar, year-end forms). Knowledge: withholding/nexus decision tree, filing-calendar reference, year-end-form tree. Templates: payroll register, reconciliation worksheet, year-end checklist. Heavy **`[verify-at-use]`** discipline (tax rules are jurisdiction- and year-specific and change annually).

**Dependencies/seams.** `people-operations-hr` (HR/employee data), `accounting-bookkeeping` (GL posting), `finance` (labor cost), `regulatory-compliance`. Medium demand, medium feasibility (high-maintenance knowledge bank — must carry strong dating discipline).

---

## Build queue note

Each queued plugin follows the marketplace plugin contract (AGENTS.md "Adding a new plugin"): `.claude-plugin/plugin.json` + `CLAUDE.md` + `README.md`, agents with the full scenario-authoring frontmatter schema (gated by `scripts/check-frontmatter.py`, ≤300-char descriptions), a Mermaid-tree knowledge bank with dated/cited entries, best-practices, templates, commands, a scenarios bank, a stdlib script where a runtime artifact adds value, and an advisory hook. Each appends to `.claude-plugin/marketplace.json` `plugins[]` (with a metadata version bump) and is verified against the full gate suite (`scripts/audit-gates.sh`, prettier, ruff, layout) before its PR. The existing `plugins/*/**` globs in `.repo-layout.json` already cover all of these paths, so no layout-allow-list change is required per plugin.
