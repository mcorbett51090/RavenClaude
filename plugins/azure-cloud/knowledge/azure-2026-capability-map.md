# Azure 2026 capability map (dated freshness anchor)

**Last reviewed:** 2026-05-28 · **Confidence:** medium-high — Azure ships constantly, so this is the anchor the Researcher sweep re-dates. Every dated claim must be re-verified before quoting a client.
**Owner:** all agents (house opinion #16 — cite the capability with a retrieval date).
**Source:** Microsoft Learn, retrieved 2026-05-28 (URLs in the per-topic knowledge docs).

## Identity / CIAM (the most date-sensitive)
- **Azure AD B2C end-of-sale May 1 2025** (no new customers); **existing tenants supported ~to 2030**; **B2C P2 / ID Protection retired ~March 2026** (auto-downgrade to P1); **HSC coexistence** for B2C→External ID migration. **New CIAM → Microsoft Entra External ID.**
- **Workload identity federation** — GA; the passwordless path for GitHub Actions / AKS / other clouds / Azure DevOps service connections.
- **Entra Agent ID** — identities for AI agents (new in the Entra family); verify scope/GA.
- **Managed identity** (system/user-assigned) — GA.

## IaC
- **Bicep** — GA; **Deployment Stacks GA** (`denySettings`, managed-resource lifecycle/cleanup) — the Bicep answer to Terraform lifecycle. **Azure Blueprints deprecated** → Deployment Stacks + Azure Policy + ALZ.
- **Terraform azurerm** — current; **Azure Export for Terraform (`aztfexport`)** for importing existing resources.
- **Azure Verified Modules (AVM)** — Microsoft-maintained, WAF-aligned, for **both** Bicep + Terraform; includes **ALZ accelerator** + **subscription-vending** modules.

## Compute
- **Functions Flex Consumption** — recommended serverless plan; constraints: **no deployment slots, one app per plan, no in-place migration from Consumption, AZ needs ≥2 always-ready instances**.
- **Container Apps** — GA (serverless containers, Dapr, scale-to-zero, dynamic sessions for sandboxed code); **App Service**, **Static Web Apps**, **AKS** — GA. ("Container Apps as the flexible default" is RavenClaude's opinion, not a Microsoft statement.)
- **⚠️ AKS — Azure Linux 2.0 node OS retired (action-forcing, verified 2026-06-19):** AKS support + security updates **ended 2025-11-30**; node images were **removed 2026-03-31** — after which affected node pools **can't scale**. Migrate to osSku **AzureLinux3** (the default for `--os-sku AzureLinux` on Kubernetes **1.32–1.36**; selectable without a version bump on 1.28+, but update the OS SKU before upgrading to 1.37+). Sources: [AKS Azure Linux support cycle](https://learn.microsoft.com/azure/azure-linux/aks-support-cycle), [Upgrade OS version in AKS](https://learn.microsoft.com/azure/aks/upgrade-os-version).

## Networking
- **Private Endpoints + Private DNS**, **Front Door** (global + WAF), **Application Gateway** (regional + WAF), **Azure Firewall**, **Virtual WAN**, **DDoS Protection** — GA. Deny-public-by-default for PaaS data planes is the recommended posture.

## Integration / observability / governance
- **Logic Apps** (Consumption + Standard), **Service Bus** (Premium → Event Grid integration), **Event Grid**, **Event Hubs**, **API Management** — GA.
- **Azure Monitor / Log Analytics / workspace-based App Insights / OpenTelemetry** — GA; **Basic Logs**, **commitment tiers**, **daily caps**, long-term retention — GA cost levers.
- **Azure Policy**, **Defender for Cloud**, **Microsoft Sentinel** (simplified pricing tiers), **Cost Management** budgets/exports/reservations — GA.

## How to keep this current
On each Researcher sweep: re-run a Microsoft Learn `what's-new` / Azure Updates check; re-date this file; correct any status that changed (especially the B2C→External ID timeline and Flex Consumption constraints); bump the plugin patch version if a *default* changes. Numeric/dated claims live **here**, not baked into the seven agent personas.
