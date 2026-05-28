# azure-cloud

The Azure infrastructure & platform specialist team — the cloud layer underneath the rest of the Microsoft stack (Fabric, Power Platform, Claude apps on Azure, web apps on Azure).

## What it is

The hard part of Azure work is the decisions: landing-zone topology, Bicep or Terraform, which compute service, passwordless identity, private networking, cost control. This plugin encodes them as a team of advisory specialists backed by a 9-doc, retrieval-dated, CAF/WAF-grounded knowledge bank (Azure ships constantly, so the dated capability map matters).

The agents are **advisory and interactive**: your Azure tenant and credentials live outside the repo, so they recommend designs and emit runnable snippets (Bicep / Terraform / `az` CLI / Policy JSON) you run yourself.

## The team

| Agent | Owns |
|---|---|
| `azure-architect` | landing zones / CAF, service selection, non-Fabric data tier, WAF |
| `bicep-iac-engineer` | Bicep + Terraform + AVM + Deployment Stacks + the passwordless CI/CD pipeline |
| `entra-identity-engineer` | managed identity / workload identity federation / RBAC / PIM / Entra External ID |
| `network-engineer` | Private Endpoints, hub-spoke/vWAN, Front Door/App Gateway/WAF, firewall/egress |
| `app-platform-engineer` | compute selection (App Service / Container Apps / Functions / Static Web Apps / AKS), the Azure host |
| `integration-engineer` | Logic Apps, Service Bus, Event Grid, Event Hubs, API Management |
| `azure-ops-engineer` | observability (Monitor/App Insights/OTel), FinOps, governance (Policy/Defender) |

Plus a 9-doc knowledge bank (landing zones, IaC, compute + integration decision trees, identity, networking, observability/FinOps, CI/CD, dated 2026 capability map), 6 templates, and 1 advisory hook (16 house opinions).

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install azure-cloud@ravenclaude
/reload-plugins
```

Requires `ravenclaude-core@>=0.7.0`.

## Prerequisite

No bundled MCP. The agents emit code against the **Azure CLI** (`az`), **Bicep**, and **Terraform** (azurerm); you run it with your own credentials (or workload identity federation in CI/CD).

## How it relates to the other plugins

- **`power-platform/flow-engineer`** — Power Automate (O365 makers) vs Logic Apps (Azure/IaC): the documented seam.
- **`microsoft-fabric`** — Fabric analytics platform → fabric; raw non-Fabric Azure data services → here.
- **`claude-app-engineering`** — the Claude app → claude-app-engineering; the Azure host it runs on → `app-platform-engineer`.
- **`web-design`** — `app-platform-engineer` provisions Static Web Apps; web-design builds the site.
- **`ravenclaude-core/security-reviewer`** (mandatory) — all identity/secrets/network-security design.

See [`CLAUDE.md`](CLAUDE.md) §10 for the full seam wording (these seams are documented reciprocally in each neighbor's CLAUDE.md).

## Versioning

Semver; keep `.claude-plugin/plugin.json` in sync with the catalog entry. The dated capability map (`knowledge/azure-2026-capability-map.md`) is re-reviewed on each Researcher staleness sweep because Azure ships constantly (B2C EOL, AVM, Deployment Stacks, Entra Agent ID).
