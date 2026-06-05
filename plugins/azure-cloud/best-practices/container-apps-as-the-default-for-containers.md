# Container Apps is the default for containerized workloads, not AKS

**Status:** Pattern
**Domain:** Azure compute
**Applies to:** `azure-cloud`

---

## Why this exists

Teams reach for AKS because they know Kubernetes, not because they need it. AKS requires node pool management, cluster upgrades, add-on operations, RBAC design, and a minimum viable node count for HA — overhead that Container Apps eliminates for the vast majority of containerized workloads. Container Apps gives serverless scale-to-zero, Dapr, traffic-splitting for canaries, and KEDA-based scaling without any node to operate. Choosing AKS for a simple API or background worker inflates operational burden with no user-visible benefit. The decision tree in `knowledge/azure-compute-decision-tree.md` codifies when AKS earns its complexity.

## How to apply

Default to Container Apps. Escalate to AKS only when the workload genuinely needs:
- The Kubernetes API (Custom Resource Definitions, operator pattern)
- A service mesh (Istio/Linkerd) at the node level
- GPU node pools
- Deny-by-default `NetworkPolicy` at the pod level
- Multi-workload isolation across hostile tenants sharing a cluster

```bicep
// Bicep — Container Apps environment + app
resource caEnv 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: 'cae-${appName}-${env}'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
    zoneRedundant: true   // prod: always true
  }
}

resource caApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'ca-${appName}-${env}'
  location: location
  identity: { type: 'SystemAssigned' }
  properties: {
    managedEnvironmentId: caEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8080
        traffic: [{ latestRevision: true, weight: 100 }]
      }
    }
    template: {
      containers: [{
        name: appName
        image: '${acrName}.azurecr.io/${appName}:${imageTag}'
        resources: { cpu: '0.5', memory: '1Gi' }
      }]
      scale: { minReplicas: 1, maxReplicas: 10 }
    }
  }
}
```

**Do:**
- Set `zoneRedundant: true` on the Container Apps environment for prod.
- Use system-assigned managed identity (`identity: { type: 'SystemAssigned' }`) and grant RBAC from there.
- Set `minReplicas: 0` only for truly bursty/dev workloads; prod usually needs `minReplicas: 1` for latency.
- Use `traffic` weights for blue/green or canary rollouts without any extra tooling.

**Don't:**
- Default to AKS because the team ran Kubernetes before — traverse the decision tree first.
- Run AKS for fewer than 6 nodes in production — it's a costly floor for small workloads.
- Embed connection strings in container definitions — use managed identity + Key Vault references.

## Edge cases / when the rule does NOT apply

- **Operator pattern / CRDs**: AKS is the only option if the workload deploys or consumes Custom Resource Definitions.
- **GPU-accelerated inference**: Container Apps does not support GPU node pools; AKS is required.
- **Multi-tenant hostile workload isolation**: separate Container Apps environments provide environment-level isolation, but not node/kernel isolation.

## See also

- [`../agents/app-platform-engineer.md`](../agents/app-platform-engineer.md) — owns the compute decision and Container Apps configuration.
- [`./pick-compute-from-the-decision-tree.md`](./pick-compute-from-the-decision-tree.md) — the parent rule that routes all compute questions to the decision tree.

## Provenance

Codifies house opinion #7 ("Pick compute from the tree; AKS only when you need the Kubernetes API") from `CLAUDE.md` §3, grounded in the Azure compute decision tree at `knowledge/azure-compute-decision-tree.md`. Container Apps is the house default for containers per that tree.

---

_Last reviewed: 2026-06-05 by `claude`_
