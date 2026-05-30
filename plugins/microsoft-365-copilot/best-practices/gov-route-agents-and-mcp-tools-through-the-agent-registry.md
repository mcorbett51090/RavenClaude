# Route every agent through the admin gate and every MCP tool through separate tenant consent — approval is AI-Admin/Global-Admin

**Status:** Absolute rule — an agent reaches users only through admin approval, and an agent's MCP tools are governed *independently* of the agent; skipping either ships ungoverned reach.

**Domain:** Governance / Agent Registry & approval

**Applies to:** `microsoft-365-copilot`

---

## Why this exists

Publishing an agent is not a developer action — it is an admin-gated lifecycle, and authors who treat "I sideloaded it" as "it's live for the org" ship nothing, while authors who forget MCP-tool consent ship an agent whose *tools* the tenant never approved. Two gates, two owners. **The agent** goes sideload (dev, personal) → submit to the **organizational catalog** → an admin **approves it in the Copilot Control System / M365 admin center** → it appears under "Built by your org" → optionally AppSource. **The agent's MCP tools / servers** are governed separately: a registered (BYO) MCP server appears in the M365 admin center under **Agents > Tools > Requests**, and an admin must both **approve it** *and* **grant tenant-wide Microsoft Entra consent** before it becomes available to agent-building surfaces — approval without consent doesn't make it usable, and a blocked server is enforced at runtime across all surfaces. Both approval and consent require an **AI Administrator** or **Global Administrator** (least-privilege: prefer AI Admin). The recurring incident is assuming an agent's MCP grounding inherits the agent's approval — it does not. This is house opinion #13.

## How to apply

Drive the agent through the catalog → admin-approval gate, and register + get approval + Entra consent for every MCP tool separately. Use AI Admin where possible.

```text
AGENT lifecycle (the app)
  sideload (dev/personal)
    → submit to organizational catalog
    → ADMIN APPROVES in Copilot Control System / M365 admin center  (AI Admin / Global Admin)
    → appears under "Built by your org" in the Agent Store
    → (optional) submit to Microsoft Commercial Marketplace / AppSource

MCP TOOL / SERVER lifecycle (governed INDEPENDENTLY of the agent)
  developer registers the remote MCP server
    → appears in M365 admin center > Agents > Tools > Requests
    → admin APPROVES the server                                     (AI Admin / Global Admin)
    → admin GRANTS tenant-wide Entra consent  ← both steps required; ~30 min to propagate
    → server is "Available" to agent-building surfaces (block = runtime-enforced everywhere)
```

**Do:**
- Submit agents to the **org catalog** and get **admin approval** before treating them as live for users (#13).
- Register each **MCP tool/server separately**, and get **both** admin approval **and** tenant-wide Entra consent.
- Use **AI Administrator** (least-privilege) over Global Administrator for the approval/consent role.
- State a `Licensing impact:` line and route the data-protection verdict to `ravenclaude-core/security-reviewer`.

**Don't:**
- Equate "sideloaded" or "in the catalog" with "available to users" — approval is the gate.
- Assume an agent's MCP tools are covered by the agent's approval — they need their own consent.
- Forget propagation lag — an approved MCP server can take up to ~30 min to appear across surfaces.

## Edge cases / when the rule does NOT apply

A **SharePoint-built** declarative agent **cannot be submitted to the org catalog at all** (Teams-only sharing) — its lifecycle is different, not exempt; rebuild in Agents Toolkit for org publishing (see [`./da-source-control-the-project-sideload-for-dev.md`](./da-source-control-the-project-sideload-for-dev.md)). **Copilot-Studio** agents are approved in the same Copilot Control System but their build/governance is the `power-platform` seam. Exact admin-center labels (Copilot Control System / Agent Registry / Agents > Tools) are evolving and `[verify-at-build]`.

## See also

- [`./publish-ship-a-validated-app-package-through-the-admin-gate.md`](./publish-ship-a-validated-app-package-through-the-admin-gate.md) — the app-package + RAI validation that precedes approval
- [`./gov-attach-a-payg-billing-policy-with-a-budget-cap.md`](./gov-attach-a-payg-billing-policy-with-a-budget-cap.md) — the licensing/PAYG companion
- [`../knowledge/copilot-admin-governance-2026.md`](../knowledge/copilot-admin-governance-2026.md) · [`../agents/copilot-admin-governance.md`](../agents/copilot-admin-governance.md)
- [Manage tools for agents in the M365 admin center](https://learn.microsoft.com/microsoft-365/admin/manage/manage-tools-for-agent) · [Agents admin guide](https://learn.microsoft.com/microsoft-365/copilot/agent-essentials/m365-agents-admin-guide)

## Provenance

Codifies house opinion #13 from [`../CLAUDE.md`](../CLAUDE.md). Grounded in the Microsoft Learn "Manage tools for agents in the M365 admin center" page (Agents > Tools > Registry/Requests, AI Admin + Global Admin requirement, approve + tenant-wide Entra consent, ~30-min propagation, runtime block enforcement) and the agents admin guide (Copilot Control System approval; SharePoint DAs can't reach the org catalog), retrieved 2026-05-30. Labels `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
