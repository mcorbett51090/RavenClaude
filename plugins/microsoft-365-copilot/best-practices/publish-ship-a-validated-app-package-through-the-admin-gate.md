# Ship every agent as a validated app package through sideload → org-catalog → AppSource — RAI validation runs at the gate

**Status:** Absolute rule — an agent is an M365 app; it ships only as a package, and RAI + store validation run on sideload and publish, not as an afterthought.

**Domain:** Governance / publish lifecycle

**Applies to:** `microsoft-365-copilot`

---

## Why this exists

Declarative agents, custom-engine agents, and the connectors/plugins they carry are all distributed as **M365 app packages** — manifest + icons + (optional) plugin/connector files — through the same unified app model as any Teams/M365 app. There is no "just deploy the manifest" path: the package is the unit, and it moves through a fixed lifecycle with validation gates. **Sideload** (dev/personal) → **organizational catalog** (admin-approved) → **Microsoft Commercial Marketplace / AppSource** (ISV, via Partner Center's "Microsoft 365 and Copilot" program). At the org-catalog and marketplace gates the package is validated: **RAI validation** runs (the same content checks as author-time), plus the **store validation guidelines** for marketplace submission. Authors who hand a loose manifest to an admin, or who treat sideload success as publish-readiness, hit the gate unprepared — a package that's schema-valid can still fail RAI or store validation at submission. Build the package, validate it locally, then submit it through the gate. This is house opinions #12 (validated app package) and #13 (admin gate).

## How to apply

Assemble the app package, validate it (schema + RAI + golden-prompt) at sideload, then promote through the lifecycle. Each gate up the chain adds validation, not fewer checks.

```text
PACKAGE (the unit of distribution)
  appPackage/manifest.json          # M365 app manifest (references the agent + plugins)
  appPackage/declarativeAgent.json  # the pinned-schema DA manifest (or CEA app)
  appPackage/ai-plugin.json         # plugin manifest (if it has actions)
  apiSpec/openapi.yaml              # OpenAPI (if it has actions)
  color.png / outline.png           # icons

LIFECYCLE (validation at each gate)
  sideload (dev/personal)           → schema + RAI validation; run golden-prompt set
    → submit to ORGANIZATIONAL CATALOG → admin approves (Copilot Control System) + RAI re-validates
       → appears under "Built by your org" in the Agent Store
    → (ISV) submit to Microsoft Commercial Marketplace via Partner Center
       → store validation guidelines + RAI + (optional) M365 App Compliance certification
```

**Do:**
- Assemble and ship the agent as an **app package** — manifest + icons + plugin/connector files (#12).
- Run **schema + RAI validation + the golden-prompt set** at sideload, before submitting (#15).
- Promote through **sideload → org catalog → AppSource**; expect RAI to re-run at each gate (#13).
- For marketplace, meet the **store validation guidelines** and consider M365 App Compliance certification.

**Don't:**
- Treat a loose manifest or a sideload-only build as publishable to the org (#13).
- Assume schema validity = publish-ready — RAI + store validation gate the submission (#12, #15).
- Hand-edit the live package out of band — keep the source-controlled `atk` project authoritative (#14).

## Edge cases / when the rule does NOT apply

A **personal-use** agent may stop at sideload (no org-catalog submission) — but it is still an app package, and RAI still runs on sideload. A **SharePoint-built** declarative agent can be shared in Teams but **cannot be submitted to the org catalog** — different lifecycle, covered in [`./da-source-control-the-project-sideload-for-dev.md`](./da-source-control-the-project-sideload-for-dev.md). **Connectors** are published/managed in the M365 admin center connectors surface rather than as a Teams app — the package model is for agents/plugins. Marketplace program names and validation-guideline specifics are `[verify-at-build]`.

## See also

- [`./gov-route-agents-and-mcp-tools-through-the-agent-registry.md`](./gov-route-agents-and-mcp-tools-through-the-agent-registry.md) — the admin approval + MCP-consent gate
- [`./da-pass-rai-validation-design-the-prompt-for-it.md`](./da-pass-rai-validation-design-the-prompt-for-it.md) — passing the RAI gate this lifecycle runs
- [`./da-source-control-the-project-sideload-for-dev.md`](./da-source-control-the-project-sideload-for-dev.md) — the source-controlled package that feeds publish
- [`../knowledge/copilot-admin-governance-2026.md`](../knowledge/copilot-admin-governance-2026.md) · [`../agents/copilot-admin-governance.md`](../agents/copilot-admin-governance.md)
- [Publish agents for Microsoft 365 Copilot](https://learn.microsoft.com/microsoft-365/copilot/extensibility/publish) · [Agents are apps](https://learn.microsoft.com/microsoft-365/copilot/extensibility/agents-are-apps)

## Provenance

Codifies house opinions #12 and #13 from [`../CLAUDE.md`](../CLAUDE.md). Grounded in the Microsoft Learn "Publish agents" and "Agents are apps" pages (sideload → org catalog → Partner Center / Commercial Marketplace; store validation guidelines + RAI + optional App Compliance certification) and the agents admin guide, retrieved 2026-05-30. Program/guideline specifics `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
