# Source-control the Agents-Toolkit project; sideload for dev — don't lose the source to Agent Builder

**Status:** Pattern — strong default; the no-code surfaces are fine for prototyping but a production agent must live in git, and the build tool you pick gates where the agent can even be published.

**Domain:** Agent design / build tooling & ALM

**Applies to:** `microsoft-365-copilot`

---

## Why this exists

There are four ways to author a declarative agent, and they are not interchangeable for a product you intend to ship and maintain. **Agent Builder** (no-code, inside Copilot) and **SharePoint** are fast to prototype — but a SharePoint-built declarative agent **cannot be published to the organizational catalog at all**, and an Agent-Builder agent's source of truth is a tenant object, not a file you can diff, review, or roll back. The **Agents Toolkit** (`atk`) project — manifest + OpenAPI + plugin manifest + icons + infra — is a set of files that belong in git: reviewable, versionable, CI-validatable, and the only pro-code path that publishes to your org catalog and the Commercial Marketplace. The failure mode is building the agent by hand in Agent Builder, shipping it, then having no source when you need to change it under review, and discovering the build tool blocked the publish path you wanted. This is house opinion #14.

## How to apply

Prototype wherever is fastest, but the moment an agent is real, move it into an Agents-Toolkit project under source control. Sideload the dev build to test; promote through the publish path from the checked-in package.

```text
Agent Builder (no-code, in Copilot)   → prototype only; source-of-truth is a tenant object
SharePoint (no-code)                   → prototype only; CANNOT publish to org catalog
Copilot Studio (low-code)              → the power-platform seam (Dataverse-backed) — not this team
Agents Toolkit (`atk`, pro-code)       → PRODUCTION: git-tracked project, Playground, CI/CD,
                                         sideload → org catalog → AppSource
```

```text
# Agents-Toolkit project, all under source control:
appPackage/manifest.json          # the M365 app manifest
appPackage/declarativeAgent.json  # the pinned-schema DA manifest
appPackage/ai-plugin.json         # the plugin manifest (if it has actions)
apiSpec/openapi.yaml              # the OpenAPI spec (if it has actions)
appPackage/color.png, outline.png # icons
infra/                            # any host infra (for a CEA)
```

**Do:**
- Keep the Agents-Toolkit project (manifest, OpenAPI, plugin manifest, icons, infra) in git.
- Use the **Agents Playground** to test locally without a tenant round-trip; sideload for in-tenant dev.
- Pick the build tool against the publish path you need — SharePoint-built DAs can't reach the org catalog.

**Don't:**
- Hand-edit a production agent in Agent Builder and lose the diffable source (#14).
- Assume a SharePoint-built declarative agent can be promoted to the org catalog — it can't.
- Skip source control because "it's just a manifest" — it is the deployable artifact and the review surface.

## Edge cases / when the rule does NOT apply

A genuine throwaway prototype or a personal-use-only agent may live entirely in Agent Builder — the rule is about *production* agents that need review, versioning, and a publish path. A low-code / Dataverse-backed maker agent belongs in **Copilot Studio**, which is the `power-platform/copilot-studio-engineer` seam, not this team. **Agents Toolkit publishing is not supported in GCC/Government tenants** (`[verify-at-build]`) — surface that on any sovereign-cloud build.

## See also

- [`./publish-ship-a-validated-app-package-through-the-admin-gate.md`](./publish-ship-a-validated-app-package-through-the-admin-gate.md) — the publish lifecycle the source-controlled package feeds
- [`./cea-escalate-to-custom-engine-only-when-a-hard-limit-forces-it.md`](./cea-escalate-to-custom-engine-only-when-a-hard-limit-forces-it.md) — when the same `atk` project becomes a custom-engine agent
- [`../knowledge/agent-platform-decision-2026.md`](../knowledge/agent-platform-decision-2026.md) · [`../agents/declarative-agent-engineer.md`](../agents/declarative-agent-engineer.md)
- [Microsoft 365 Agents Toolkit overview](https://learn.microsoft.com/microsoftteams/platform/toolkit/overview-agents-toolkit) — the Playground + multi-channel publish

## Provenance

Codifies house opinion #14 from [`../CLAUDE.md`](../CLAUDE.md). Grounded in the Microsoft Learn Agents-Toolkit overview, the "Choose the right tool" comparison, the agents admin guide (the boxed note "Declarative agents built with SharePoint can't be published to an organization catalog"), and the Agents-SDK page's GCC publishing caveat, all retrieved 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
