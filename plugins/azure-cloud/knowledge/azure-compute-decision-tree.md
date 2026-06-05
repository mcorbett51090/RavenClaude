# Decision tree: which Azure compute?

**Last reviewed:** 2026-05-28 · **Confidence:** high ([compute decision](https://learn.microsoft.com/azure/architecture/guide/technology-choices/compute-decision-tree), [container service](https://learn.microsoft.com/azure/architecture/guide/choose-azure-container-service), retrieved 2026-05-28).
**Owner:** `app-platform-engineer` (+ `azure-architect` for the cross-service call).

```mermaid
flowchart TD
    A[Host an app on Azure] --> S{Static SPA + simple API?}
    S -->|Yes| SWA[Static Web Apps<br/>git-deployed, global, managed Functions API]
    S -->|No| E{Event-driven, sporadic/spiky, scale-to-zero?}
    E -->|Yes| F[Azure Functions<br/>Flex Consumption]
    E -->|No| K{Need the Kubernetes API,<br/>service mesh, GPU pools, multi-workload isolation?}
    K -->|Yes| AKS[AKS]
    K -->|No| C{Containerized + want serverless scale,<br/>Dapr, traffic splitting?}
    C -->|Yes| CA[Container Apps]
    C -->|No| AS[App Service<br/>PaaS web app]
```

## The services
| Service | Pick when | Scale-to-zero | Notes |
|---|---|---|---|
| **Static Web Apps** | SPA (React/Angular/Vue/Blazor) + light serverless API, git-deployed | n/a | global CDN; managed Functions or bring-your-own Functions |
| **Azure Functions** | event-driven, sporadic/spiky | **yes** (Consumption / Flex Consumption) | Flex Consumption is the recommended serverless plan — but **no deployment slots, one app per plan, no in-place migration from Consumption, AZ needs ≥2 always-ready instances** |
| **Container Apps** | containers, serverless scale, Dapr, traffic-split/canary | **yes** | RavenClaude's flexible default for containers (Microsoft's guide doesn't crown a default); single environment = one security boundary |
| **App Service** | straightforward HTTP web app/API, deployment slots | no | Web App for Containers is an App Service feature |
| **AKS** | need the Kubernetes API, service mesh, GPU node pools, deny-by-default network policy, multi-workload isolation | partial (user node pools) | most control, most ops; ≥6 nodes for prod |

**Trade-off:** AKS = most control + most ops; Container Apps / App Service = PaaS simplicity. Choose per-service in a composition — Functions for event-driven pieces, Container Apps/AKS for core services. (House opinion #7.)

## Non-Fabric data tier (owned by `azure-architect`)
For an app backend (not Fabric analytics): **Azure SQL** (relational, T-SQL), **Cosmos DB** (NoSQL/global/vector), **PostgreSQL/MySQL Flexible Server** (OSS relational). Wire all data PaaS via **Private Endpoint + Private DNS** with `publicNetworkAccess` Disabled (house opinion #6 — see [`azure-networking-and-connectivity.md`](azure-networking-and-connectivity.md)). Fabric analytics data → `microsoft-fabric` (the seam).

## Reliability
**Zone-redundant by default for prod** where the SKU supports it (house opinion #8).

> The Claude-app Azure host (Container Apps / Functions / Foundry) is provisioned here; the Claude app itself is `claude-app-engineering` (the seam — see [`../CLAUDE.md`](../CLAUDE.md) §10).

---

## Decision Tree: Azure Compute — selecting a host for an app workload

**When this applies:** The user asks "where should this run?" / "which Azure compute for X?" / "should this be on AKS?" — i.e. a workload needs a host and the observable inputs are its shape (static SPA, event-driven/spiky, containerized, plain HTTP web app) and whether it needs the Kubernetes API, a service mesh, GPU node pools, or multi-workload isolation. Not for the data tier (Azure SQL / Cosmos / PostgreSQL — `azure-architect`) and not for the AI hosting layer (Foundry — [`azure-ai-foundry.md`](azure-ai-foundry.md)).

**Last verified:** 2026-05-30 against Microsoft's [compute decision tree](https://learn.microsoft.com/azure/architecture/guide/technology-choices/compute-decision-tree) + [choose an Azure container service](https://learn.microsoft.com/azure/architecture/guide/choose-azure-container-service) (the same sources as the header, re-confirmed).

```mermaid
flowchart TD
    A[Host an app on Azure] --> S{Static SPA + simple API?}
    S -->|Yes| SWA[Static Web Apps<br/>git-deployed, global, managed Functions API]
    S -->|No| E{Event-driven, sporadic/spiky, scale-to-zero?}
    E -->|Yes| F[Azure Functions<br/>Flex Consumption]
    E -->|No| K{Need the Kubernetes API,<br/>service mesh, GPU pools, multi-workload isolation?}
    K -->|Yes| AKS[AKS]
    K -->|No| C{Containerized + want serverless scale,<br/>Dapr, traffic splitting?}
    C -->|Yes| CA[Container Apps]
    C -->|No| AS[App Service<br/>PaaS web app]
```

**Rationale per leaf:**

- _Static Web Apps_ — a SPA (React/Angular/Vue/Blazor) + light serverless API is git-deployed and globally distributed with a managed (or bring-your-own) Functions API; no separate compute to operate.
- _Azure Functions (Flex Consumption)_ — event-driven, sporadic/spiky work wants scale-to-zero so you don't pay for idle; Flex Consumption is the recommended serverless plan. **requires:** AZ resilience needs ≥2 always-ready instances; no deployment slots, one app per plan, no in-place migration from Consumption.
- _AKS_ — terminates here only when a Kubernetes-specific need is present (the Kubernetes API, service mesh, GPU node pools, deny-by-default network policy, multi-workload isolation); it is the most control and the most ops (≥6 nodes for prod).
- _Container Apps_ — containerized work wanting serverless scale, Dapr, or traffic-split/canary without operating Kubernetes; the house default for containers.
- _App Service_ — a straightforward HTTP web app/API with deployment slots and PaaS simplicity (Web App for Containers is an App Service feature).

**Tradeoffs summary table:**

| Method | Scale-to-zero | Ops burden | Prod floor | Use when |
|---|---|---|---|---|
| Static Web Apps | n/a (global CDN) | lowest | — | SPA + light serverless API, git-deployed |
| Azure Functions (Flex Consumption) | yes | low | ≥2 always-ready for AZ | event-driven, sporadic/spiky |
| Container Apps | yes | low-medium | zone-redundant where supported | containers + serverless scale / Dapr / canary (house default) |
| App Service | no | medium | zone-redundant where supported | plain HTTP web app/API, deployment slots |
| AKS | partial (user node pools) | highest | ≥6 nodes | need the Kubernetes API / mesh / GPU pools / isolation |

---

## Decision Tree: Azure Identity — managed identity, WIF, or app registration?

**When this applies:** A workload, CI/CD pipeline, or service needs to authenticate to Azure APIs or other Entra-protected resources. The observable inputs are: where does the caller run (Azure compute, GitHub Actions, external service, developer laptop) and whether the caller is a human or a workload.

**Last verified:** 2026-06-05 against Entra Identity documentation and WIF GA release notes.

```mermaid
flowchart TD
    START[Needs Azure credentials] --> H{Is the caller a human?}
    H -->|Yes| PIM[Entra user account + PIM eligible role<br/>JIT elevation with MFA and justification]
    H -->|No, workload| AZ{Running on Azure compute?}
    AZ -->|Yes| MI[Managed Identity - system or user assigned<br/>no credential to manage]
    AZ -->|No, CI runner - GitHub/GitLab/ADO| WIF[Workload Identity Federation<br/>OIDC token exchange - no client secret]
    AZ -->|No, external service or on-prem| EXT{Can the external service issue an OIDC token?}
    EXT -->|Yes| WIF
    EXT -->|No| APP[App registration + client secret<br/>rotate every 90 days + Key Vault]
```

**Rationale per leaf:**
- *Managed Identity* — the Azure fabric rotates the credential automatically; the workload calls `DefaultAzureCredential` and gets a short-lived token with no secret stored anywhere.
- *WIF* — CI systems issue signed OIDC tokens that Entra exchanges for short-lived access tokens; no client secret in pipeline variables.
- *PIM eligible role* — humans get JIT time-limited access with audit trail; standing Owner is an anti-pattern.
- *App registration + client secret* — last resort for external non-OIDC callers; rotate in Key Vault with a rotation runbook; never embed in code.

**Tradeoffs summary:**

| Method | Credential lifetime | Secret to manage? | Use when |
|---|---|---|---|
| Managed Identity | Auto-rotated by fabric | No | Workload on Azure compute |
| Workload Identity Federation | Per-workflow OIDC exchange | No | CI/CD runners with OIDC |
| PIM eligible role | Session-scoped - hours | No | Human operators |
| App reg + client secret | 90-day rotation | Yes - Key Vault | External non-OIDC callers only |

---

## Decision Tree: Azure networking — Private Endpoint vs Service Endpoint vs VNet Integration

**When this applies:** A PaaS resource (Storage, Key Vault, SQL, Cosmos, Container Registry, Service Bus) needs to be reachable from a VNet without being public. The observable inputs are: does the resource need a private IP in the VNet, does it need to be reachable from on-premises, and is the team using Private DNS.

**Last verified:** 2026-06-05 against Azure Private Link and VNet integration documentation.

```mermaid
flowchart TD
    START[PaaS resource needs private access] --> CRITICAL{Is this a data-plane resource - Key Vault, Storage, SQL, Cosmos, ACR?}
    CRITICAL -->|Yes - house rule private-by-default| PE[Private Endpoint<br/>private IP in subnet + Private DNS zone]
    CRITICAL -->|No, integration endpoint - Service Bus, Event Hubs| SE{Need reachability from on-prem or cross-VNet?}
    SE -->|Yes| PE
    SE -->|No, VNet-local only| SVCEP[Service Endpoint<br/>cheaper, no private IP, blocks public only from this VNet]
    PE --> DNS{Private DNS zone exists for this service type?}
    DNS -->|Yes| LINK[Link the zone to the VNet - auto-resolves]
    DNS -->|No| CREATE[Create the privatelink DNS zone + A record]
    CRITICAL -->|No, app outbound to PaaS| VNETINT[VNet Integration<br/>app-side outbound only - no private IP on the PaaS side]
```

**Rationale per leaf:**
- *Private Endpoint* — assigns the PaaS data plane a private IP inside your subnet; traffic never leaves the VNet; required for `publicNetworkAccess: Disabled`; works from on-prem via ExpressRoute/VPN.
- *Service Endpoint* — allows the VNet subnet to reach the PaaS service without traversing the public internet, but the PaaS resource still has a public IP and is not reachable from on-prem unless the Service Endpoint is combined with on-prem routing; cheaper than Private Endpoint for low-isolation scenarios.
- *VNet Integration* — the app (App Service, Container Apps, Functions) routes egress traffic through a delegated subnet; does not give the PaaS backend a private IP; combine with Private Endpoint on the backend.
- *Private DNS zone + VNet link* — required for Private Endpoint to resolve correctly; the `privatelink.*` zone must be linked to every VNet that resolves the name.

**Tradeoffs summary:**

| Method | Private IP? | On-prem reachable? | Cost | Use when |
|---|---|---|---|---|
| Private Endpoint | Yes | Yes via ER/VPN | Per-endpoint fee | Data-plane PaaS - house default |
| Service Endpoint | No | No | Free | Low-isolation PaaS access from one VNet |
| VNet Integration | App outbound only | N/A | Per-app | App egress routing only |

---

## Decision Tree: Azure FinOps — which cost lever to pull first?

**When this applies:** An Azure subscription bill is higher than expected, a budget alert has fired, or the team is asked to reduce Azure spend. The observable inputs are: which resource types dominate the bill, and whether the usage patterns are appropriate.

**Last verified:** 2026-06-05 against Azure Cost Management documentation and Log Analytics pricing tiers.

```mermaid
flowchart TD
    START[Azure bill too high or alert fired] --> FIRST{Which resource type dominates?}
    FIRST -->|Log Analytics ingestion| LA[Check diagnostic settings - disable verbose logs<br/>use Basic Logs tier for high-volume low-query tables<br/>set sampling on App Insights]
    FIRST -->|Compute - VMs, AKS nodes| COMPUTE{Are resources idle or oversized?}
    COMPUTE -->|Yes, idle| SHUTDOWN[Stop or delete idle resources<br/>auto-shutdown for dev/test]
    COMPUTE -->|Yes, oversized| RESIZE[Rightsize via Advisor recommendations<br/>then buy savings plan or RI]
    COMPUTE -->|No, appropriately used| COMMIT[Buy Azure savings plan or Reserved Instance<br/>after 30 days of baseline data]
    FIRST -->|Storage| STOR[Review lifecycle policies - move cool/archive<br/>delete orphaned disks and snapshots]
    FIRST -->|Networking - egress, Front Door| NET[Review data transfer patterns<br/>CDN caching effectiveness + region colocations]
    FIRST -->|PaaS services - SQL, Cosmos, Service Bus| PaaS[Check DTU/RU provisioning vs actual use<br/>serverless or autoscale tiers where supported]
```

**Rationale per leaf:**
- *Log Analytics* — the single most common Azure bill surprise; high-ingestion verbose logs can cost more than the workload itself.
- *Stop/delete idle* — dev/test VMs and AKS node pools running 24/7 are the easiest money to recover.
- *Rightsize then commit* — buying a reservation on an oversized VM locks in the waste; rightsize first.
- *Storage lifecycle* — moving blobs to Cool/Archive and deleting orphaned managed disks is free to configure and immediate.
- *CDN caching* — reducing egress by caching at Front Door edge is often the fastest networking cost lever.
- *PaaS autoscale* — provisioned Cosmos RUs or SQL DTUs sitting at 10% utilization are pure waste; serverless or autoscale tiers eliminate the floor.

**Tradeoffs summary:**

| Lever | Time to savings | Effort | Risk | Use when |
|---|---|---|---|---|
| Stop idle dev/test resources | Immediate | Low | Low | Dev/test not in use |
| Disable verbose diagnostic logs | Immediate | Low | Low | Log Analytics dominates bill |
| Rightsize compute | 1-2 weeks | Medium | Medium - test after | Advisor shows low utilization |
| Storage lifecycle policy | Days | Low | Low | Blobs aging in hot tier |
| PaaS serverless/autoscale tier | Days | Medium | Test required | Provisioned tier underutilized |
| Commit with savings plan/RI | Immediate discount | Low | Medium - commitment | Stable baseline confirmed |
