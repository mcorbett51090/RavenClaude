# Convert a declarative agent to a custom-engine agent by re-homing the grounding and wiring the seams — don't rebuild from scratch

**Status:** Pattern — strong default for the DA→CEA conversion path; the connectors and actions survive the move, the orchestration/state/channels become yours, and the engine + host route out.

**Domain:** Agent design / DA→CEA conversion

**Applies to:** `microsoft-365-copilot`

---

## Why this exists

When a declarative agent hits the hard-limit wall (a loop it can't do, a proactive trigger, an off-M365 channel), the instinct is to throw it away and start a custom-engine agent (CEA) from zero. That wastes the parts that transfer. In a CEA on the M365 Agents SDK, what *changes* is the orchestration loop (now yours, iterative, model- and orchestrator-agnostic), the state/turn management, and the channels (now M365 Copilot + Teams + web + the 10+ Agents-SDK channels). What *survives* is the grounding: the Copilot connectors and API plugins you already built still apply — a CEA does its own retrieval via Microsoft Graph APIs and the **Retrieval API** for M365 data, but the connector schema and the plugin's OpenAPI are reusable assets, not throwaway. The conversion is a re-home, not a rewrite, and the two heaviest new pieces — the engine and the host — are explicitly *other plugins'* jobs. Getting the seams right is what keeps this plugin's scope to the Agents-SDK surface.

## How to apply

Inventory what the DA already has, then map each piece to its new owner. The SDK takes orchestration/state/channels; the grounding re-homes via Graph/Retrieval API; the engine and host route out.

```text
DA asset                    →  CEA destination
─────────────────────────────────────────────────────────────────────
instructions/system prompt  →  engine (claude-app-engineering owns prompt/orchestrator)
single grounding op         →  iterative retrieval in the orchestrator loop (now allowed)
Copilot connector(s)        →  reused; CEA retrieves via Graph APIs / Retrieval API
API plugin(s) / OpenAPI     →  reused as tools the orchestrator calls (now can loop)
conversation starters       →  channel-specific UX in the Agents-SDK app
— (new) —                   →  channel/turn/state, streaming, citations  (THIS plugin)
— (new) —                   →  orchestrator + model + evals + caching    → claude-app-engineering
— (new) —                   →  Entra app reg + host (Foundry/ACA/Functions) → azure-cloud
— (new) —                   →  app package + org-catalog approval         → copilot-admin-governance
```

**Do:**
- Reuse the existing connectors and API plugins — re-home the *retrieval*, don't rebuild the grounding.
- Keep channel/turn/state, streaming, and **citations** (citations are part of the contract, not a nicety) in the Agents-SDK layer this plugin owns.
- Route the engine to `claude-app-engineering` and the Entra app reg + host to `azure-cloud` — name the requirement, they build it.
- Plan the **Bot Framework → Agents SDK** migration if the source is a legacy BF bot — BF bots port to the SDK.

**Don't:**
- Rebuild grounding from scratch when the connector/plugin already exists.
- Host the agent or write the orchestrator inside this plugin's design — honor the seams (#15).
- Ship the converted CEA without citations or without the app-package + admin gate (#12, #13).

## Edge cases / when the rule does NOT apply

If the DA's grounding was **SharePoint/OneDrive knowledge** (not a connector or plugin), the CEA re-homes it via the **Retrieval API** over Graph (PAYG-metered for non-Copilot-licensed users, `[verify-at-build]`) rather than a reusable connector schema. A **Foundry** path can publish to Copilot directly and auto-provision the Bot Service + Entra app reg, collapsing some of the `azure-cloud` hand-off — but the host residency/identity still routes to `azure-cloud`. If the target is a Copilot-Studio / Dataverse CEA, the whole conversion is the `power-platform` seam, not this one.

## See also

- [`./cea-escalate-to-custom-engine-only-when-a-hard-limit-forces-it.md`](./cea-escalate-to-custom-engine-only-when-a-hard-limit-forces-it.md) — the *decision* this rule executes
- [`./connector-choose-synced-vs-federated-and-set-crawl-refresh.md`](./connector-choose-synced-vs-federated-and-set-crawl-refresh.md) — the grounding that survives the conversion
- [`../knowledge/agents-sdk-and-toolkit-2026.md`](../knowledge/agents-sdk-and-toolkit-2026.md) · [`../agents/agents-sdk-engineer.md`](../agents/agents-sdk-engineer.md)
- [Bot Framework → Agents SDK migration](https://learn.microsoft.com/microsoft-365/agents-sdk/bf-migration-guidance) · [Create and deploy an agent with the Agents SDK](https://learn.microsoft.com/microsoft-365/copilot/extensibility/create-deploy-agents-sdk)

## Provenance

Codifies the DA→CEA-conversion discipline behind house opinions #1 and #15 from [`../CLAUDE.md`](../CLAUDE.md). Grounded in the Microsoft Learn Agents-SDK build pages (model/orchestrator-agnostic, multi-channel, "access the same data via Microsoft Graph APIs and use the Retrieval API for grounding") and the BF-migration guidance, retrieved 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
