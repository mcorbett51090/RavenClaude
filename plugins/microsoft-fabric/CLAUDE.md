# Microsoft Fabric Plugin — Team Constitution

> Team constitution for the `microsoft-fabric` Claude Code plugin. Seven specialist agents covering the Microsoft Fabric data-and-analytics platform — OneLake, Lakehouse, Warehouse, Data Factory, Real-Time Intelligence, Direct Lake semantic models, and platform admin — plus a citation-grounded knowledge bank, templates, and an advisory hook.
>
> Built for enterprise Microsoft / Fabric engagements: the consultant needs Fabric judgment (which store? which movement? Direct Lake mode? capacity sizing? security plane?) grounded in first-party docs, not a memory of a platform that changes monthly.
>
> **Orientation:** this file is **domain-specific** to Microsoft Fabric. For the domain-neutral team constitution inherited by every plugin (architect, coders, reviewers, project-manager, etc.), see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`fabric-architect`](agents/fabric-architect.md) | Workspace/domain/capacity topology, the **store-selection** + **shortcut/mirror/auto-mirror** decisions, medallion layout, data-mesh | "Lakehouse or warehouse?"; "design the Fabric topology"; "shortcut, mirror, or copy?" |
| [`lakehouse-engineer`](agents/lakehouse-engineer.md) | Lakehouse, Spark/Python notebooks, Delta/V-Order/NEE/Liquid-Clustering/deletion-vectors, **medallion**, **materialized lake views**, gold-shaping for Direct Lake | "build the medallion"; notebook authoring; "this Delta table is slow" |
| [`warehouse-engineer`](agents/warehouse-engineer.md) | Fabric Warehouse T-SQL, dimensional modeling, multi-table ACID, SQL analytics endpoint, burstable perf, SQL-native RLS/CLS/masking/OLS | "build a star schema"; T-SQL ELT; "warehouse or SQL endpoint?" |
| [`data-factory-engineer`](agents/data-factory-engineer.md) | The **data-movement decision**: Mirroring, Copy job, pipelines, Dataflow Gen2 (Fast Copy), Eventstream; connectors; incremental/CDC | "ingest/replicate <source>"; "mirror this DB"; pipeline orchestration |
| [`realtime-intelligence-engineer`](agents/realtime-intelligence-engineer.md) | Eventstream → Eventhouse → KQL → Real-Time dashboard → Activator; anomaly detection | streaming/telemetry; "alert when…"; KQL; real-time dashboards |
| [`fabric-semantic-model-engineer`](agents/fabric-semantic-model-engineer.md) | **Direct Lake** semantic models (on-OneLake vs on-SQL), framing, fallback avoidance, gold shaping, PBIP/TMDL | "build a Direct Lake model"; "why did Direct Lake fall back?"; storage-mode choice |
| [`fabric-admin`](agents/fabric-admin.md) | Capacity + **FinOps**, **OneLake security** (two planes + GA/preview matrix), domains, Purview, **ALM** (Git + deployment pipelines + Fabric CLI) | "why is my capacity throttling?"; the security model; CI/CD setup |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. *(Deferred to v0.2.0: `fabric-data-ai-engineer` — notebooks/MLflow/AutoML, Fabric Data Agents, Operations Agents, Copilot, AI functions.)*

This is a domain **doing**-team in the `power-platform` mold (which has 11 agents). Per the marketplace house rule, domain plugins may ship specialist *doing*-agents but must **not** fork core's *review* roles (architect/security-reviewer) — this plugin routes architecture + security back to core (§10).

---

## 2. Routing rules (Team Lead)

- **"Where does this go in Fabric?" / "Lakehouse or warehouse?" / "Shortcut, mirror, or copy?"** → `fabric-architect` (traverses the store + movement decision trees).
- **"Build the medallion / notebook / Delta tables." / "This table is slow."** → `lakehouse-engineer`.
- **"Build / optimize the warehouse." / T-SQL star schema.** → `warehouse-engineer`.
- **"Get data into Fabric." / "Mirror this DB." / incremental/CDC.** → `data-factory-engineer`.
- **Streaming / KQL / "alert when…" / real-time dashboard.** → `realtime-intelligence-engineer`.
- **"Build a Direct Lake model." / "Why did Direct Lake fall back?"** → `fabric-semantic-model-engineer`.
- **Capacity / cost / throttling / security model / governance / CI-CD.** → `fabric-admin`.
- **Standalone Power BI report / DAX / `.pbix`** → `power-platform/power-bi-engineer` (the seam, §10).
- **Non-Microsoft / SMB / embedded-in-app analytics** → `data-platform` (the router, §10).
- **"Is this Fabric metric movement real?"** → `applied-statistics/applied-statistician`.

---

## 3. Cross-cutting house opinions (every agent enforces; the hook flags the grep-able ones)

1. **One copy in OneLake.** Reach for a **shortcut** before copying; mirroring is **free to replicate, not free to query**. Duplication is a smell.
2. **Pick the store from the decision tree, not from habit.** Lakehouse↔Spark, Warehouse↔T-SQL+multi-table-ACID, Eventhouse↔streaming.
3. **Medallion or justify its absence.** Bronze raw/immutable, silver curated, gold business-ready. **Never serve bronze to Direct Lake / the SQL endpoint.**
4. **V-Order on gold for Direct Lake; not on bronze.** Match optimization to the layer.
5. **Capacity is a shared, throttleable resource.** Size to **average + smoothing**, **isolate** noisy workloads, use surge protection; never assume a heavy job is "free."
6. **Security at the right plane.** Workspace roles = control plane; OneLake security (RLS/CLS/OLS) = data plane; Viewer ≠ data access by default; Admin/Member/Contributor Write overrides OneLake-security Read.
7. **ALM is Git + deployment pipelines, dev/test/prod.** No hand-editing prod; metadata-only deploys.
8. **Know your Direct Lake mode.** On-OneLake = **no DirectQuery fallback** (errors / empty-on-security-misconfig, composite models); on-SQL = **falls back** (and SQL OLS/RLS forces it). Design gold accordingly.
9. **Cite the capability's GA/preview status with a retrieval date.** Fabric ships monthly; "preview" is a design constraint.
10. **Don't reinvent the neighbors.** Honor the seams (§10): enterprise Microsoft/Fabric here; non-Microsoft/SMB embedded → `data-platform`; standalone Power BI → `power-platform/power-bi-engineer`.
11. **Native Execution Engine on by default** (Runtime 1.3/2.0) — the biggest free Spark perf/cost win. Autotune is the dead Runtime-1.2 path; don't use it.
12. **Liquid Clustering / Z-order over static partitioning** on silver/gold — file skipping without partition explosion.
13. **Deletion vectors on merge-heavy tables** — avoid full-file rewrites on MERGE/UPDATE/DELETE.
14. **Schema-enabled lakehouses by default** — namespace hygiene and the prerequisite for OneLake-security data preview.

---

## 4. Anti-patterns every agent flags

- Copying data that a **shortcut** would serve (house opinion #1).
- Calling Mirroring "free" without the "replicate-free, query-billed" caveat.
- Choosing a store by habit instead of the decision tree (#2).
- Serving **bronze** to Direct Lake / the SQL endpoint (#3).
- V-Order on bronze (write overhead) or missing on gold consumed by Direct Lake (#4).
- Sizing capacity for **peak** instead of average+smoothing; one capacity for everything (no isolation) (#5).
- Treating workspace roles as data access, or promising RLS/CLS that's preview-only on that engine (#6).
- Hand-editing a prod workspace instead of promoting via a deployment pipeline (#7).
- Saying "Direct Lake" without naming the mode, or assuming on-OneLake falls back to DirectQuery (#8).
- Quoting a Fabric capability's GA/preview status with no retrieval date (#9).
- Recommending **autotune** (deprecated Runtime-1.2) instead of the Native Execution Engine (#11).
- Static partitioning where Liquid Clustering fits; no deletion vectors on a merge-heavy table (#12/#13).

---

## 5. Capability Grounding Protocol (Anti-Hallucination)

Inherits the CGP from `ravenclaude-core`. Before any agent says "I can't" or declares a design, it must:

1. **Consult the knowledge bank** (§8) — the decision trees and reference docs are the source of truth.
2. **Traverse the relevant decision tree** before naming a store / movement method / storage mode — don't keyword-match.
3. **Try the next-easiest defensible path** before declaring blocked (e.g. shortcut → mirror → copy job → pipeline; reframe → gold reshape → mode change).
4. **Escalate with the mandatory phrasing** — what was tried, what was ruled out, the recommended next path.

See the upstream protocol in [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md).

---

## 6. Output Contract

Each agent ends its report with its role-specific contract (see the agent file) **plus the cross-plugin Structured Output Protocol JSON block** ([`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)). Agents are **advisory and interactive**: the client's Fabric tenant is outside the repo, so they recommend and emit runnable `fab` CLI / KQL / T-SQL / PySpark / Power Query snippets the consultant runs — they don't execute against a live tenant.

---

## 7. Automated checks (hooks)

The `hooks/` directory ships [`check-fabric-anti-patterns.sh`](hooks/check-fabric-anti-patterns.sh) — a PreToolUse Write/Edit/MultiEdit hook on Fabric-ish files (`.py`/`.ipynb`/`.sql`/`.kql`/`.tmdl`/`.json`/`.md`):

| Check | Triggers on | Rule (§3 / §4) |
|---|---|---|
| `spark.ms.autotune.enabled` set true | `.py`/`.ipynb`/`.json` | #11 (use NEE, not autotune) |
| "mirror"/"mirroring" + "free" with no "query"/"billed" nearby | `.md` | #1 (replicate-free ≠ query-free) |
| V-Order disabled on a gold/Direct-Lake table | `.py`/`.sql`/`.ipynb` | #4 |
| "Direct Lake" with no mode (on OneLake / on SQL) nearby | `.md`/`.tmdl` | #8 |

Advisory by default (`exit 0` with stderr warnings). Set `FABRIC_STRICT=1` to make it blocking. See `power-platform/hooks/check-house-opinions.sh` for the canonical pattern.

---

## 8. Knowledge bank

Reference docs with `Last reviewed:` dates + confidence notation + Microsoft Learn source URLs. Inline priors live on the agents; the files in `knowledge/` are the source of truth, re-read on demand.

| File | Read when |
|---|---|
| [`knowledge/fabric-store-decision-tree.md`](knowledge/fabric-store-decision-tree.md) | Choosing a store — lakehouse/warehouse/eventhouse/SQL DB/Cosmos/shortcut; the lakehouse-vs-warehouse + shortcut/mirror/auto-mirror calls |
| [`knowledge/fabric-data-movement-decision-tree.md`](knowledge/fabric-data-movement-decision-tree.md) | Choosing ingestion — mirroring/copy-job/copy-activity/eventstream/dataflow-gen2 + the cost caveats |
| [`knowledge/medallion-on-onelake.md`](knowledge/medallion-on-onelake.md) | Building bronze/silver/gold — per-layer V-Order/file-size/clustering/maintenance + MLV-vs-notebook-vs-dataflow |
| [`knowledge/direct-lake-and-semantic-models.md`](knowledge/direct-lake-and-semantic-models.md) | Building or debugging a semantic model — the two Direct Lake modes, framing, fallback, gold shaping |
| [`knowledge/capacity-finops-and-throttling.md`](knowledge/capacity-finops-and-throttling.md) | Capacity sizing/cost/throttling — SKUs, CU, smoothing/bursting, reservations, isolation, the FinOps playbook |
| [`knowledge/onelake-security-and-governance.md`](knowledge/onelake-security-and-governance.md) | The security model — two planes, RLS/CLS/OLS GA/preview matrix, domains, Purview |
| [`knowledge/fabric-alm-cicd.md`](knowledge/fabric-alm-cicd.md) | CI-CD — Git integration + deployment pipelines + Fabric CLI / fabric-cicd / REST |
| [`knowledge/fabric-2026-capability-map.md`](knowledge/fabric-2026-capability-map.md) | "Is this GA or preview?" — runtimes, NEE, stores, Direct Lake, RTI, AI, ALM (dated; the freshness anchor) |
| [`knowledge/fabric-data-science-and-ai.md`](knowledge/fabric-data-science-and-ai.md) | AI over OneLake + the ML lifecycle — Fabric Data Agents (GA), Operations Agents, AI functions, AutoML, MLflow (cross-workspace), Semantic Link, Copilot, GraphQL + Foundry IQ. Owned by `lakehouse-engineer` (interim, until the v0.2.0 `fabric-data-ai-engineer`). Dated 2026-05-28. |
| [`knowledge/direct-lake-fallback-triage-decision-tree.md`](knowledge/direct-lake-fallback-triage-decision-tree.md) | **Diagnosing** (not choosing) a misbehaving model — the mode-aware **Direct Lake fell-back / errored / empty** triage tree + the **semantic-model refresh/framing failure** triage tree. Complements the *selection* trees in `fabric-decision-trees.md`. Owned by `fabric-semantic-model-engineer` + `fabric-admin`. Dated 2026-06-05. |
| [`knowledge/dax-measures-for-direct-lake.md`](knowledge/dax-measures-for-direct-lake.md) | Authoring or reviewing a **DAX measure on a Direct Lake model** — the everyday-correctness **accuracy spine** (row vs filter context, the implicit-`CALCULATE` **context-transition** trap, `RELATED` in iterators, `KEEPFILTERS` intersect-vs-replace, `REMOVEFILTERS`-not-as-a-table, **no `ALLSELECTED` in an iterator**, `DIVIDE`) + the **Direct-Lake specifics that change WHERE the math lives** (row-level derivation → gold Delta table; calculated columns are **preview/unmaterialized on on-OneLake, unsupported on on-SQL** `[verify-at-use]`; author against `DirectLakeBehavior = Direct Lake only` to surface hidden fallback; unsupported source types break measures at the column level). Restates the **everyday-measures-here / advanced-DAX-to-`power-bi-engineer`** seam (§10). Deep authoring home: [`../power-platform/knowledge/dax-measure-accuracy.md`](../power-platform/knowledge/dax-measure-accuracy.md). Owned by `fabric-semantic-model-engineer`. Dated 2026-06-09. |

---

## 8a. Scenarios bank (enabled — build-out 2026-06-05)

The scenarios bank is **live**: [`scenarios/`](scenarios/) holds dated, scope-tagged, *unverified* engagement narratives (the marketplace 9-field scenario schema; see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)). Surface a matching scenario only as a **secondary** source, always behind the mandatory unverified-scenario preamble ("Based on N unverified scenarios from YYYY-MM tagged [scope] — verify in your environment"), never overriding the cited [`knowledge/`](knowledge/) bank or a `security-reviewer` verdict (§10). Scenarios carry no tenant-identifying info or named CU-cost figures (privacy note in [`scenarios/README.md`](scenarios/README.md)). Fabric ships monthly — every GA/preview-sensitive claim is dated + `[verify-at-use]` (house opinion #9).

The most-likely-to-benefit specialists check the bank when a situation matches: `fabric-admin` (capacity / ALM / security), `fabric-semantic-model-engineer` (Direct Lake), `fabric-architect` (OneLake topology). Current bank: capacity-CU throttling (background-rejection collision), Direct Lake → DirectQuery fallback (RLS forced), OneLake shortcut medallion modeling, deployment-pipeline ALM autobind break. See [`scenarios/README.md`](scenarios/README.md) for the index + promotion path.

---

## 9. Templates in this plugin

| Template | Use for |
|---|---|
| [`templates/fabric-workspace-and-capacity-plan.md`](templates/fabric-workspace-and-capacity-plan.md) | Workspace/domain/capacity topology + sizing + isolation + region/residency |
| [`templates/medallion-lakehouse-spec.md`](templates/medallion-lakehouse-spec.md) | Bronze/silver/gold spec with per-layer optimization |
| [`templates/fabric-ingestion-design.md`](templates/fabric-ingestion-design.md) | Movement method + connector + incremental strategy + schedule |
| [`templates/direct-lake-semantic-model-spec.md`](templates/direct-lake-semantic-model-spec.md) | Direct Lake model: mode, tables, gold requirements, deployment |
| [`templates/fabric-capacity-cost-review.md`](templates/fabric-capacity-cost-review.md) | FinOps review: utilization, rightsizing, isolation, reservation posture |
| [`templates/fabric-alm-runbook.md`](templates/fabric-alm-runbook.md) | Git + deployment-pipeline promotion runbook |

---

## 10. Escalating out of the Microsoft Fabric team — the seams

**`power-platform/power-bi-engineer`** — owns Power BI as a standalone authoring tool: `.pbix`/`.pbit` (via the pbix-mcp), Import/DirectQuery semantic models, **advanced DAX authoring** (calculation groups, reusable measure libraries, perf tuning), PBIP-in-git, report-level deployment/refresh. **This plugin owns the *Fabric storage layer* underneath a semantic model** *and the everyday Direct Lake measures on it*: Direct Lake over OneLake, V-Order gold-table shaping for framing, DirectQuery-fallback avoidance, the lakehouse/warehouse the model reads, and **everyday measure correctness** via [`knowledge/dax-measures-for-direct-lake.md`](knowledge/dax-measures-for-direct-lake.md) (the deep authoring home is the neighbor's [`../power-platform/knowledge/dax-measure-accuracy.md`](../power-platform/knowledge/dax-measure-accuracy.md)). **Litmus test:** *advanced DAX (calculation groups, measure libraries, perf tuning), a visual, or a `.pbix` → power-bi-engineer; an **everyday Direct Lake measure** (sums/ratios/simple time intelligence — authored via `knowledge/dax-measures-for-direct-lake.md`), the Delta tables, the OneLake storage mode, or why Direct Lake fell back → microsoft-fabric.*

**microsoft-fabric ↔ data-platform.** One question decides it: *is this an enterprise Microsoft shop on Fabric capacity (OneLake / Direct Lake / Purview governance)?* If **yes** → `microsoft-fabric`. If the deliverable is a **non-Microsoft, SMB, cost-sensitive, embedded-in-app** dashboard (Cube / Evidence / Metabase / Supabase) → `data-platform`. `data-platform`'s `database-setup-guide` may stand up an Azure SQL / Fabric SQL endpoint as a plain database for an SMB embed, but **enterprise Fabric architecture (lakehouse/warehouse topology, capacity sizing, medallion, FinOps, OneLake security) hands off to `microsoft-fabric`** — and `microsoft-fabric` hands the *embedded-app rendering layer* (JWT embed, CSP, per-viewer-pricing economics) back to `data-platform`. *(This seam is documented reciprocally in [`../data-platform/CLAUDE.md`](../data-platform/CLAUDE.md).)*

**`applied-statistics/applied-statistician`** — "is this Fabric metric movement / anomaly real?" (signal vs noise). This plugin gets the number into Fabric and onto a dashboard; applied-statistics says whether it's real.

**`ravenclaude-core/security-reviewer`** — any auth/secrets/PII change (service principals, OneLake-security roles, tenant settings, connection strings) routes through core's security reviewer (mandatory per the marketplace convention).

**`ravenclaude-core/data-engineer`** — generic (non-Fabric) ELT / dbt / warehouse modeling stays in core; Fabric-specific lives here.

**`azure-cloud`** (when installed) — the Fabric **analytics platform** (OneLake / Lakehouse / Warehouse / Direct Lake / capacity) is this plugin; **raw, non-Fabric Azure data services** used as an app backend (Azure SQL / Cosmos / PostgreSQL Flexible Server / Storage) belong to `azure-cloud` (its `azure-architect` owns the non-Fabric data-tier decision; `network-engineer` wires their Private Endpoints). The Azure capacity + subscription/landing-zone Fabric runs on is also `azure-cloud`. (Reciprocal of [`../azure-cloud/CLAUDE.md`](../azure-cloud/CLAUDE.md) §10.)

**`ravenclaude-core/architect`** — cross-domain boundary adjudication when a question crosses a plugin line.

---

## 11. Bundled MCP — `microsoft-learn` (Microsoft Learn docs); operational Fabric MCP servers are recommend-not-bundle

This plugin **bundles exactly one** MCP server — the **Microsoft Learn MCP Server** — and **recommends (does not bundle)** the two operational Fabric MCP servers. The split is the [`../../docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md) decision table applied honestly: a server is bundled only if it's zero-config + read-only + first-party/well-maintained; a per-tenant / credentialed / write-capable server is recommend-not-bundle.

### 11.0 Bundled — `microsoft-learn` (read-only docs, no auth, no cost)

The plugin declares `microsoft-learn` in `plugin.json`, backed by the official [`microsoftdocs/mcp`](https://github.com/microsoftdocs/mcp) (MIT), reached at the **remote streamable-HTTP** endpoint `https://learn.microsoft.com/api/mcp`. It exposes **three read-only tools** — `microsoft_docs_search`, `microsoft_docs_fetch`, `microsoft_code_sample_search` — that ground answers in **official Microsoft Learn documentation**.

**Why this one bundles (unusually for a Microsoft server):** it is **remote, no-auth, free, read-only** — no per-consumer URL, no credential, no install, no write verb, no metered cost — which is the only Microsoft-ecosystem server that clears the BUNDLE row of the doctrine. Verified 2026-06-05 against [Microsoft Learn MCP Server overview](https://learn.microsoft.com/training/support/mcp) ("no authentication required," "publicly available," "no charge," remote streamable HTTP). `[verify-at-use]` — re-confirm endpoint + tool surface at use; Fabric/Learn ship monthly.

**Consumer prerequisite — none.** It's a remote HTTP endpoint; nothing to install. Claude Code connects when the plugin is enabled (`type: "http"`). **Loud-but-non-fatal:** if the endpoint is unreachable (no network, an egress proxy, or `web-access.yaml` denies `learn.microsoft.com`) the server shows `failed` in `/mcp` and the error surfaces in the `/plugin` Errors tab; Claude Code and all other tools keep working. **If the Learn tools aren't responding, check `/mcp` + the `/plugin` Errors tab and confirm `learn.microsoft.com` is reachable/allow-listed first.** No PATH fallback exists (no local binary — the endpoint *is* the server).

**Which agent owns it?** **All** agents — this plugin's #1 discipline is "cite the capability's GA/preview status with a retrieval date" (house opinion #9), and the Learn MCP is the grounding tool that backs that. **Trigger:** when a Fabric capability's GA/preview status, an API field, a `fab`/KQL/T-SQL detail, or a decision-guide is load-bearing, **call `microsoft_docs_search`/`microsoft_docs_fetch` instead of asserting from memory** (the claim-grounding discipline made operational). `fabric-admin` + `fabric-architect` are the heaviest callers (capability map, decision guides).

**Boundary** — `microsoft-learn` is for **reading official Microsoft documentation + code samples**. It is **NOT** a connection to a Fabric tenant, **NOT** a Fabric automation surface, and **NOT** a substitute for `fab`/REST. For acting against a tenant, use the `fab` CLI / REST path (§11.1) or the recommend-not-bundle operational servers (§11a). See [`NOTICE.md`](NOTICE.md) for attribution.

### 11.1 The `fab` CLI / REST prerequisite (unchanged)

Fabric **automation** is via the **Fabric CLI (`fab`, `pip install ms-fabric-cli`)**, **fabric-cicd**, and the **Fabric REST APIs** (Entra-authenticated). Agents recommend and emit `fab`/REST snippets; the consultant runs them in their own environment with their own credentials. See [`knowledge/fabric-alm-cicd.md`](knowledge/fabric-alm-cicd.md).

### 11a. Recommend-not-bundle — the operational Fabric MCP servers

Two **first-party Microsoft** Fabric MCP servers exist and are genuinely useful, but both are **credentialed and write-capable**, so the doctrine sends them to *recommend, don't bundle* (you can't hardcode a tenant/credential, and a bundled write-capable server interacts with core's command-review Gate 25 `mcp.allowed_servers` allowlist). Verified 2026-06-05; **nothing invented.**

| Server | Disposition | Verified facts (`[verify-at-use]` — public preview, ships monthly) |
|---|---|---|
| **Fabric RTI MCP** ([`microsoft/fabric-rti-mcp`](https://github.com/microsoft/fabric-rti-mcp), MIT) | **recommend-not-bundle** | PyPI `microsoft-fabric-rti-mcp`; `uvx microsoft-fabric-rti-mcp`. **Credentialed** (Azure Identity `DefaultAzureCredential`) + **write-capable** (KQL query *and* ingest, Eventstream create/modify/delete, Activator triggers). **Public Preview.** Owner: `realtime-intelligence-engineer`. Any write verb → `ravenclaude-core/security-reviewer` + the consumer's `mcp.allowed_servers` allowlist. |
| **Fabric MCP** ([`microsoft/mcp` → `servers/Fabric.Mcp.Server`](https://github.com/microsoft/mcp/tree/main/servers/Fabric.Mcp.Server), MIT) | **recommend-not-bundle** | .NET 9 (`fabmcp server start`, or `npx @microsoft/fabric-mcp@latest`). "Local-first" for API specs/schemas/best-practices, **but includes write tools** (`core_create-item`, `datafactory_create-pipeline`, OneLake file upload/delete) → credentialed for live ops. Owner: `fabric-architect` / `lakehouse-engineer`. Same `security-reviewer` + allowlist gate before any write verb. |

**Recommended setup (consumer-run, `[verify-at-use]` the package + version):**
```bash
# Fabric RTI MCP — authenticate first (az login / DefaultAzureCredential); pin the version.
claude mcp add fabric-rti -- uvx microsoft-fabric-rti-mcp   # public preview; verify version at use
```
Default posture: read-only first, secrets stay a **reference** (never a literal), `security-reviewer` sign-off before enabling any mutating verb. Prefer the lower-blast-radius `fab` CLI / REST path (§11.1) when an MCP isn't required (the grounding protocol's "next-easiest defensible path", §5).

---

## Value-add completeness (build-out 2026-06-05)

This is a **Microsoft data-platform** domain, so the technical-runtime tier genuinely applies (unlike pure-advisory verticals). Every value-add menu item is dispositioned honestly below. PR #315 had already consolidated the knowledge decision-trees + `best-practices/` + `templates/` and stubbed the scenarios `README.md`; this build-out closes the net-new gaps (the scenario *files*, runtime-tier dispositioning, the bundled docs MCP) and adds one complementary **diagnostic** decision-tree file.

| # | Item | Disposition |
|---|---|---|
| 1 | **scenarios/ bank** | **BUILT** — 4 dated, scope-tagged engagement narratives matching the pre-existing `scenarios/README.md` index exactly (the files were the net-new gap; #315 created the index + privacy note but not the files): capacity-CU throttling (background-rejection collision → isolate-before-scale), Direct Lake → DirectQuery fallback (Warehouse RLS forced it), OneLake shortcut medallion modeling (shortcut-first), deployment-pipeline ALM autobind break (missing data-source rule). 9-field schema; each volatile fact dated + `[verify-at-use]`; each maps to an existing best-practice rule. Enabled in CLAUDE.md §8a; routed to the most-likely specialist. |
| 2 | **Decision-tree (Mermaid) knowledge** | **BUILT (1 new file, 2 trees, complementing #315)** — `knowledge/direct-lake-fallback-triage-decision-tree.md`: a **Direct Lake misbehaving (fell-back / errored / empty) mode-aware triage** tree + a **semantic-model refresh/framing failure** triage tree. Chosen because #315's consolidated trees are all *selection* trees (lakehouse-vs-warehouse-vs-KQL, Direct Lake vs Import vs DirectQuery, OneLake access, ingestion, capacity-throttle, security-plane, gold-shape) — there was **no diagnostic tree** for "the model is built and misbehaving," which is exactly what 2 of the 4 scenarios hit. Authored as a standalone topic file (the marketplace pattern for a topic tree) so it ships its Mermaid without the dashboard's pre-rendered-SVG pipeline (which lives under `ravenclaude-core/`, out of this plugin's write scope). |
| 3 | **Bundled MCP server** | **BUILT (bundle) + recommend-not-bundle** — §11. **Bundled: the Microsoft Learn MCP Server** (`microsoftdocs/mcp`, remote streamable HTTP `https://learn.microsoft.com/api/mcp`) — the one Microsoft-ecosystem server that clears the zero-config + read-only bar (**no auth, free, read-only, no install**), and uniquely on-mission for a plugin whose #1 discipline is "cite GA/preview with a date." Declared with `mcpServers` + top-level `x-mcpAttribution` (third-party) + `NOTICE.md`. **Recommend-not-bundle:** Fabric RTI MCP (`microsoft-fabric-rti-mcp`) and Fabric MCP (`Fabric.Mcp.Server`) — both first-party Microsoft but **credentialed + write-capable** → documented `claude mcp add` paths + `security-reviewer` gate. All package names/endpoints/verbs verified against Microsoft Learn + the GitHub repos 2026-06-05; nothing invented. |
| 4 | **LSP server** | **N-A** — Fabric work is authored in PySpark notebooks / T-SQL / KQL / TMDL / `fab` CLI, not a host source language with a clean, stable, installable on-`PATH` LSP binary this plugin could point an `.lsp.json` at (the way backend-engineering ships pyright/tsserver/gopls). The artifacts live in the consumer's Fabric tenant, not a local repo the agent edits with go-to-definition. Honest N-A; the bundled Learn MCP + the `fab`/REST snippets cover the code-intelligence need. |
| 5 | **Runnable script (`scripts/`)** | **BUILT** — `scripts/fabric_capacity_calc.py` (stdlib only, Python 3.8+, ruff-clean): `sku-fit` (smallest F-SKU for an *average* CU draw + headroom + smoothing/burst note), `smoothing` (CU-seconds → smoothed per-window draw, so a "scary" peak's real fit is visible), `isolation` (shared vs isolate-the-noisy-workload by required CU — house opinion #5). **No prices baked in** (repo rule + Fabric pricing is region/time-volatile); CU ladder is a *capability* figure from Microsoft Learn, cost left to the Azure Pricing Calculator. A calculator, not a data source — every input is user-supplied. Backs the FinOps playbook + the capacity-throttling scenario. |
| 6 | **bin/ executables / monitors / output-styles / settings / themes** | **N-A** — no compiled/installed binary warranted (the single stdlib script + advisory hook + skills cover the surface); nothing to *watch* (the plugin is advisory, not a running process); output is Markdown deliverables governed by the §6 Output Contract + the cross-plugin Structured Output Protocol; no Fabric-specific tool-permission surface beyond `ravenclaude-core`'s. |
| 7 | **skills / hooks / commands / templates** | **SUFFICIENT** — 5 skills, 1 advisory anti-pattern hook (`check-fabric-anti-patterns.sh`, 4 grep-able house-opinion checks), 5 commands, 6 templates already cover topology / medallion / ingestion / Direct Lake / capacity-cost / ALM. The new scenarios bank + diagnostic tree + capacity script extend reach without a new agent (team-growth-as-knowledge house rule). No clear gap this round. |
| 8 | **CHANGELOG.md / NOTICE.md** | **CHANGELOG UPDATED** (new top entry for this build-out; the existing file stopped at `0.1.0`, brought current). **NOTICE.md BUILT** — required now that a third-party (Microsoft Learn MCP) server is bundled; documents source/license/endpoint/read-only verbs + the no-prerequisite + loud-but-non-fatal failure path. |

---

## 12. References

- Domain-neutral team constitution: [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md)
- Structured Output Protocol (upstream): [`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)
- The Power BI seam: [`../power-platform/CLAUDE.md`](../power-platform/CLAUDE.md) + its `power-bi-engineer` agent
- The data-platform router: [`../data-platform/CLAUDE.md`](../data-platform/CLAUDE.md)
- Bundled-MCP doctrine: [`../../docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md)
- Scenario-retrieval pattern + 9-field schema: [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)
- Build provenance: [`../../docs/microsoft-fabric-plugin-analysis.md`](../../docs/microsoft-fabric-plugin-analysis.md) + [`../../docs/microsoft-fabric-build-plan.md`](../../docs/microsoft-fabric-build-plan.md)
