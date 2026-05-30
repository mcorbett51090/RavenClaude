# Design a declarative agent to ~66% of every hard limit — and never assume it can loop

**Status:** Absolute rule — the limits are platform-enforced and inclusive of overhead; a design at the ceiling fails in production.

**Domain:** Agent design / declarative-agent sizing

**Applies to:** `microsoft-365-copilot`

---

## Why this exists

A declarative agent runs inside Microsoft 365 Copilot under a fixed wall: 50 grounding items, 25 plugin-response items, ~4,096 tokens, a 45-second end-to-end timeout, and an orchestration of exactly **one grounding op + one tool call, sequential, with no loops**. Every one of those numbers is *inclusive of system overhead*, so the usable budget is well under the headline. Two failure modes follow: (1) a design sized to the ceiling that intermittently truncates or times out as overhead eats the margin, and (2) a task that genuinely needs iteration — which a declarative agent simply cannot do. This is house opinions #3 and #4. The moment a task needs a loop, it is a custom-engine agent, not a declarative one.

## How to apply

Pin the manifest schema (never "latest"), keep `instructions` under the ~8,000-char budget, declare only the capabilities you need, and budget every limit to two-thirds.

```jsonc
{
  // PIN the schema — the manifest ships ~monthly; "latest" is a time bomb (#2)
  "$schema": "https://developer.microsoft.com/json-schemas/copilot/declarative-agent/v1.7/schema.json",
  "version": "v1.7",
  "name": "Contoso Policy Assistant",
  "description": "Answers HR-policy questions from the indexed policy library.",
  // ~8,000-char budget: role + scope + tone + refusal rules ONLY.
  // Push reference detail into grounding, not the prompt.
  "instructions": "You are an HR-policy assistant. Answer only from the connected policy library...",
  "capabilities": [
    { "name": "GraphConnectors", "connections": [{ "connection_id": "contosoPolicies" }] }
  ]
}
```

**Do:**
- Budget to **~66%** of 50 grounding / 25 plugin-response / ~4,096 tokens / 45 s — they are inclusive of overhead.
- Keep orchestration to a single grounding op + single tool call, sequential.
- Pin `$schema`/`version` to a known manifest version (currently v1.7) and bump deliberately.
- Move reference detail into grounding sources; keep `instructions` lean and under ~8,000 chars.

**Don't:**
- Size a design to the ceiling of a hard limit.
- Assume a declarative agent can iterate, retry, or chain multiple tool calls — it cannot (#4).
- Ship on schema validity alone — schema-valid ≠ behaviorally correct (golden-prompt regression set required, #15).

## Edge cases / when the rule does NOT apply

When the task *needs* a loop, iterative reasoning, proactive/autonomous behavior, an off-M365 channel, or a non-Copilot model, the rule's premise is gone — you are building a **custom-engine agent** (`agents-sdk-engineer`), which is hosted and carries its own ops burden. The exact limit values and current schema version ship monthly and are tagged `[verify-at-build]`; re-verify the v-number and the numbers against the architecture doc before you rely on them.

## See also

- [`../knowledge/declarative-agent-manifest-2026.md`](../knowledge/declarative-agent-manifest-2026.md) — the full limits table, capability map, and validation gates
- [`../knowledge/agent-platform-decision-2026.md`](../knowledge/agent-platform-decision-2026.md) — the declarative-vs-custom-engine decision tree
- [`../skills/declarative-agent-manifest-authoring/SKILL.md`](../skills/declarative-agent-manifest-authoring/SKILL.md) — field-by-field manifest authoring + the budget math
- [`../agents/declarative-agent-engineer.md`](../agents/declarative-agent-engineer.md) — the agent that enforces this wall

## Provenance

Codifies house opinions #2, #3, #4, and #15 from [`../CLAUDE.md`](../CLAUDE.md). Grounded in [`../knowledge/declarative-agent-manifest-2026.md`](../knowledge/declarative-agent-manifest-2026.md), sourced from the Microsoft Learn declarative-agent architecture and manifest-v1.7 pages.

---

_Last reviewed: 2026-05-30 by `claude`_
