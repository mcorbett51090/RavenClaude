---
description: Decide how to extend Microsoft 365 Copilot — traverse the declarative vs custom-engine vs Copilot-Studio decision, pick the grounding source (synced/federated connector vs SharePoint knowledge vs API plugin), and name the host/engine seams.
argument-hint: "[the scenario, e.g. 'an agent that drafts and submits expense reports']"
---

# Design Copilot extensibility

You are running `/microsoft-365-copilot:design-copilot-extensibility`. Decide the build path and grounding for what the user described (`$ARGUMENTS`), following this plugin's `copilot-extensibility-architect` discipline — pick from the decision tree, never from "which feels more powerful."

## When to use this

The build path or grounding source for a Copilot extension isn't settled yet. Once it's clearly a declarative agent, route to `/microsoft-365-copilot:build-declarative-agent`; once it's clearly a connector, `/microsoft-365-copilot:build-graph-connector`.

## Steps

1. **Default to a declarative agent** — it runs on Copilot's orchestrator/models, inherits M365 compliance, needs no hosting (`cea-escalate-to-custom-engine-only-when-a-hard-limit-forces-it.md`).
2. **Escalate to a custom-engine agent only when a hard limit forces it** — iterative reasoning/loops, proactive/autonomous behavior, an off-M365 channel, or a non-Copilot model; the no-loop wall is the brightest line. Name *which* limit forced it (same file).
3. **Confirm the declarative agent genuinely can't first** — try reshaping the grounding or splitting scope before taking on hosting + ops + model cost forever (same file).
4. **Pick the grounding source from the job, not habit** — synced connector for scale + ranked retrieval, federated/MCP for real-time, API plugin for transactional actions (`connector-choose-synced-vs-federated-and-set-crawl-refresh.md`).
5. **Sanity-check the declarative wall** — if the grounding/action shape can't fit ~66% of 50 grounding / 25 response items / ~4,096 tokens / 45s sequential-no-loop, that's a signal to escalate (`design-to-66-percent-of-the-declarative-agent-wall.md`).
6. **Name the seams when custom-engine** — the engine-on-Claude → `claude-app-engineering`; the Entra app reg + host (Foundry/Container Apps) → `azure-cloud`; publish + org-catalog approval → `copilot-admin-governance`. Don't absorb their work (`cea-escalate-to-custom-engine-only-when-a-hard-limit-forces-it.md`).

## Guardrails

- Never choose a custom-engine agent for power/flexibility when a declarative agent fits — that's hosting + ops you didn't need.
- Cite each capability's GA/preview status with a retrieval date and tag fast-moving facts `[verify-at-build]` — the schema and features ship monthly.
- Low-code/Dataverse-backed agents are the `power-platform/copilot-studio-engineer` seam, not this plugin. State a `Licensing impact:` line on every grounding/build recommendation.
