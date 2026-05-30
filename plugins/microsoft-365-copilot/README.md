# microsoft-365-copilot

A Microsoft 365 Copilot **extensibility & administration** specialist team for Claude Code — six agents that bring decision-tree-driven, citation-grounded judgment to building and governing agents on the M365 Copilot surface.

## What it is

Extending M365 Copilot is rarely blocked by typing — it's blocked by **decisions**: declarative agent or custom-engine? which grounding source? will this hit the 50-item / 45-second / no-loop wall? synced or federated connector? how do I remediate oversharing *before* turning Copilot on? This plugin encodes those decisions as a team of advisory specialists backed by a 9-doc knowledge bank whose every claim is grounded in Microsoft Learn with a retrieval date (the manifest schema ships ~monthly, so dated grounding matters).

The agents are **advisory and interactive**: your M365 tenant lives outside the repo, so they recommend the design and emit runnable artifacts (manifest JSON, OpenAPI, `atk` / `m365` CLI / Microsoft Graph snippets, Purview / admin-center steps) you run yourself.

## The team

| Agent | Owns |
|---|---|
| `copilot-extensibility-architect` | the routing brain: declarative vs custom-engine vs Copilot-Studio, grounding-source choice, the hard-limit-wall check, channel + publish path |
| `declarative-agent-engineer` | DA manifests (pinned schema), instructions (8K budget), capabilities, conversation starters, Agent Builder vs Agents Toolkit, manifest + RAI validation |
| `graph-connector-engineer` | Copilot (Graph) connectors — synced vs federated (MCP), schema + semantic labels, ACL ingestion/trimming, semantic-index latency |
| `api-plugin-engineer` | API plugins from OpenAPI — plugin-manifest↔`operationId` mapping, Entra/OAuth2/API-key auth, the GCC-High caveat |
| `agents-sdk-engineer` | custom-engine agents on the M365 Agents SDK/Toolkit — channels/turns/state, streaming/citations, DA→CEA conversion, multi-channel publish |
| `copilot-admin-governance` | Agent Registry lifecycle, agent + MCP-tool approval, licensing/PAYG, Purview DLP + sensitivity labels for Copilot, RSS/RCD, data residency |

Plus: a 9-doc knowledge bank (two Mermaid decision trees + manifest / connector / API-plugin / SDK / governance / security / residency references), 5 skills, 5 templates, and 1 advisory anti-pattern hook (15 house opinions).

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install microsoft-365-copilot@ravenclaude
/reload-plugins
```

Requires `ravenclaude-core@>=0.7.0` (inherits the Capability Grounding + Structured Output protocols).

## Prerequisite

No bundled MCP. Copilot automation uses the **Agents Toolkit** (`atk`, the Teams-Toolkit successor with the Playground), the **CLI for Microsoft 365** (`m365`), and the **Microsoft Graph** connector/admin APIs (Microsoft Entra auth). The agents recommend and emit the commands; you run them with your own credentials.

## How it relates to the other plugins

- **`power-platform/copilot-studio-engineer`** — Copilot Studio low-code / no-code / Dataverse-backed agents, governed in the Power Platform admin center. This plugin owns the M365 Copilot *surface* (declarative + custom-engine agents, Graph connectors, API plugins, M365-admin/Purview governance). *Copilot Studio, low-code, Dataverse → power-platform; Agent Builder / Agents Toolkit, Graph connectors, M365 admin center → here.*
- **`claude-app-engineering`** — the engine inside a custom-engine agent when it runs on Claude (prompts, tools, evals, caching). This plugin owns the M365 Agents SDK surface it plugs into.
- **`azure-cloud`** — the Entra app registration + the host for a custom-engine agent (Foundry / Container Apps). This plugin names the requirement; azure-cloud designs and provisions it.
- **`microsoft-fabric`** — Fabric/OneLake storage under data you want Copilot to ground on; this plugin surfaces it via a connector.
- **`ravenclaude-core/security-reviewer`** (mandatory) — connector ACLs, API-plugin auth, prompt-injection over ingested content.

See [`CLAUDE.md`](CLAUDE.md) §10 for the full seam wording.

## Versioning

Semver; bump on every user-visible change and keep `.claude-plugin/plugin.json` in sync with the catalog entry in `.claude-plugin/marketplace.json`. Because the manifest schema + many features ship monthly or in preview, dated claims concentrate in the per-topic `*-2026.md` knowledge docs and carry `[verify-at-build]` flags re-checked on each Researcher staleness sweep.
