# Make the cloud-flow-vs-Logic-Apps call by ownership and governance plane, not by feature checklist

**Status:** Pattern — strong default; the wrong choice is expensive to unwind because the two run on different billing, RBAC, and ALM planes.
**Domain:** Power Automate / integration
**Applies to:** `power-platform`

---

## Why this exists

Power Automate cloud flows and Azure Logic Apps share an engine — Power Automate "is built on top of Azure Logic Apps," both are "designer-first integration platforms," and their connector sets overlap ([Microsoft Learn, *Integration and Automation Platform Options in Azure*](https://learn.microsoft.com/en-us/azure/azure-functions/functions-compare-logic-apps-ms-flow-webjobs), `ms.date 2026-03-23`, retrieved 2026-06-08). Because they look alike in the designer, teams pick one on familiarity and discover the consequences late: a citizen-built cloud flow can't get **resource-level RBAC**, Azure-subscription billing, VNet integration, or B2B/EDI; a Logic App can't be governed by **DLP**, packaged in a Dataverse solution, or owned by a per-user-licensed maker. The choice is not a feature checklist — it is a decision about **who owns it, how it's licensed, which governance plane controls it, and how it ships.**

The first-party audience split states it plainly: Power Automate "empowers business users, office workers, and citizen developers to build simple integrations without … code"; Azure Logic Apps "supports integrations ranging from little-to-no-code … to more advanced, codeful, and complex workflows … B2B processes or scenarios that require enterprise-level interactions with Azure DevOps" (same Learn page, retrieved 2026-06-08).

## How to apply

Decide on these axes, in order — the first one that forces a side wins:

| Axis | Power Automate cloud flow | Azure Logic Apps |
|---|---|---|
| **Owner / maintainer** | Citizen maker / maker team in O365 | IT pro / developer in an Azure subscription |
| **Licensing & billing** | Per-user license in Office 365 / Power Platform | Consumption-based or Standard plan billed to an Azure subscription |
| **Governance plane** | **Data Loss Prevention (DLP)** | **Azure Policy** + resource-level RBAC + audit trails |
| **RBAC granularity** | User-level (tied to the maker) | Resource-level (survives the author leaving) |
| **Lifecycle / ALM** | Solution-aware flow + Power Platform ALM (connection refs, env vars, pipelines) | ARM/Bicep, Azure CLI, VS Code, Azure DevOps |
| **Workload shape** | Approvals, notifications, simple business automation over first-party connectors | High-volume, stateful enterprise orchestration, B2B/EDI (Enterprise Integration Pack), VNet-integrated |

(Axis table from the [community Learn comparison](https://learn.microsoft.com/en-us/microsoft-365/community/power-automate-vs-logic-apps), `updated_at 2025-11-14`, retrieved 2026-06-08, corroborated against the first-party page above; RBAC-level and audit-trail distinctions are from that community page and are `[partly community-sourced — corroborate against the first-party capability table at verify-time]`.)

**Do:**
- Start with `flow-engineer` making the **initial** call; hand off to `azure-cloud/integration-engineer` (when installed) the moment any axis forces Logic Apps (this plugin's CLAUDE.md §11 seam).
- Default to a **cloud flow** when a citizen maker owns it, it's licensed per-user under O365/DLP, and the workload is simple business automation.
- Default to a **Logic App** when it lives in an Azure subscription, deploys via Bicep/Terraform, is governed by Azure Policy, or needs resource-level RBAC, B2B/EDI, or VNet.
- Remember the two **compose**: "A Power Automate flow can call an Azure Logic Apps workflow" (first-party page, retrieved 2026-06-08) — a citizen-owned flow can delegate one heavy/enterprise leg to a Logic App rather than re-platforming the whole thing.

**Don't:**
- Pick by connector availability alone — both reach 1,400+ connectors; the governance/ownership plane is the real differentiator.
- Build an enterprise, high-volume, security-sensitive integration as a per-user cloud flow because "the maker already knows Power Automate" — when that maker leaves, user-level RBAC means the workflow can be orphaned.
- Quote a specific capability-comparison row from memory — route the detailed "which one" to Microsoft's [*Power Automate migration → Compare capability details*](https://learn.microsoft.com/en-us/azure/logic-apps/power-automate-migration#compare-capability-details) table and `[verify-at-use]`.

## Edge cases / when the rule does NOT apply

- **A genuine hybrid** — a citizen-owned approval flow that needs one B2B/EDI leg: keep the flow in Power Automate and call a Logic App for that leg, rather than moving everything to Azure.
- **Org has no Azure subscription / no platform team** — Logic Apps may be off the table organizationally regardless of fit; surface that as a constraint, don't silently pick the technically-ideal-but-unavailable option.
- **Pricing is volatile** — Consumption vs Standard plan economics change; `[verify-at-use]` against the Azure pricing calculator before quoting cost to a customer.

## See also

- [`../knowledge/flow-decision-trees.md`](../knowledge/flow-decision-trees.md) — `## Decision Tree: Integration platform — cloud flow vs Azure Logic Apps` (the branch logic this rule states in prose)
- [`../agents/flow-engineer.md`](../agents/flow-engineer.md) — makes the initial call and owns the hand-off
- [`./flow-desktop-rpa-is-last-resort.md`](./flow-desktop-rpa-is-last-resort.md) — the *other* "which automation surface" rule (RPA vs cloud)
- CLAUDE.md §11 — the escalation seam to `azure-cloud/integration-engineer`

## Provenance

Grounded in Microsoft Learn *Integration and Automation Platform Options in Azure* (`functions-compare-logic-apps-ms-flow-webjobs`, first-party, `ms.date 2026-03-23`) and *Power Automate vs Logic Apps* (`microsoft-365/community/power-automate-vs-logic-apps`, community, `updated_at 2025-11-14`), both retrieved 2026-06-08; research persisted at `docs/research/2026-06-08-power-platform-best-practices/`. Codifies this plugin's existing CLAUDE.md §11 litmus test as a named, citable rule.

---

_Last reviewed: 2026-06-08 by `claude`_
