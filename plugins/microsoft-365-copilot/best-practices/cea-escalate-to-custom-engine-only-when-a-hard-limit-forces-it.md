# Escalate to a custom-engine agent only when a hard limit forces it — and name the host + engine seams when you do

**Status:** Absolute rule — a custom-engine agent is hosting + ops + model cost you take on permanently; reach for it only when a declarative agent genuinely cannot do the job, and never absorb the engine/host work that belongs to other plugins.

**Domain:** Agent design / platform choice

**Applies to:** `microsoft-365-copilot`

---

## Why this exists

A declarative agent runs on Copilot's own orchestrator and models, inherits M365 compliance, and needs **no hosting**. A custom-engine agent (CEA) on the M365 Agents SDK is the opposite trade: *you* bring the orchestrator, the model, and the hosting, and you own the ops, the compliance posture, and the bill — forever. That cost is justified only when a declarative agent hits a wall it cannot design around: **iterative reasoning / loops**, **proactive or autonomous** behavior, an **off-M365 channel** (web, SMS, Teams-as-a-bot, the 10+ Agents-SDK channels), or a **non-Copilot model**. The single brightest line is the no-loop wall — a declarative agent does one grounding op + one tool call, sequential; the moment the task needs to iterate, it is a CEA. The anti-pattern is reaching for a CEA because it feels more powerful, then carrying hosting you never needed. This is house opinions #1, #4, and #15: declarative-first, and when you do go custom-engine, the engine and host are *other plugins' jobs*.

## How to apply

Run the platform decision tree before naming a CEA. If a CEA is genuinely forced, name *why a declarative agent doesn't fit* and hand the engine and host to their owners — this plugin owns only the Agents-SDK surface.

```text
Declarative agent fits UNLESS one of these is true → then it's a custom-engine agent:
  - needs a loop / iterative reasoning / multi-step tool chaining   (the no-loop wall, #4)
  - proactive / autonomous (initiates work without a user prompt)
  - off-M365 channel (web, SMS, email, Teams bot, partner channels)
  - non-Copilot model (BYO model via Agents SDK / Foundry)

When forced, the seams (you NAME the requirement; they BUILD it):
  engine on Claude (orchestrator/prompts/tools/evals/caching) → claude-app-engineering
  Entra app reg + host (Foundry / Container Apps / Functions)  → azure-cloud
  publish + org-catalog approval                              → copilot-admin-governance
```

**Do:**
- Confirm the declarative agent genuinely can't (reshape grounding, split scope) **before** escalating (#1).
- State *which* hard limit forced the CEA in the output — "needs a loop", "proactive trigger", etc.
- Hand the engine to `claude-app-engineering` and the Entra app reg + host to `azure-cloud`; this plugin owns channel/turn/state, streaming, citations, and publish.
- Carry the `Licensing impact:` line — a CEA adds host + (often) model cost on top of Copilot seats / PAYG.

**Don't:**
- Choose a CEA for power/flexibility when a declarative agent fits — that's unneeded hosting + ops (#1).
- Host or write the engine *inside* this plugin's design — honor the seams (#15).
- Assume a CEA escapes governance — it still ships as an app package through the admin gate (#13).

## Edge cases / when the rule does NOT apply

A **low-code / Dataverse-backed** agent that needs custom orchestration is a Copilot-Studio CEA, which is the `power-platform/copilot-studio-engineer` seam — not the Agents-SDK path this plugin owns. A **Microsoft Foundry** agent can be published to Copilot directly (auto-provisioning Azure Bot Service + Entra) *or* wired via an Agents-Toolkit proxy — the host seam still routes to `azure-cloud`, but the integration shape differs (`[verify-at-build]`). The **Teams SDK** (Teams-only, built-in Action Planner) is a lighter alternative to the full Agents SDK when the only channel is Teams.

## See also

- [`./cea-convert-da-to-cea-rehome-grounding-and-the-seams.md`](./cea-convert-da-to-cea-rehome-grounding-and-the-seams.md) — the conversion mechanics when a DA actually hits the wall
- [`./design-to-66-percent-of-the-declarative-agent-wall.md`](./design-to-66-percent-of-the-declarative-agent-wall.md) — the wall that forces the escalation
- [`../knowledge/agent-platform-decision-2026.md`](../knowledge/agent-platform-decision-2026.md) · [`../knowledge/agents-sdk-and-toolkit-2026.md`](../knowledge/agents-sdk-and-toolkit-2026.md)
- [`../agents/copilot-extensibility-architect.md`](../agents/copilot-extensibility-architect.md) · [`../agents/agents-sdk-engineer.md`](../agents/agents-sdk-engineer.md)
- [Custom engine agents overview](https://learn.microsoft.com/microsoft-365/copilot/extensibility/overview-custom-engine-agent) — the development-approach comparison (Copilot Studio / Teams AI / Agents SDK / Foundry)

## Provenance

Codifies house opinions #1, #4, and #15 from [`../CLAUDE.md`](../CLAUDE.md). Grounded in the Microsoft Learn custom-engine-agent overview (the four-way development comparison, channels, orchestrator/model BYO) and the Agents-SDK overview, retrieved 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
