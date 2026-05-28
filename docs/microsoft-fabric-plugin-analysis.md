# Microsoft Fabric — most-useful-next-addition analysis + buildout plan

**Date:** 2026-05-28
**Author:** Autonomous repo-analysis pass (Claude Opus 4.7, overnight)
**Status:** Decision + research synthesis + buildout plan. §7 carries the expert review + gap analysis + score; §8 is the plan as revised by that review. The execution-sequenced build plan lives in [`microsoft-fabric-build-plan.md`](microsoft-fabric-build-plan.md).
**Grounding:** every Fabric claim below is grounded in official Microsoft Learn documentation retrieved 2026-05-28 via the Microsoft Learn MCP server. Source URLs are inline.

---

## 0. TL;DR

The single most useful next addition to the marketplace is a new **`microsoft-fabric`** plugin — a Microsoft Fabric specialist team (lakehouse / warehouse / Data Factory / Real-Time Intelligence / semantic-model / platform-admin). Rationale in one line: **Fabric coverage in the repo today is literally zero** (`grep -ri "fabric" plugins/power-platform/` → 0 hits) even though it is the centerpiece of Microsoft's 2024-2026 data platform and sits dead-center in Matt's most-covered, most-active service line (Power Platform + Power BI + Microsoft data/AI). It clears every bar in [`docs/plugin-roadmap-analysis.md`](plugin-roadmap-analysis.md)'s ranking criteria, and — uniquely among the candidates — it can be built with first-party, citation-grounded authority because this environment has the **Microsoft Learn MCP server** attached.

---

## 1. What the repo is today (state of play, 2026-05-28)

Eight plugins ship today; the marketplace is mature:

| Plugin | Version | One-line |
|---|---|---|
| `ravenclaude-core` | 0.48.0 | Team Lead + 14 specialists, comfort-posture dashboard, the tribunal (the Thing), MCP allowlist |
| `power-platform` | 0.13.0 | 11 Power Platform agents (canvas/Fx, Automate, Dataverse, model-driven, PCF, Copilot Studio, Power Pages, **power-bi-engineer**, admin/ALM, tester) + bundled pbix-mcp |
| `finance` | 0.5.2 | FP&A / modeling / controller / treasury / valuation / audit-prep / board-pack |
| `regulatory-compliance` | 0.4.2 | AML/KYC, reg reporting, risk, policy, exam-prep, Bermuda-insurance |
| `web-design` | 0.4.3 | architect/UX/visual/frontend/content/a11y/perf |
| `edtech-partner-success` | 0.5.2 | PSM lane |
| `data-platform` | 0.3.4 | **non-Microsoft, SMB** embedded analytics — Cube/Evidence/Metabase/Superset/Supabase/Airbyte; explicitly opinionated *against* per-viewer-priced BI |
| `applied-statistics` | 0.1.0 | "is this difference REAL?" — the statistician seam |

Two big observations shape the gap:

1. **The Norse-themed dashboard features were superseded.** [`norse-features-build-plan.md`](norse-features-build-plan.md) specced 12 named dashboard surfaces (Heimdall, Mjölnir, Gleipnir, Norns, Bifröst, Yggdrasil, …). The actual recent workstream (PRs #81→#118, core v0.18→v0.48) went a different way: comfort-posture + the **tribunal (the Thing)** + the MCP allowlist dashboard. The Norse names that survive in code (`heimdall`, `mimir`) are tribunal **seat** names, not the planned dashboard tabs — those tabs were never built. The team voted with its commits; chasing the Norse backlog now would be re-opening a closed direction.
2. **The Microsoft data-platform half of Matt's stack is a hole.** `power-platform` covers low-code (apps/automate/Dataverse/Pages/Copilot Studio) and *report-level* Power BI (`power-bi-engineer` + pbix-mcp). `data-platform` deliberately covers the **non-Microsoft SMB** lane. Nobody covers **Microsoft Fabric** — OneLake, Lakehouse, Warehouse, Data Factory-in-Fabric, Real-Time Intelligence, Direct Lake, Fabric ALM, capacity FinOps. The roadmap doc itself flagged this: *"broader Fabric work (Lakehouses, Notebooks, Data Pipelines) is partial."*

---

## 2. Casting a wide net — candidate additions

Eleven candidates were enumerated and scored against the repo's own five ranking criteria from [`plugin-roadmap-analysis.md`](plugin-roadmap-analysis.md) §3, plus a sixth that matters *tonight*: **grounding availability** (can this be built with first-party authority right now, or would it be from-memory and stale-prone?). Scores are 1 (low) – 5 (high).

| # | Candidate | Matt-edge | Active fit | Differentiation | Surface area | Readiness | Grounding-now | Verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | **`microsoft-fabric` (new plugin)** | 5 | 5 | 4 | 5 | 4 | **5** (MS Learn MCP attached) | **BUILD — winner** |
| 2 | Deepen `power-platform` (Fabric-in-PP) | 5 | 5 | 3 | 4 | 4 | 5 | Strong, but Fabric is its own domain (see §3) |
| 3 | `salesforce` (roadmap) | 2 | 2 | 2 | 5 | 3 | 3 | Defer — competes with PP brand (unchanged from roadmap doc) |
| 4 | `agentic-ai` / claude-app-engineering | 4 | 3 | 3 | 4 | 3 | 4 (claude-api skill exists) | Defer — overlaps core `prompt-engineer`; revisit |
| 5 | `azure-cloud` (Bicep/Terraform/landing zones) | 3 | 3 | 2 | 5 | 3 | 5 | Defer — broad; partial overlap w/ Fabric admin + core backend |
| 6 | Deepen `web-design` (the fallback hint) | 3 | 4 | 3 | 3 | 5 | 4 | Good bonus work, not a "most-useful" headliner |
| 7 | `microsoft-365` / Copilot-extensibility | 3 | 3 | 3 | 3 | 3 | 5 | Partly in PP (copilot-studio-engineer); thin alone |
| 8 | `devops-cicd` plugin | 3 | 3 | 2 | 3 | 4 | 4 | Overlaps core git-workflow + PP solution-alm |
| 9 | `sql-database-engineering` | 3 | 3 | 2 | 3 | 4 | 4 | Overlaps core backend + Fabric warehouse |
| 10 | Build the Norse dashboard backlog | 2 | 2 | 3 | 4 | 3 | 2 | Superseded direction (see §1) |
| 11 | `security-appsec` plugin | 3 | 2 | 3 | 3 | 3 | 3 | Already core's `security-reviewer`; thin |

**Why Fabric wins decisively:** it is the only candidate that scores ≥4 on *all six* axes. It is the natural, roadmap-sanctioned extension of Matt's strongest service line; the differentiation is real (no equivalent opinionated Fabric plugin exists in the Claude Code ecosystem, and the `data-platform` plugin's anti-Microsoft-BI stance leaves the enterprise-Microsoft lane wide open); the surface area is enormous (six+ distinct workloads, each with genuine engineering judgment); and — the deciding factor for an autonomous overnight build — it can be grounded in **first-party Microsoft Learn docs in this very session**, so the content ships citation-backed and current rather than from a stale memory of a platform that changes monthly.

---

## 3. The architecture decision: new plugin vs. expand `power-platform`

This is the one genuinely contestable call, so it gets its own section (and is the first thing the expert review in §7 is asked to stress-test).

**Decision: a new `microsoft-fabric` plugin.** Reasoning against the [`new-plugin-checklist.md`](../checklists/new-plugin-checklist.md) §1 bar:

- **Domain-distinct?** Yes. Power Platform is *low-code application & automation* (canvas/model-driven apps, cloud flows, Dataverse, Power Pages, Copilot Studio). Fabric is an *enterprise data-and-analytics platform* (lake, warehouse, Spark, streaming, semantic models, ML/AI). They are sibling Microsoft clouds, not one domain. Putting Spark/Delta/KQL/medallion content inside `power-platform` would pollute the low-code team exactly the way the house rule forbids.
- **≥3 specialist agents in mind?** Easily six-to-eight (see §5).
- **Doesn't it overlap `power-platform/power-bi-engineer`?** There is exactly one seam, and it's clean: **Power BI as a standalone report/DAX/pbix tool → `power-platform/power-bi-engineer`** (it owns the pbix-mcp); **Power BI *semantic models running on Fabric* (Direct Lake over OneLake, lake-centric modeling, TMDL/PBIP in a Fabric workspace) → `microsoft-fabric`**. Direct Lake is a *Fabric* storage mode ([Direct Lake overview](https://learn.microsoft.com/fabric/fundamentals/direct-lake-overview)); the modeling decisions (V-Order gold tables, framing, fallback-to-DirectQuery) belong with the lake, not the report canvas. §5 documents the seam in both directions.
- **Doesn't it overlap `data-platform`?** No — they're complementary lanes with a documented router: `data-platform` is the **non-Microsoft, SMB, cost-sensitive, embedded-in-app** answer (Cube/Evidence/Metabase, opinionated against per-viewer BI); `microsoft-fabric` is the **enterprise-Microsoft, OneLake-centric, Purview-governed** answer. The seam is a one-question router (Microsoft shop + Fabric capacity + OneLake/Direct Lake/Purview needs → Fabric; else → data-platform). §5 documents it.
- **`applied-statistics` seam** already exists and is reused: "is this Fabric metric movement real?" → `applied-statistician`.

---

## 4. Deep dive — the Microsoft Fabric surface (research synthesis)

All claims grounded in Microsoft Learn, retrieved 2026-05-28. This is the knowledge spine the plugin's agents and knowledge bank are built from.

### 4.1 Platform & OneLake
- **OneLake** is a single SaaS data lake built on ADLS Gen2; every workload reads/writes one copy in **open Delta** format; no per-transaction charge — reads/writes consume **Fabric capacity** instead. ([overview](https://learn.microsoft.com/fabric/fundamentals/microsoft-fabric-overview), [capacity consumption](https://learn.microsoft.com/fabric/onelake/onelake-capacity-consumption))
- **Shortcuts** give zero-copy access to data in other workspaces/tenants or external lakes (ADLS/S3/GCS); compute is billed to the *consuming* capacity, storage to the *owning* capacity. ([shortcuts](https://learn.microsoft.com/fabric/onelake/onelake-shortcuts))
- **Capacity** (F2…F2048 SKUs; F64 = old P1) is the unit of compute; **bursting** lets ops temporarily exceed the SKU, **smoothing** averages usage over 5-64 min (interactive) or 24 h (background), and **throttling** kicks in on sustained overuse. ([throttling](https://learn.microsoft.com/fabric/enterprise/throttling), [plan capacity](https://learn.microsoft.com/fabric/enterprise/plan-capacity))
- **Workspaces** are the security/admin/cost boundary; **domains/subdomains** group workspaces for data-mesh governance. ([domains](https://learn.microsoft.com/fabric/governance/domains), [Fabric architecture](https://learn.microsoft.com/azure/cloud-adoption-framework/data/architecture-fabric-data-lake-unify-data-platform))

### 4.2 The data-store decision guide (the core "which store?" judgment)
Per [choose-a-data-store](https://learn.microsoft.com/fabric/fundamentals/decision-guide-data-store) and [Warehouse-vs-Lakehouse](https://learn.microsoft.com/fabric/fundamentals/decision-guide-lakehouse-warehouse):

| Store | Pick when | Engine |
|---|---|---|
| **Lakehouse** | big data, un/semi/structured, Spark-first, data engineering, medallion | Spark + read-only SQL endpoint |
| **Warehouse** | structured, T-SQL-first, multi-table ACID transactions, BI/OLAP | full T-SQL |
| **Eventhouse** | streaming/telemetry, high-granularity interactive analytics | KQL (+ T-SQL endpoint) |
| **SQL database** | OLTP / operational + operational analytics | T-SQL (mirrored to OneLake) |
| **Cosmos DB** | NoSQL, vector search, globally distributed | NoSQL |
| **Shortcut** | data already exists elsewhere; want single source of truth | n/a (virtualization) |

### 4.3 Data Engineering (Lakehouse)
- Delta Lake everywhere; **V-Order** write-time Parquet optimization for fast Power BI/SQL reads. ([lakehouse overview](https://learn.microsoft.com/fabric/data-engineering/lakehouse-overview))
- **Medallion** bronze→silver→gold, each layer ideally its own lakehouse/workspace; bronze prioritizes ingest speed (no V-Order), gold prioritizes read (V-Order required for Direct Lake, 400 MB-1 GB files). ([medallion](https://learn.microsoft.com/fabric/onelake/onelake-medallion-lakehouse-architecture), [table maintenance](https://learn.microsoft.com/fabric/fundamentals/table-maintenance-optimization))
- **Spark compute**: starter pools (5-10 s session start, Medium nodes) vs custom pools/environments (libraries, node size, Spark props); runtimes 1.2/1.3/2.0 = Spark 3.4/3.5/4.0. **Python notebooks** (2-core, instant) vs **PySpark notebooks** (distributed). ([spark-compute](https://learn.microsoft.com/fabric/data-engineering/spark-compute), [notebook selection](https://learn.microsoft.com/fabric/data-engineering/fabric-notebook-selection-guide))

### 4.4 Data Warehouse
- Lake-centric T-SQL warehouse storing Delta in OneLake; full DQL/DML/DDL + multi-table ACID; serverless distributed query processing; **burstable capacity** (scale factor 1×-32× on small SKUs). ([data warehousing](https://learn.microsoft.com/fabric/data-warehouse/data-warehousing), [burstable](https://learn.microsoft.com/fabric/data-warehouse/burstable-capacity))

### 4.5 Data Factory (ingestion/integration) — the data-movement decision guide
Per [choose-a-data-movement-strategy](https://learn.microsoft.com/fabric/data-factory/decision-guide-data-movement):

| Method | Pick when | Notes |
|---|---|---|
| **Mirroring** | near-real-time replica of an operational DB | **free**, no setup, read-only Delta in OneLake |
| **Copy job** | bulk / incremental / CDC without building pipelines | 50+ connectors, watermark + native CDC |
| **Copy activity (pipeline)** | orchestrated, fully customizable ELT | you manage state/incremental yourself |
| **Eventstream** | real-time streaming ingestion | routes to Eventhouse/Lakehouse/Activator |

- **Dataflow Gen2** = 300+ low-code transforms; **Fast Copy** = up to 13-21× faster ingest (bypasses mashup engine). ([dataflow strategy](https://learn.microsoft.com/fabric/data-factory/decision-guide-data-transformation))

### 4.6 Real-Time Intelligence
- **Eventstream** (ingest/transform/route) → **Eventhouse** (KQL DB, auto-index/partition by time) → **KQL queryset** / **Real-Time dashboard** → **Activator** (no-code alert/trigger/action). Native anomaly detection; T-SQL endpoint on Eventhouse; Eventhouse endpoint for Lakehouse (Oct 2025). ([RTI overview](https://learn.microsoft.com/fabric/real-time-intelligence/overview))

### 4.7 Power BI on Fabric — Direct Lake (the headline BI capability)
- **Direct Lake** loads Delta tables straight into the VertiPaq engine from OneLake — Import-class speed with DirectQuery-class freshness, no refresh-copy; refresh = metadata **framing** (seconds); auto-**fallback to DirectQuery** when limits/unsupported features hit. Direct Lake on OneLake vs on SQL. PBIP/TMDL for git-deployable models. ([Direct Lake overview](https://learn.microsoft.com/fabric/fundamentals/direct-lake-overview), [semantic models](https://learn.microsoft.com/fabric/data-warehouse/semantic-models))

### 4.8 Data Science & AI (2026)
- **Fabric Data Agents** — conversational read-only NL Q&A over Lakehouse/Warehouse/semantic model/KQL/ontology via Azure OpenAI Assistant APIs; integrate with Foundry, Copilot Studio, M365 Copilot. **Operations Agents** — ontology-driven, act on live streams via Activator/Power Automate. **Copilot in Fabric** (notebooks `/fix`, DAX, KQL, Data Factory). MLflow autologging, AutoML, Data Wrangler, model endpoints, AI functions. ([analyze-train-data](https://learn.microsoft.com/fabric/fundamentals/analyze-train-data), [copilot overview](https://learn.microsoft.com/fabric/fundamentals/copilot-fabric-overview))

### 4.9 ALM / CI-CD
- **Git integration** (Azure DevOps/GitHub, workspace ↔ repo) + **deployment pipelines** (dev/test/prod stages, metadata-only). **fabric-cicd**, **Fabric CLI v1.5 GA** (March 2026; `fab`, service principal, AI agent layer), **bulk import/export item-definition APIs** (preview). ([CI/CD overview](https://learn.microsoft.com/fabric/cicd/cicd-overview), [manage-deployment](https://learn.microsoft.com/fabric/cicd/manage-deployment))

### 4.10 Governance, security & FinOps
- **OneLake catalog** Explore/Govern/**Secure** tabs; **workspace roles** (Admin/Member/Contributor/Viewer); **OneLake security** RBAC (data-access roles, default roles, RLS/CLS/OLS); Purview integration; sensitivity labels; external data sharing. ([security overview](https://learn.microsoft.com/fabric/security/security-overview), [OneLake security model](https://learn.microsoft.com/fabric/onelake/security/data-access-control-model))
- **FinOps**: Capacity Estimator, 1-yr reservations, rightsizing F SKUs, pay-as-you-go/autoscale, Capacity Metrics app, smoothing/bursting; per-experience optimization. ([cost optimization](https://learn.microsoft.com/azure/well-architected/microsoft-fabric/cost-optimization), [optimize capacity](https://learn.microsoft.com/fabric/enterprise/optimize-capacity))
- A full **Azure Well-Architected Framework for Microsoft Fabric** exists (reliability/security/cost/operational-excellence/performance) — the spine for the plugin's "house opinions."

---

## 5. Plugin scope (the buildout)

A domain-specialist team plugin in the mold of `power-platform`. Requires `ravenclaude-core@>=0.7.0` to inherit the Capability Grounding + Structured Output protocols.

### 5.1 Specialist roster (planned: 8; v0.1.0 ships 6 — see build plan)

| Agent | Owns | Spawn when |
|---|---|---|
| **`fabric-architect`** | Workspace/domain topology, capacity sizing & SKU, the **store-selection decision guide**, medallion design, data-mesh, shortcuts-vs-copy | greenfield Fabric architecture; "lakehouse or warehouse?"; capacity sizing; "how should I lay out workspaces/domains?" |
| **`lakehouse-engineer`** | Lakehouse, Spark/PySpark + Python notebooks, Delta/V-Order, medallion bronze/silver/gold, materialized lake views, environments/pools, shortcuts | data engineering, notebook authoring, Delta optimization, "build the medallion pipeline" |
| **`warehouse-engineer`** | Fabric Warehouse T-SQL, dimensional modeling, ACID, SQL analytics endpoint, perf (burstable/smoothing), CLS/OLS | "build/optimize the warehouse"; T-SQL ELT; star-schema; SQL-first teams |
| **`data-factory-engineer`** | The **data-movement decision guide**, pipelines, Dataflow Gen2 (Fast Copy), Copy job (CDC/incremental), Mirroring, connectors, orchestration | "get data into Fabric"; ingestion/replication; "mirror this DB"; pipeline orchestration |
| **`realtime-intelligence-engineer`** | Eventstream, Eventhouse, KQL, Real-Time dashboards, Activator, anomaly detection | streaming/telemetry, KQL, "alert when…", real-time dashboards |
| **`fabric-admin`** | Capacity admin + **FinOps**, OneLake security (RBAC/RLS/CLS/OLS), domains, Purview, sensitivity labels, **ALM** (Git + deployment pipelines + fabric-cli/fabric-cicd), tenant settings, DLP | capacity/cost management, governance, security model, CI/CD setup, "why is my capacity throttling?" |
| *(v0.2.0)* `fabric-semantic-model-engineer` | Direct Lake semantic models on OneLake, TMDL/PBIP, DAX-on-Fabric, framing/fallback, the power-bi-engineer seam | "build a Direct Lake model"; "why did my model fall back to DirectQuery?" |
| *(v0.3.0)* `fabric-data-ai-engineer` | Notebooks/MLflow/AutoML, **Fabric Data Agents**, Operations Agents, AI functions, Copilot, Foundry/ontology | "build a Data Agent"; ML lifecycle on Fabric; AI-over-OneLake |

### 5.2 Knowledge bank (the citation-grounded reference spine)
Each file carries `Last reviewed: 2026-05-28` + confidence notation + MS Learn source URLs.
1. `fabric-store-decision-tree.md` — Mermaid tree: lakehouse / warehouse / eventhouse / SQL DB / Cosmos / shortcut.
2. `fabric-data-movement-decision-tree.md` — Mermaid tree: mirroring / copy job / copy activity / eventstream / dataflow gen2.
3. `medallion-on-onelake.md` — bronze/silver/gold, per-layer V-Order + file-size + maintenance recommendations.
4. `direct-lake-and-semantic-models.md` — Direct Lake mechanics, framing, fallback, gold-table shaping for Direct Lake.
5. `capacity-finops-and-throttling.md` — SKUs, CU, smoothing/bursting/throttling, reservations, rightsizing, Capacity Metrics app.
6. `onelake-security-and-governance.md` — workspace roles vs OneLake security, RLS/CLS/OLS, domains, Purview, sensitivity labels.
7. `fabric-alm-cicd.md` — Git integration + deployment pipelines + fabric-cli/fabric-cicd + bulk APIs; choose-workflow.
8. `fabric-2026-capability-map.md` — what's GA vs preview as of 2026-05 (Fabric CLI v1.5, Spark 4.0/Runtime 2.0, Data Agents, materialized lake views, Cosmos DB in Fabric, SQL DB in Fabric, OneLake security) — the freshness anchor the Researcher sweep re-dates.

### 5.3 Templates
1. `fabric-workspace-and-capacity-plan.md`
2. `medallion-lakehouse-spec.md`
3. `fabric-ingestion-design.md` (data-movement method + connector + schedule + incremental strategy)
4. `direct-lake-semantic-model-spec.md`
5. `fabric-capacity-cost-review.md`
6. `fabric-alm-runbook.md` (Git + deployment-pipeline promotion runbook)

### 5.4 Hook (advisory, the `power-platform` pattern)
`check-fabric-anti-patterns.sh` — PreToolUse Write/Edit on `.py`/`.sql`/`.kql`/`.ipynb`/`.tmdl`/`.json`/`.md`, advisory (`exit 0`), flags grep-able house-opinion violations (see §5.5). `FABRIC_STRICT=1` makes it blocking.

### 5.5 House opinions (every agent enforces; the hook flags the grep-able ones)
1. **One copy in OneLake.** Reach for a **shortcut** before copying data; duplication is a smell. (Hook: flags `COPY INTO`/notebook copy where a shortcut would do — advisory only.)
2. **Pick the store from the decision tree, not from habit.** Lakehouse↔Spark, Warehouse↔T-SQL+multi-table-ACID, Eventhouse↔streaming.
3. **Medallion or justify its absence.** Bronze raw/immutable, silver curated, gold business-ready; don't serve bronze to Direct Lake/SQL endpoint.
4. **V-Order on gold for Direct Lake; not on bronze.** Match optimization to the layer.
5. **Capacity is a shared, throttleable resource.** Size to average + smoothing, not peak; never assume a heavy job is "free."
6. **Security at the right plane.** Workspace roles = control plane; OneLake security (RLS/CLS/OLS) = data plane; Viewer ≠ data access by default.
7. **ALM is Git + deployment pipelines, dev/test/prod.** No hand-editing prod workspaces; metadata-only deploys.
8. **Direct Lake first, then fallback-aware.** Know what forces DirectQuery fallback and design gold tables to avoid it.
9. **Cite the capability's GA/preview status with a retrieval date.** Fabric ships monthly; "preview" is a design constraint, not a footnote.
10. **Don't reinvent `data-platform` or `power-platform`.** Honor the seams (§5.6); escalate across them.

### 5.6 Cross-plugin seams (documented in CLAUDE.md §"Escalating out")
- **`power-platform/power-bi-engineer`** — standalone Power BI reports/DAX/pbix; this plugin owns Fabric-native Direct Lake semantic models. Bi-directional handoff.
- **`data-platform`** — the non-Microsoft / SMB / embedded lane; one-question router (Microsoft+Fabric+OneLake/Purview → here; else → data-platform).
- **`applied-statistics`** — "is this Fabric metric movement real?" → `applied-statistician`.
- **`ravenclaude-core/security-reviewer`** — any auth/secrets/PII change (service principals, OneLake security, tenant settings) routes through core's security reviewer (mandatory per existing convention).
- **`ravenclaude-core/data-engineer`** — generic (non-Fabric) ELT/dbt/warehouse modeling stays in core; Fabric-specific lives here.
- **`ravenclaude-core/architect`** — cross-domain boundary adjudication.

---

## 6. Risks & open questions (pre-review)
- **R1 — Roster size vs. build time.** 8 agents is the plan; shipping 6 strong agents at v0.1.0 and sequencing semantic-model + data-ai is the realism call. *(Expert review: confirm the 6-agent v0.1.0 cut.)*
- **R2 — power-bi-engineer overlap.** The Direct-Lake seam must be airtight or two agents fight over Power BI. *(Review: stress-test the seam wording.)*
- **R3 — Currency rot.** Fabric ships monthly; the `fabric-2026-capability-map.md` + retrieval-dated citations are the mitigation, but the plugin must be wired into the Researcher staleness sweep.
- **R4 — No bundled MCP at v0.1.0.** Unlike `power-platform` (pbix-mcp), Fabric automation is via `fab` CLI + REST, which the consumer installs. v0.1.0 documents the prerequisite rather than bundling. *(Review: is that the right call, or bundle/declare an MCP?)*
- **R5 — Hook false-positive rate.** The "prefer shortcut over copy" check is heuristic; ship advisory-only.

---

## 7. Expert review + gap analysis + score

Two independent reviewer agents were convened against §0-§6: a **Microsoft Fabric domain architect** and a **RavenClaude marketplace-conventions architect**. Both returned **Approve-with-changes** on every dimension. The decision to build (new `microsoft-fabric` plugin) was endorsed without dissent; all findings are content/scope refinements, not a redesign.

### 7.1 Scores (1-5)

| Dimension | Score | Reviewer |
|---|---|---|
| New-plugin justification | 5 | conventions |
| Workload coverage | 4 | domain |
| Technical accuracy (as drafted in §4) | 3 | domain |
| Roster design | 4 | domain |
| Knowledge-bank design | 4 | domain |
| House-opinions quality | 3 | domain |
| Seam cleanliness (power-bi / data-platform / applied-statistics) | 3 | conventions |
| Convention compliance | 4 | conventions |
| Scope realism for v0.1.0 | 4 | both |

**Composite: ~3.8/5 — Approve-with-changes.** The two low scores (technical accuracy 3, seam cleanliness 3) drive the must-fix list; both are fixable in the knowledge files + CLAUDE.md wording, not the architecture.

### 7.2 Gap analysis — must-fix findings (folded into §8)

1. **[domain + conventions] Promote the Direct Lake / semantic-model owner into v0.1.0; defer `fabric-data-ai-engineer` instead.** Direct Lake is the highest-frequency Fabric-BI decision and the riskiest seam (R2). Deferring it leaves "why did Direct Lake fall back?" unowned by *either* plugin. → v0.1.0 ships **7 agents** (adds `fabric-semantic-model-engineer`); data-AI moves to v0.2.0.
2. **[domain] §4.7 conflates the two Direct Lake modes.** **Direct Lake on OneLake does NOT fall back to DirectQuery** (it errors on unprocessed tables, supports composite models); only **Direct Lake on SQL** falls back, and SQL-endpoint OLS/RLS *forces* that fallback. → rewrite knowledge doc #4 + house opinion #8 around the two-mode split.
3. **[domain] OneLake security RLS/CLS/OLS is NOT uniformly GA.** Eventhouse is RLS-only + preview; third-party engines preview; **schema-enabled lakehouses are a prerequisite**; hard caps (250 roles/item, 500 members/role); RLS-only and CLS-only roles can't be combined. → knowledge doc #6 carries an engine-by-engine GA/preview matrix; `fabric-admin` owns it explicitly.
4. **[conventions] The data-platform seam must be bidirectional and edited into BOTH plugins.** `data-platform/database-setup-guide` already lists Fabric, house opinion #12 ("Microsoft is special") steers M365 clients to "Power BI Embedded + Fabric," and `knowledge/multi-tenant-rls-patterns.md` mentions Fabric OneLake. A one-way router is insufficient. → amend `data-platform/CLAUDE.md` §10 + house opinion #12 to hand off enterprise-Fabric, narrowing its Fabric mention to "SMB embedded-app context only."
5. **[conventions] `requires` pin + marketplace/CHANGELOG sync + scenario frontmatter.** Pin `ravenclaude-core@>=0.7.0` (Capability Grounding + Structured Output); add the `marketplace.json` `plugins[]` entry with matching `version`; ship `CHANGELOG.md` at `## [0.1.0]`; all 7 agents ship the full `audience`/`works_with`/`scenarios`/`quickstart` schema. No `NOTICE.md`/MCP at v0.1.0 (the `fab` CLI prerequisite is documented, not bundled — R4 resolved).

### 7.3 Should-fix / accuracy corrections (folded into §8 + the knowledge bank)

- **House opinions expand to 14**: add **Native Execution Engine on by default** (Velox/Gluten, GA on Runtime 1.3/2.0, the biggest free perf/cost win); **Liquid Clustering / Z-order over static partitioning**; **deletion vectors** for merge-heavy silver; **schema-enabled lakehouses as the default**.
- **House opinion #5** adds **capacity isolation** (throttling is per-capacity; isolate noisy workloads) + **surge protection**.
- **`lakehouse-engineer` owns Materialized Lake Views** as a first-class medallion path (`CREATE MATERIALIZED LAKE VIEW`, declarative dependency-ordered bronze→silver→gold + data-quality constraints) — the "MLV vs notebook vs Dataflow Gen2" decision. Note DL-on-OneLake can build on an MLV but not a non-materialized SQL view.
- **`fabric-architect` owns the unified "shortcut vs mirror vs auto-mirror" call** — Cosmos DB in Fabric and SQL DB in Fabric **auto-mirror to OneLake Delta (HTAP), zero-config, CU-based billing, Entra-only auth**; doc #2's tree must include in-Fabric auto-mirror, not just external-DB mirroring.
- **§4.3 runtime accuracy**: Runtime 1.2 / Spark 3.4 is **EOSA** (end of support 2026-03-31, already past); **Runtime 1.3 / Spark 3.5 is the current GA** (LTS); **Runtime 2.0 / Spark 4.0 is still public preview** — don't imply Spark 4.0 is production-default. **Autotune is Runtime-1.2-only** (deprecated path); NEE is the modern lever — don't recommend autotune.
- **§4.5 "Mirroring is free"** → "**free to replicate, not free to query**": replication+storage free only up to a CU-based cap (1 TB free per CU; F64 = 64 TB); query compute always billed; cross-region egress applies.
- **§4.2 store table**: Cosmos DB / SQL DB in Fabric auto-mirror to OneLake Delta (HTAP) with a read-only SQL analytics endpoint — their analytical surface is the same OneLake-Delta pattern.

---

## 8. Revised plan (per §7)

**Net of the review: build the plugin, with these locked-in changes.**

### 8.1 Roster — v0.1.0 ships 7 agents
`fabric-architect`, `lakehouse-engineer`, `warehouse-engineer`, `data-factory-engineer`, `realtime-intelligence-engineer`, **`fabric-semantic-model-engineer`** (promoted), `fabric-admin`. **Deferred to v0.2.0:** `fabric-data-ai-engineer` (notebooks/MLflow/Data Agents/Operations Agents/Copilot/AI functions). Every agent ships full scenario frontmatter.

### 8.2 Knowledge bank — 8 docs, accuracy-corrected
Same eight as §5.2, with the §7 corrections baked in: doc #4 (Direct Lake) split by mode + fallback-by-mode; doc #6 (OneLake security) carries the engine GA/preview matrix + schema-enabled prerequisite + caps; doc #2 (data movement) includes in-Fabric auto-mirror; doc #3 (medallion) names MLVs + NEE + Liquid Clustering + deletion vectors; doc #8 (capability map) dates Runtime 1.3 GA / 2.0 preview / 1.2 EOSA, Fabric CLI v1.5 GA, NEE GA, Data Agents.

### 8.3 House opinions — 14 (was 10)
The original 10 (with #1 corrected to "shortcut-first; mirroring is free to replicate, not free to query"; #5 adds capacity isolation + surge protection; #8 rewritten for the two Direct Lake modes), plus: **#11 Native Execution Engine on by default** (Runtime 1.3/2.0); **#12 Liquid Clustering / Z-order over static partitioning** on silver/gold; **#13 deletion vectors on merge-heavy tables**; **#14 schema-enabled lakehouses by default** (and required for OneLake security). #10 links to §5.6 as the single seam source.

### 8.4 Seams — bidirectional, exact wording locked
Use the conventions reviewer's literal wording in `microsoft-fabric/CLAUDE.md` §"Escalating out":
- **power-bi-engineer:** "*if the question is about a measure, a visual, or a `.pbix` → power-bi-engineer; if it's about the Delta tables, OneLake storage mode, or why Direct Lake fell back → microsoft-fabric.*" `fabric-semantic-model-engineer` owns the Direct Lake model; gold-table shaping stays with `lakehouse-engineer`; DAX-measure authoring escalates to `power-bi-engineer`.
- **data-platform (bidirectional, in both plugins):** one-question router — enterprise Microsoft shop on Fabric capacity (OneLake/Direct Lake/Purview) → `microsoft-fabric`; non-Microsoft / SMB / cost-sensitive / embedded-in-app → `data-platform`. `data-platform` may stand up an Azure SQL / Fabric SQL endpoint as a plain DB for an SMB embed, but enterprise Fabric architecture hands off here; the embedded-app rendering layer (JWT/CSP/per-viewer economics) hands back to `data-platform`. **Edit `data-platform/CLAUDE.md` §10 + house opinion #12 reciprocally.**

### 8.5 Build mechanics
`requires: ravenclaude-core@>=0.7.0`; `marketplace.json` entry with `version` synced to `plugin.json`; `CHANGELOG.md` at `[0.1.0]`; advisory hook (`exit 0`, `FABRIC_STRICT=1` to block); standard subdirs already in `.repo-layout.json` (no allow-list change needed); regenerate `repo-guide.html`; update `architecture.md` Status table + `README.md`. No `NOTICE.md`/MCP — the `fab` CLI / REST prerequisite is documented in CLAUDE.md.

The execution-sequenced version of this is [`microsoft-fabric-build-plan.md`](microsoft-fabric-build-plan.md).

---

## 9. Sources
All Microsoft Learn, retrieved 2026-05-28 via the Microsoft Learn MCP server. Key anchors: the Fabric [fundamentals overview](https://learn.microsoft.com/fabric/fundamentals/microsoft-fabric-overview), the four **decision guides** ([data store](https://learn.microsoft.com/fabric/fundamentals/decision-guide-data-store), [lakehouse vs warehouse](https://learn.microsoft.com/fabric/fundamentals/decision-guide-lakehouse-warehouse), [data movement](https://learn.microsoft.com/fabric/data-factory/decision-guide-data-movement), [data transformation](https://learn.microsoft.com/fabric/data-factory/decision-guide-data-transformation)), [Direct Lake](https://learn.microsoft.com/fabric/fundamentals/direct-lake-overview), [medallion on OneLake](https://learn.microsoft.com/fabric/onelake/onelake-medallion-lakehouse-architecture), [throttling/capacity](https://learn.microsoft.com/fabric/enterprise/throttling), [OneLake security](https://learn.microsoft.com/fabric/onelake/security/data-access-control-model), [CI/CD overview](https://learn.microsoft.com/fabric/cicd/cicd-overview), and the [Well-Architected Framework for Fabric](https://learn.microsoft.com/azure/well-architected/microsoft-fabric/cost-optimization).
