# azure-cloud — next-most-useful-addition analysis + buildout plan (round 3)

**Date:** 2026-05-28
**Author:** Autonomous repo-analysis pass, round 3 (Claude Opus 4.7, overnight loop)
**Status:** Decision + research synthesis + buildout plan. §6 carries the expert review + gap analysis + score; §7 is the plan as revised by that review.
**Grounding:** every Azure claim is grounded in Microsoft Learn, retrieved 2026-05-28 via the Microsoft Learn MCP server. Source URLs inline.

---

## 0. TL;DR

Rounds 1-2 shipped `microsoft-fabric` (data) and `claude-app-engineering` (AI). The remaining hole in Matt's Microsoft stack is the **Azure cloud infrastructure layer underneath all of it** — IaC, landing zones, identity (Entra), app hosting, integration, governance, cost, observability. Fabric runs on Azure capacity; Power Platform integrates Azure (Logic Apps, Key Vault, Functions); Claude apps deploy to Azure / Foundry; web apps host on Azure Static Web Apps / Container Apps. A new **`azure-cloud`** plugin completes the stack. The roadmap deferred it only on **priority** (other domains ranked higher), not validity — with those domains now shipped, it rises to the top. It scores high on Matt-edge, active fit, surface area, and grounding-now; the one real risk is **cross-plugin seam density** (Logic Apps↔Power Automate, Azure data↔Fabric, Azure host↔claude-app-engineering, infra↔core), which §6's review is asked to stress-test.

---

## 1. Re-scored candidate map (after rounds 1-2)

| Candidate | Matt-edge | Active fit | Differentiation | Surface | Readiness | Grounding-now | Verdict |
|---|---|---|---|---|---|---|---|
| **`azure-cloud`** | 5 | 5 | 3 | 5 | 4 | 5 | **BUILD — winner** |
| `salesforce` | 2 | 2 | 2 | 5 | 3 | 3 | Defer — still competes with the Microsoft brand |
| Deepen `web-design` knowledge | 3 | 4 | 3 | 3 | 5 | 4 | Bonus/maintenance, not a new domain |
| `microsoft-365-copilot` (declarative agents / Graph / Teams apps) | 3 | 3 | 3 | 3 | 3 | 5 | Candidate for a later round; partial overlap with PP copilot-studio |
| Backfill scenario frontmatter (older plugins) | — | — | — | — | 5 | — | Maintenance task, queue separately |

`azure-cloud` differentiation is "3" (generic Azure tooling exists; most Claude users do AWS) but every other axis is ≥4, and it is the load-bearing foundation under three plugins already shipped this loop.

---

## 2. The architecture decision: new plugin vs. core skills

The contestable call (first thing §6 stress-tests), because the roadmap flagged "overlap with core backend + Fabric admin." **Decision: new plugin**, with the same justification that cleared `microsoft-fabric/fabric-architect` in round 1.

- **Domain-distinct?** Yes. `ravenclaude-core`'s `backend-coder`/`architect` are domain-neutral generalists. Azure landing zones, Bicep/AVM, Entra workload identity federation, the compute-service decision, Azure governance — these are deep operational craft a generalist core agent does **not** carry. This is exactly the "the domain carries operational craft the core agent genuinely lacks → ship an agent" branch of the house rule (the same branch `power-platform/dataverse-architect` and `fabric-architect` took).
- **≥3 agents?** Six (§4).
- **The "could core/architect + a skill match it?" test** — for the cross-cutting *decision* surfaces (compute selection, IaC-tool choice) a skill could plausibly carry the priors; but the *doing* surfaces (authoring Bicep/AVM modules, designing Entra federation + PIM, wiring Service Bus/Event Grid/APIM, tuning Log Analytics cost) are operational specialist work, not a decision tree. The plugin ships agents for the doing and folds the pure decisions into knowledge those agents traverse. **No security-reviewer/architect clone** — escalates to core.
- **The seam density is the real risk** (§5), not the new-plugin decision.

---

## 3. Deep dive — the Azure surface (research synthesis)

All claims grounded in Microsoft Learn, retrieved 2026-05-28.

### 3.1 Landing zones & governance (CAF Ready)
**Azure landing zones** = the platform foundation: a **management-group hierarchy** (keep it flat, 3-4 levels; `Platform` + `Landing Zones` + `Sandbox`/`Decommissioned`) with **Azure Policy** enforced down the tree, **subscription-per-environment** (dev/test/prod as separate subscriptions under archetype MGs like `corp`/`online`, *not* separate MGs per environment), **subscription vending**, **policy-driven governance + subscription democratization**, RBAC at subscription/resource-group scope (not MG, except platform teams via PIM), a **tagging strategy** (owner/cost-center/environment/application), and universal **RBAC + Cost Management + Defender for Cloud + Network Watcher**. ([CAF Ready](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/), [management groups](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/design-area/resource-org-management-groups))

### 3.2 IaC: Bicep vs Terraform (+ AVM)
**Bicep** = Azure-only, no state file (incremental deployment), **`what-if`** preview, **preflight policy validation** (fails before deploy), portal export, `az bicep`/`az deployment`. **Terraform** = multi/hybrid-cloud, **state** (back up + secure; remote state in Azure Storage), `terraform plan`/`apply`, providers, `aztfexport`. **Azure Verified Modules (AVM)** = Microsoft-maintained reusable modules for **both** Bicep and Terraform, WAF-aligned. **Deployment stacks** manage a resource group/sub/MG as one lifecycle unit. ([Bicep vs Terraform](https://learn.microsoft.com/azure/developer/terraform/comparing-terraform-and-bicep), [AVM](https://learn.microsoft.com/community/content/azure-verified-modules))

### 3.3 Compute decision
App Service (PaaS web), **Container Apps** (serverless containers, scale-to-zero, Dapr, the flexible default), **Functions** (event-driven, Consumption/Flex Consumption scale-to-zero), **Static Web Apps** (SPA + serverless API, git-deployed, global), **AKS** (full Kubernetes API; only when you need it), Container Instances, Batch. Scale-to-zero + ops-burden + the need for the Kubernetes API drive the choice. ([choose a compute service](https://learn.microsoft.com/azure/architecture/guide/technology-choices/compute-decision-tree), [choose a container service](https://learn.microsoft.com/azure/architecture/guide/choose-azure-container-service))

### 3.4 Identity (Entra)
**App registration** (external/non-Azure workloads) vs **managed identity** (Azure-hosted; system- or user-assigned — Azure manages the creds) vs **workload identity federation** (passwordless: external IdP like GitHub Actions / Kubernetes exchanges its token for an Entra token — **no secrets to rotate**). **RBAC** scoped least-privilege; **PIM** for just-in-time elevation (no standing Owner). **Entra External ID** = the CIAM product (**Azure AD B2C is end-of-sale May 2025** → External ID is the path). **Entra Agent ID** = identities for AI agents (new). ([workload identity federation](https://learn.microsoft.com/entra/workload-id/workload-identity-federation), [what is Entra](https://learn.microsoft.com/entra/fundamentals/what-is-entra))

### 3.5 Integration
**Logic Apps** (IT/dev, Azure subscription, Consumption/Standard, Azure Policy to restrict connectors) vs **Power Automate** (O365 makers, per-user license, DLP) — the seam. **Service Bus** (commands/messaging, Premium for Event Grid integration + Peek-Lock), **Event Grid** (events, reactive), **Event Hubs** (streaming), **API Management** (publish/secure APIs), **Functions** (serverless orchestration glue). Crossover patterns (Service Bus → Event Grid → Function to drain idle queues). ([integration architecture](https://learn.microsoft.com/azure/architecture/integration/integration-start-here), [Logic Apps vs Power Automate](https://learn.microsoft.com/azure/azure-functions/functions-compare-logic-apps-ms-flow-webjobs))

### 3.6 Observability & FinOps
**Azure Monitor** + **Log Analytics** (workspace-based) + **Application Insights** (OpenTelemetry; **workspace-based**). Cost is dominated by **Log Analytics ingestion + retention** → control with **sampling**, **Basic Logs** tables, **commitment tiers**, **daily caps**, retention tuning. **Cost Management**: budgets + cost alerts per subscription, daily cost-analysis emails, CSV exports, **capacity reservations**. ([Monitor cost](https://learn.microsoft.com/azure/azure-monitor/fundamentals/cost-usage), [cost optimization in Monitor](https://learn.microsoft.com/azure/azure-monitor/fundamentals/best-practices-cost))

### 3.7 Deployment / CI-CD
GitHub Actions / Azure DevOps with **workload identity federation** (passwordless service connections), AVM in pipelines, `what-if`/`plan` gates, environments + approvals. ([WIF for pipelines](https://learn.microsoft.com/entra/workload-id/workload-identity-federation))

---

## 4. Plugin scope (the buildout)

A domain-specialist team in the `microsoft-fabric` mold. Requires `ravenclaude-core@>=0.7.0`.

### 4.1 Roster — 6 agents
| Agent | Owns | Spawn when |
|---|---|---|
| **`azure-architect`** | landing zones / CAF, management-group + subscription topology, WAF, region/residency, the cross-service "which Azure service?" adjudication | "design our Azure landing zone"; "how should we organize subscriptions?"; "which Azure service for X?" |
| **`bicep-iac-engineer`** | Bicep (+ Terraform azurerm), AVM, modules, what-if/plan, deployment stacks, preflight policy, state | "write the Bicep/Terraform for X"; "Bicep or Terraform?"; "set up AVM modules" |
| **`entra-identity-engineer`** | Entra app reg vs managed identity vs **workload identity federation**, RBAC, PIM, **Entra External ID** (CIAM), Entra Agent ID | "set up passwordless auth for CI/CD"; "managed identity or app registration?"; "CIAM for our app" |
| **`app-platform-engineer`** | the **compute decision** (App Service / Container Apps / Functions / Static Web Apps / AKS), hosting/scaling/slots | "where should this app run?"; "App Service or Container Apps?"; "host this on Azure" |
| **`integration-engineer`** | Logic Apps (+ the Power Automate seam), Service Bus, Event Grid, Event Hubs, API Management, Functions glue | "connect these systems"; "Service Bus or Event Grid?"; "publish this API" |
| **`azure-ops-engineer`** | Monitor/Log Analytics/App Insights/OpenTelemetry observability, **cost/FinOps**, governance (Policy/RBAC/tags/Defender), CI-CD deploy | "my Azure bill is too high"; "add observability"; "set up CI/CD" |

*(No security-reviewer/architect clone — identity/security design + cross-domain architecture escalate to core per §2.)*

### 4.2 Knowledge bank — 8 docs (dated, cited)
1. `azure-landing-zones-and-governance.md` 2. `azure-iac-decision-and-bicep.md` 3. `azure-compute-decision-tree.md` (Mermaid) 4. `entra-identity-and-access.md` 5. `azure-integration-decision.md` (Mermaid) 6. `azure-observability-and-finops.md` 7. `azure-deployment-cicd.md` 8. `azure-2026-capability-map.md` (the dated freshness anchor — AVM, deployment stacks, B2C EOL → External ID, Entra Agent ID, Flex Consumption, Container Apps).

### 4.3 Templates — 6
`azure-landing-zone-plan.md`, `iac-deployment-spec.md`, `azure-architecture-spec.md`, `entra-identity-design.md`, `azure-cost-and-observability-review.md`, `azure-cicd-runbook.md`.

### 4.4 Hook (advisory; `AZURE_STRICT=1` to block)
`check-azure-anti-patterns.sh` on `.bicep`/`.tf`/`.json`/`.yml`/`.yaml`:
1. Hardcoded secret in IaC (`password=`/`accountKey=`/`client_secret`/SAS) → Key Vault / managed identity.
2. `0.0.0.0/0` or `publicNetworkAccess: 'Enabled'` / `*` source → public exposure.
3. `Owner`/`Contributor` role assignment at subscription/management-group scope in IaC → over-privilege.
4. Hardcoded subscription/tenant GUID in IaC → parameterize.

### 4.5 House opinions — 14 (final in CLAUDE.md §3)
Landing-zone-first · IaC-or-it-didn't-happen (what-if before apply, no prod click-ops) · Bicep-for-Azure-only/Terraform-for-multi-cloud (+ AVM) · passwordless by default (managed identity / workload identity federation; secrets in Key Vault) · least-privilege + PIM (no standing Owner) · pick compute from the tree · tag everything · budgets+alerts per subscription · observability = OpenTelemetry + workspace-based App Insights + sampling · Logic-Apps-vs-Power-Automate seam · Defender + Policy on by default · don't fork core's review roles · honor the neighbors (Fabric/Power-Platform/claude-app-engineering) · cite the capability with a retrieval date.

### 4.6 Seams (the key risk — documented bidirectionally)
- **`power-platform/flow-engineer`** — Logic Apps (Azure/IT/dev) vs Power Automate (O365/makers): the documented Microsoft seam.
- **`microsoft-fabric`** — Fabric analytics platform → fabric; raw non-Fabric Azure data services (Azure SQL/Cosmos/Storage) as an app backend → here/core.
- **`claude-app-engineering`** — `app-platform-engineer` provisions the Azure host (Container Apps/Functions/Foundry); claude-app-engineering builds the Claude integration.
- **`web-design`** — `app-platform-engineer` provisions Static Web Apps; web-design builds the site.
- **`ravenclaude-core/security-reviewer`** (mandatory) — all identity/secrets/network-security design.
- **`ravenclaude-core/architect`** — cross-domain/whole-system architecture.
- **`ravenclaude-core/backend-coder`/`frontend-coder`** — the app code that runs on the infra.

---

## 5. Risks & open questions (pre-review)
- **R1 — seam density.** More cross-plugin seams than any prior plugin (PP, Fabric, claude-app-eng, web-design, core). The risk is Team-Lead misroute. *(Review: are the seams clean, and which need reciprocal edits in the neighbor's CLAUDE.md?)*
- **R2 — overlap with core backend/architect.** Is the new-plugin justification solid, or should some agents be core skills? *(Review.)*
- **R3 — roster size / foldability.** 6 agents — is `integration-engineer` or `app-platform-engineer` foldable into `azure-architect`? *(Review.)*
- **R4 — currency.** Azure ships constantly (B2C EOL, AVM, Entra Agent ID); the dated capability map + Researcher sweep mitigate.
- **R5 — no bundled MCP.** v0.1.0 documents `az` CLI / Bicep / Terraform as prerequisites; bundles nothing.

---

## 6. Expert review + gap analysis + score

Two independent reviewers: a **principal Azure architect** and the **RavenClaude marketplace-conventions architect**. Both **Approve-with-changes**; the new-plugin decision endorsed without dissent.

### 6.1 Scores (1-5)

| Dimension | Score | Reviewer |
|---|---|---|
| New-plugin justification | 4 | conventions |
| Surface coverage | 3 | domain |
| Technical accuracy (as drafted in §3) | 4 | domain |
| Roster design | 3.5 | domain |
| Knowledge-bank design | 3.5 | domain |
| House-opinions / hook quality | 3.5 | domain |
| Seam cleanliness | 3 | conventions |
| Convention compliance | 4 | conventions |
| Scope realism for v0.1.0 | 3 | conventions |

**Composite ~3.5/5 — Approve-with-changes.** Surface coverage (3, networking gap) and seam cleanliness (3, reciprocity claimed-not-delivered) drive the must-fix list.

### 6.2 Must-fix (folded into §7)

1. **[domain] Networking is unowned.** VNet / Private Endpoints + Private DNS / hub-spoke / Front Door / App Gateway / WAF / Azure Firewall / egress are first-order — and the hook's `publicNetworkAccess`/`0.0.0.0/0` checks assume a posture nothing owns. → add a **7th agent `network-engineer`** + a `azure-networking-and-connectivity.md` knowledge doc; move CI/CD out of `azure-ops-engineer` into `bicep-iac-engineer` (ops was carrying four jobs).
2. **[domain] Private-endpoint / deny-public-by-default is missing from house opinions.** → add "private-by-default for PaaS data planes (Key Vault/Storage/SQL/Cosmos) via Private Endpoint + Private DNS; public access is an explicit, justified exception."
3. **[conventions] Reciprocal seam edits are claimed (§4.6) but don't exist.** Ship all four in this PR: (1) `power-platform/CLAUDE.md` — trim the flow-engineer "vs Logic Apps" claim + add the reciprocal pointer (**#1 risk — collides with a live decision claim**); (2) `claude-app-engineering/CLAUDE.md` §10 — add the Azure-host seam; (3) `microsoft-fabric/CLAUDE.md` §10 — raw non-Fabric Azure data services route here/core; (4) `web-design/agents/web-architect.md` — inline pointer that azure-cloud provisions Static Web Apps.
4. **[conventions] Three-way version sync** — catalog `metadata.version` 0.28.0 → **0.29.0** + catalog `plugins[]` entry + plugin.json all at parity.

### 6.3 Should-fix / corrections (folded into §7 + the knowledge bank)

- **House opinions expand to 16**: add **zone-redundant-by-default for prod** (AZ SKUs + paired-region BCDR) and **CAF naming + tagging standard** (`abbr-workload-env-region` naming; owner/cost-center/env/app tags). Add a hook check for non-conforming names + TLS/HTTPS-off + storage `allowBlobPublicAccess`/`allowSharedKeyAccess` + Terraform local backend; broaden secret detection to `connectionString`/`primaryKey`.
- **`azure-architect`** also owns the **non-Fabric data-tier decision** (Azure SQL vs Cosmos vs PostgreSQL Flexible Server + Private Endpoint wiring) — currently vague.
- **Audience tags:** `azure-architect` + `azure-ops-engineer` carry `[consultant, dev]` (landing-zone design + cost reviews are consultant deliverables); the other five `[dev]`. Full scenario frontmatter on all 7 (don't add a third "pending backfill" debt).
- **`azure-architect` foldability** — explicitly cleared (kept as an agent): CAF landing-zone + management-group/subscription-vending operational craft exceeds a generalist + decision tree, matching `fabric-architect`'s round-1 clearance.
- **§3 accuracy:** B2C end-of-sale **May 1 2025** but **existing tenants supported ~to 2030**, **B2C P2 retired ~March 2026**, HSC coexistence for migration → External ID. "Container Apps as the flexible default" is **RavenClaude's opinion**, not a Microsoft statement. **Flex Consumption** constraints: no deployment slots, one app per plan, no in-place migration from Consumption, AZ needs ≥2 always-ready instances. Bicep has **no separate user-managed state file** (it keeps deployment history + server-side state). **Deployment Stacks are GA** (`denySettings`) — the Bicep answer to Terraform lifecycle; **Blueprints is deprecated → Deployment Stacks + Azure Policy / ALZ**. Name the ALZ archetypes (`corp`/`online`/`sandbox`/`decommissioned`) + the **AVM ALZ accelerator + subscription-vending modules** (both Bicep + Terraform).

---

## 7. Revised plan (per §6)

**Build it, with these locked-in changes.**

### 7.1 Roster — 7 agents
1. **`azure-architect`** `[consultant, dev]` — landing zones/CAF, MG + subscription topology (+ subscription-vending AVM), WAF incl. reliability/zone-redundancy, the cross-service "which Azure service?" adjudication, and the **non-Fabric data-tier decision**.
2. **`bicep-iac-engineer`** `[dev]` — Bicep (+ Terraform azurerm), AVM, **Deployment Stacks**, what-if/plan, state, preflight policy, **+ CI/CD (GitHub Actions/Azure DevOps + workload identity federation)**.
3. **`entra-identity-engineer`** `[dev]` — app reg / managed identity / **workload identity federation**, RBAC, PIM, **Entra External ID** (B2C nuances), Entra Agent ID.
4. **`network-engineer`** `[dev]` *(new)* — VNet/subnets, **Private Endpoints + Private DNS**, hub-spoke/vWAN, NSG/UDR, Front Door/App Gateway/WAF, Azure Firewall/egress, DDoS, deny-public-by-default.
5. **`app-platform-engineer`** `[dev]` — the **compute decision** (App Service/Container Apps/Functions Flex/Static Web Apps/AKS), hosting/scaling/slots; the Claude-app Azure-host seam.
6. **`integration-engineer`** `[dev]` — Logic Apps (+ the Power Automate seam), Service Bus, Event Grid, Event Hubs, APIM, Functions glue.
7. **`azure-ops-engineer`** `[consultant, dev]` — Monitor/Log Analytics/App Insights/OpenTelemetry observability + **FinOps** + governance (Policy/RBAC/tags/Defender). *(Most likely to split in v0.2.0.)*

### 7.2 Knowledge bank — 9 docs (dated + cited; §6.3 corrections baked in)
landing-zones-and-governance, iac-decision-and-bicep, compute-decision-tree, entra-identity-and-access, **azure-networking-and-connectivity** *(new)*, integration-decision, observability-and-finops, deployment-cicd, 2026-capability-map.

### 7.3 House opinions — 16; Hook — 6 checks
Per §4.5 + §6.3 (adds private-by-default, zone-redundant prod, CAF naming/tagging). Hook: hardcoded secret (incl. connectionString/primaryKey), public exposure (0.0.0.0/0 / publicNetworkAccess Enabled / allowBlobPublicAccess / allowSharedKeyAccess), Owner/Contributor at sub/MG scope, TLS/HTTPS-off, hardcoded sub/tenant GUID, Terraform local backend.

### 7.4 Seams — bidirectional, shipped in this PR
The four reciprocal edits from §6.2(3), with the conventions reviewer's litmus wording. Logic-Apps↔Power-Automate: *citizen maker + per-user/DLP → flow-engineer; Azure-subscription + Bicep/Terraform + Azure Policy → integration-engineer*. Azure-host↔claude-app-engineering: *prompt/caching/tool/eval → claude-app-engineering; "where on Azure + how provisioned" → app-platform-engineer*.

### 7.5 Build mechanics
`requires: ravenclaude-core@>=0.7.0`; catalog `metadata.version` 0.28.0→0.29.0 + three-way parity; `CHANGELOG.md` at `[0.1.0]`; scenario frontmatter on all 7; advisory hook; standard subdirs already allow-listed; regenerate `repo-guide.html`; update `architecture.md` + root `README.md`; the four reciprocal seam edits (each bumps its neighbor's version). No NOTICE/MCP (documents the `az` CLI / Bicep / Terraform prerequisite).

---

## 8. Sources
Microsoft Learn, retrieved 2026-05-28: [CAF Ready / landing zones](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/), [management groups](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/design-area/resource-org-management-groups), [Bicep vs Terraform](https://learn.microsoft.com/azure/developer/terraform/comparing-terraform-and-bicep), [Azure Verified Modules](https://learn.microsoft.com/community/content/azure-verified-modules), [choose a compute service](https://learn.microsoft.com/azure/architecture/guide/technology-choices/compute-decision-tree), [choose a container service](https://learn.microsoft.com/azure/architecture/guide/choose-azure-container-service), [workload identity federation](https://learn.microsoft.com/entra/workload-id/workload-identity-federation), [what is Entra](https://learn.microsoft.com/entra/fundamentals/what-is-entra), [integration architecture](https://learn.microsoft.com/azure/architecture/integration/integration-start-here), [Logic Apps vs Power Automate](https://learn.microsoft.com/azure/azure-functions/functions-compare-logic-apps-ms-flow-webjobs), [Azure Monitor cost](https://learn.microsoft.com/azure/azure-monitor/fundamentals/cost-usage).
