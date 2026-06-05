# Enable Defender for Cloud across all subscriptions from the landing zone

**Status:** Pattern
**Domain:** Azure governance / security
**Applies to:** `azure-cloud`

---

## Why this exists

Defender for Cloud's CSPM (Cloud Security Posture Management) tier is free and provides Secure Score, regulatory compliance assessments, and security recommendations across every subscription. Waiting until a workload is "mature" to enable it means the first security assessment happens after configuration debt has accumulated. The house opinion (#13: "Defender for Cloud + Azure Policy on by default") is explicit: both go on at the landing zone stage, not the workload stage. The Defender for Cloud plans (workload protection) are priced per resource type, but the CSPM baseline has no per-resource charge.

## How to apply

Enable Defender for Cloud via Azure Policy at the management group scope so every new subscription auto-enrolls:

```bicep
// Bicep — assign built-in "Enable Microsoft Defender for Cloud on your subscription" initiative
resource defenderAssignment 'Microsoft.Authorization/policyAssignments@2023-04-01' = {
  name: 'enable-defender-cloud'
  scope: managementGroup().id
  location: location
  identity: { type: 'SystemAssigned' }
  properties: {
    policyDefinitionId: '/providers/Microsoft.Authorization/policySetDefinitions/1f3afdf9-d0c9-4c3d-847f-89da613e70a8'
    displayName: 'Enable Defender for Cloud'
    enforcementMode: 'Default'
    parameters: {}
  }
}
```

Enable the Defender plans you need per subscription:
```bash
# Enable CSPM + Defender for Servers P1 (minimum recommended for prod)
az security pricing create --name VirtualMachines --tier Standard
az security pricing create --name AppServices --tier Standard
az security pricing create --name SqlServers --tier Standard
az security pricing create --name StorageAccounts --tier Standard
az security pricing create --name Containers --tier Standard
```

Configure email notifications:
```bash
az security contact create \
  --name "security-contact" \
  --email "security@example.com" \
  --alert-notifications On \
  --alerts-to-admins On
```

**Do:**
- Enable CSPM (free) in every subscription — there is no cost reason not to.
- Enable Defender plans (paid) for resource types in prod: VMs, App Services, SQL, Storage, Containers.
- Route high-severity alerts to an operational inbox or SIEM via Continuous Export to Log Analytics or Event Hub.
- Review Secure Score weekly — a drifting score is an early warning sign.

**Don't:**
- Enable only the free CSPM tier and ignore the workload protection plans for prod resources — CSPM shows you what to fix; the Defender plans detect active exploits.
- Suppress Secure Score recommendations without a documented exception.
- Leave email alerts with no recipient — unconfigured alerts generate noise nobody acts on.

## Edge cases / when the rule does NOT apply

- **Sandbox/dev subscriptions with no production data**: the free CSPM tier is still recommended; the paid Defender plans can be omitted if the budget impact is not justified.
- **Highly regulated environments with a separate CSPM tool (Qualys, Prisma Cloud, Wiz)**: Defender for Cloud can coexist with a SIEM integration, but evaluate whether dual-scanning adds value or just noise.

## See also

- [`../agents/azure-ops-engineer.md`](../agents/azure-ops-engineer.md) — owns Defender configuration and governance enforcement.
- [`./gov-azure-policy-as-guardrails.md`](./gov-azure-policy-as-guardrails.md) — Azure Policy is the delivery mechanism for Defender enrollment across subscriptions.

## Provenance

Codifies house opinion #13 from `CLAUDE.md` §3: "Defender for Cloud + Azure Policy on by default across all subscriptions." Grounded in the Azure landing zone accelerator reference architecture and CAF security governance guidance.

---

_Last reviewed: 2026-06-05 by `claude`_
