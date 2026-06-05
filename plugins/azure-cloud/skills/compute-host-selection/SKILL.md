---
name: compute-host-selection
description: "Decision playbook for choosing the right Azure compute service — App Service, Container Apps, Azure Functions, Static Web Apps, or AKS — based on workload shape, ops burden, and scaling requirements."
---

# Compute Host Selection

## When to Use This Skill

Use when a new workload needs a home on Azure and the right compute service is not obvious, or when reviewing an existing workload that may be over- or under-engineered for its current host.

## 1. The Primary Decision Tree

Answer these questions in order:

| Question | If YES | If NO |
|---|---|---|
| Is it purely static (HTML/JS/CSS + optional serverless API)? | **Static Web Apps** | Continue |
| Is it event-driven, short-duration (< 10 min), and triggered by a queue/timer/HTTP? | **Azure Functions** | Continue |
| Does it need HTTP scaling to zero AND you want container-native packaging? | **Container Apps** | Continue |
| Does it need the full Kubernetes API (CRDs, operators, custom schedulers)? | **AKS** | Continue |
| Everything else (traditional web app, always-on API, background service) | **App Service** | — |

## 2. Service Comparison Table

| Service | Scale-to-zero | Container-native | Ops burden | Best for |
|---|---|---|---|---|
| App Service | No (always-on) | Optional | Low | Web apps, REST APIs, background workers |
| Container Apps | Yes (Consumption) | Yes | Low-medium | Microservices, event-driven containers, scale-to-zero HTTP |
| Azure Functions | Yes | Optional | Low | Event-driven, short-lived, trigger-based processing |
| Static Web Apps | Yes | No | Minimal | SPAs, static sites, Jamstack with optional API routes |
| AKS | No | Yes | High | Kubernetes-specific APIs, complex orchestration |

## 3. Hosting the Claude Application on Azure

Per `app-platform-engineer`'s remit:

| Claude app shape | Recommended host |
|---|---|
| HTTP API wrapper around Claude | Container Apps (scale-to-zero, sidecar-friendly) |
| Serverless inference trigger | Azure Functions (Consumption plan, Durable for long chains) |
| Long-running agent with stateful conversation | Container Apps (min replicas: 1) or App Service |
| Full web app (front-end + API) | App Service (front-end) + Container Apps (API) |

Seam: `claude-app-engineering` names the target; this plugin provisions it.

## 4. App Service Plan SKU Selection

| Workload | SKU tier | Notes |
|---|---|---|
| Production web API | P2v3 or P3v3 | Zone-redundant available from P1v3+ |
| Dev / internal tools | B2 or B3 | No autoscale; acceptable for low-traffic |
| High-scale or zone-redundant | P2v3 + ZoneRedundant: true | Premium v3 required |
| Functions (always-on) | Elastic Premium EP2 | Needed when cold-start is unacceptable |

Avoid the Free and Shared tiers for anything beyond prototyping.

## 5. Container Apps Environment Considerations

```bicep
resource containerAppsEnv 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: 'cae-myapp-prod-eastus'
  location: location
  properties: {
    zoneRedundant: true    // prod only; not available in all regions
    workloadProfiles: [
      {
        name: 'Consumption'
        workloadProfileType: 'Consumption'
      }
    ]
  }
}
```

Use the **Consumption** workload profile for scale-to-zero. Use **Dedicated** (D4 / D8) for workloads needing guaranteed CPU/memory.

## 6. When to Use AKS (and When Not To)

**Use AKS only when you need:**
- Custom Kubernetes operators or CRDs
- Specific runtime scheduling (GPU node pools, spot nodes)
- Existing Kubernetes manifests and Helm charts from on-premises

**Do not use AKS when:**
- The requirement is "containerized" — Container Apps handles this with far less ops overhead
- The team doesn't have Kubernetes expertise — cluster upgrades, node pool management, and CNI configuration are non-trivial
- Cost is a concern — AKS system node pools run 24/7; Container Apps Consumption scales to zero

## 7. Checklist Before Finalizing

- [ ] Workload shape mapped to the decision tree (§1)
- [ ] Scale-to-zero requirement confirmed or ruled out
- [ ] Zone redundancy requirement confirmed for prod
- [ ] Ops team capability assessed (AKS requires Kubernetes expertise)
- [ ] Cost estimate produced for the selected SKU
- [ ] Seam to `claude-app-engineering` invoked if the workload is a Claude app

## Pitfalls

- Defaulting to AKS because the team "uses Docker" — Container Apps covers 90% of container use cases without Kubernetes ops overhead
- Using the Consumption plan for Functions that must always be warm — use Elastic Premium
- Choosing App Service for scale-to-zero HTTP APIs — it doesn't scale to zero; use Container Apps
- Forgetting zone redundancy for prod workloads — outages in a single AZ take the service down

## See Also

- [`../../agents/app-platform-engineer.md`](../../agents/app-platform-engineer.md) — compute decisions, scaling, and Claude-app Azure hosting
- [`../../agents/azure-architect.md`](../../agents/azure-architect.md) — WAF reliability and service selection
- [`../../CLAUDE.md`](../../CLAUDE.md) — house opinion: pick compute from the tree; AKS only when you need Kubernetes
