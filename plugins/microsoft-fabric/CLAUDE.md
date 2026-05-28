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

---

## 8a. Scenarios bank — TODO (planned)

Not yet enabled. Per the marketplace pattern, enable the scenarios bank when the first real engagement scenario surfaces via `/wrap`: create `plugins/microsoft-fabric/scenarios/` with a `README.md` (copy from `plugins/power-platform/scenarios/README.md`), add the scenario-retrieval inline-prior block to the relevant agents, and remove this block.

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

**`power-platform/power-bi-engineer`** — owns Power BI as a standalone authoring tool: `.pbix`/`.pbit` (via the pbix-mcp), Import/DirectQuery semantic models, DAX measure authoring, PBIP-in-git, report-level deployment/refresh. **This plugin owns the *Fabric storage layer* underneath a semantic model**: Direct Lake over OneLake, V-Order gold-table shaping for framing, DirectQuery-fallback avoidance, and the lakehouse/warehouse the model reads. **Litmus test:** *if the question is about a measure, a visual, or a `.pbix` → power-bi-engineer; if it's about the Delta tables, the OneLake storage mode, or why Direct Lake fell back → microsoft-fabric.*

**microsoft-fabric ↔ data-platform.** One question decides it: *is this an enterprise Microsoft shop on Fabric capacity (OneLake / Direct Lake / Purview governance)?* If **yes** → `microsoft-fabric`. If the deliverable is a **non-Microsoft, SMB, cost-sensitive, embedded-in-app** dashboard (Cube / Evidence / Metabase / Supabase) → `data-platform`. `data-platform`'s `database-setup-guide` may stand up an Azure SQL / Fabric SQL endpoint as a plain database for an SMB embed, but **enterprise Fabric architecture (lakehouse/warehouse topology, capacity sizing, medallion, FinOps, OneLake security) hands off to `microsoft-fabric`** — and `microsoft-fabric` hands the *embedded-app rendering layer* (JWT embed, CSP, per-viewer-pricing economics) back to `data-platform`. *(This seam is documented reciprocally in [`../data-platform/CLAUDE.md`](../data-platform/CLAUDE.md).)*

**`applied-statistics/applied-statistician`** — "is this Fabric metric movement / anomaly real?" (signal vs noise). This plugin gets the number into Fabric and onto a dashboard; applied-statistics says whether it's real.

**`ravenclaude-core/security-reviewer`** — any auth/secrets/PII change (service principals, OneLake-security roles, tenant settings, connection strings) routes through core's security reviewer (mandatory per the marketplace convention).

**`ravenclaude-core/data-engineer`** — generic (non-Fabric) ELT / dbt / warehouse modeling stays in core; Fabric-specific lives here.

**`azure-cloud`** (when installed) — the Fabric **analytics platform** (OneLake / Lakehouse / Warehouse / Direct Lake / capacity) is this plugin; **raw, non-Fabric Azure data services** used as an app backend (Azure SQL / Cosmos / PostgreSQL Flexible Server / Storage) belong to `azure-cloud` (its `azure-architect` owns the non-Fabric data-tier decision; `network-engineer` wires their Private Endpoints). The Azure capacity + subscription/landing-zone Fabric runs on is also `azure-cloud`. (Reciprocal of [`../azure-cloud/CLAUDE.md`](../azure-cloud/CLAUDE.md) §10.)

**`ravenclaude-core/architect`** — cross-domain boundary adjudication when a question crosses a plugin line.

---

## 11. The `fab` CLI / REST prerequisite (no bundled MCP at v0.1.0)

Unlike `power-platform` (which bundles pbix-mcp), this plugin **does not bundle an MCP server**. Fabric automation is via the **Fabric CLI (`fab`, `pip install ms-fabric-cli`)**, **fabric-cicd**, and the **Fabric REST APIs** (Entra-authenticated). Agents recommend and emit `fab`/REST snippets; the consultant runs them in their own environment with their own credentials. See [`knowledge/fabric-alm-cicd.md`](knowledge/fabric-alm-cicd.md). If a stable community Fabric MCP emerges, evaluate bundling it in a later version.

---

## 12. References

- Domain-neutral team constitution: [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md)
- Structured Output Protocol (upstream): [`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)
- The Power BI seam: [`../power-platform/CLAUDE.md`](../power-platform/CLAUDE.md) + its `power-bi-engineer` agent
- The data-platform router: [`../data-platform/CLAUDE.md`](../data-platform/CLAUDE.md)
- Build provenance: [`../../docs/microsoft-fabric-plugin-analysis.md`](../../docs/microsoft-fabric-plugin-analysis.md) + [`../../docs/microsoft-fabric-build-plan.md`](../../docs/microsoft-fabric-build-plan.md)
