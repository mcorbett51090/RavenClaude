# M365 Agents SDK + Agents Toolkit (2026)

**Last reviewed:** 2026-05-30
**Confidence:** High on the Bot-Framework-successor lineage + toolkit rename (first-party). `[verify-at-build]` on SDK feature surface + Playground specifics.
**Read when:** building a custom-engine agent, converting a declarative agent to one, or migrating a Bot Framework bot.

---

## The M365 Agents SDK (Bot Framework's successor)

The **M365 Agents SDK** is the successor to the Bot Framework SDK — it owns the **agent surface**: channel/turn/state management, activity handling, streaming responses, and citations. It does **not** own the engine (orchestrator/model/prompts) — for a Claude-powered custom-engine agent, the engine is `claude-app-engineering`'s. Grounding: [Agents SDK overview](https://learn.microsoft.com/microsoft-365/agents-sdk/agents-sdk-overview).

**Bot Framework → Agents SDK migration:** existing BF bots port to the Agents SDK; plan the migration when bringing a legacy bot onto the Copilot/Teams surface. Grounding: [BF migration guidance](https://learn.microsoft.com/microsoft-365/agents-sdk/bf-migration-guidance).

## The Agents Toolkit (`atk`, Teams Toolkit's successor)

The **Agents Toolkit** (`atk`) replaces the Teams Toolkit — VS Code / Visual Studio / CLI scaffolding, the **Playground** for local test without a tenant round-trip, and CI/CD. House rule: **source-control the project; sideload for dev.** Grounding: [Agents Toolkit overview](https://learn.microsoft.com/microsoftteams/platform/toolkit/overview-agents-toolkit).

## When you need a custom-engine agent

Only when a declarative agent can't (see [`agent-platform-decision-2026.md`](agent-platform-decision-2026.md)): iterative reasoning/loops, proactive/autonomous behavior, off-M365 channels, or a non-Copilot model. The CEA carries **hosting + ops cost** — confirm the declarative agent genuinely doesn't fit. Grounding: [custom engine agent](https://learn.microsoft.com/microsoft-365/copilot/extensibility/overview-custom-engine-agent).

## DA → CEA conversion

When a declarative agent hits the wall: the SDK now owns the orchestration loop, state, and channels; re-home the grounding (connectors/actions still apply via `graph-connector-engineer` / `api-plugin-engineer`); the engine moves to `claude-app-engineering`; the host + Entra app reg move to `azure-cloud`.

## Publish + channels

A custom-engine agent ships as an **app package** (see [`agents-are-apps`](https://learn.microsoft.com/microsoft-365/copilot/extensibility/agents-are-apps)) across channels (M365 Copilot / Teams / web). The **org-catalog gate is admin-approved** → `copilot-admin-governance`.

## Licensing impact

CEAs carry host + (often) model cost on top of Copilot seats / PAYG — state it.

## Refresh triggers
- Agents SDK / Toolkit feature surface or CLI name changes.
- Agent 365 SDK (Entra agent identity + governed MCP) reaches GA `[verify-at-build]`.
