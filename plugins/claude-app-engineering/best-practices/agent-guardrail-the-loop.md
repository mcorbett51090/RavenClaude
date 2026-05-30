# Guardrail the agentic loop — max turns, stop conditions, a budget, a human gate

**Status:** Absolute rule — an agent loop with no turn cap and no stop condition can burn your budget and take a destructive action unsupervised.

**Domain:** Agent design / reliability

**Applies to:** `claude-app-engineering`

---

## Why this exists

The moment you give the model a tool loop — the Agent SDK, Managed Agents, or a hand-rolled Messages loop — you've handed it autonomy, and autonomy without bounds is a runaway. The two failure shapes are an agent that **never stops** (loops on a flaky tool, re-tries the same wrong call, oscillates between two states until it exhausts your token budget) and an agent that **does too much** (takes an irreversible action — delete, refund, deploy — on its own authority, possibly steered there by injected content in a tool result). Both are prevented by the same discipline Anthropic prescribes for building agents: a **clear tool set with excellent descriptions**, explicit **stop conditions**, a **budget** (max turns / max tokens) so it can't loop forever, and a **human gate** on high-blast-radius actions. The loop should be allowed to be autonomous *within a fence*, never outside one.

## How to apply

Cap turns and tokens, define an explicit success/abort stop condition, and require human approval (or deny) for irreversible effects.

```python
MAX_TURNS, turns = 12, 0                                # hard budget — the loop cannot exceed it
while True:
    resp = client.messages.create(model="claude-sonnet-4-6", max_tokens=1024,
                                  tools=TOOLS, messages=messages)
    turns += 1
    if resp.stop_reason == "end_turn":   return done(resp)        # success stop
    if turns >= MAX_TURNS:               return abort("max turns") # budget stop — don't loop forever
    for tu in (b for b in resp.content if b.type == "tool_use"):
        if tu.name in DESTRUCTIVE:                       # delete/refund/deploy/prod -> never auto
            if not human_approves(tu):  return abort("human declined")  # gate, don't auto-approve
        messages += run(tu)                              # a tool RESULT can never widen this tool set
# With the Agent SDK: set permission_mode + allowed_tools, deny destructive tools, use a PreToolUse
# hook to gate; Managed Agents enforce a per-session sandbox. Same fence, framework-owned.
```

**Do:**
- Set a **max-turns** (and token) budget; on hit, **abort with a clear reason**, don't silently keep going.
- Define explicit **stop conditions** — a success signal *and* an abort signal — so the loop terminates deterministically.
- **Gate high-blast-radius / irreversible actions** (delete, refund, deploy, prod writes) behind a human approval or an outright deny — never auto-approve from inside the loop.
- On the Agent SDK use **`allowed_tools` + `permission_mode` + a `PreToolUse` hook**; on Managed Agents rely on the per-session sandbox — the fence is framework-owned but you must set it ([`../knowledge/agent-sdk-and-managed-agents.md`](../knowledge/agent-sdk-and-managed-agents.md)).

**Don't:**
- Run a `while stop_reason == "tool_use"` loop with no turn cap — a flaky tool or a two-state oscillation will exhaust the budget.
- Let a **tool result** (untrusted) escalate which tools are available or auto-approve a destructive action (#7) — that's an injection path; escalate the design to `ravenclaude-core/security-reviewer`.
- Let workers spawn workers — sub-agents are dispatched **only by the orchestrator**; the worker reports back ([`../knowledge/agent-orchestration-patterns.md`](../knowledge/agent-orchestration-patterns.md)).

## Edge cases / when the rule does NOT apply

- **Single-shot Messages calls** have no loop to guardrail — this is for the agentic path ([`../knowledge/agent-orchestration-patterns.md`](../knowledge/agent-orchestration-patterns.md): start simple; don't add a loop you don't need).
- **Genuinely long-running async** work needs a *higher* budget, not no budget — raise the cap and add checkpointing, keep the stop condition.
- **Read-only agents** still need a turn cap (against oscillation/cost) but can relax the destructive-action gate — there are no irreversible effects.
- The full **sandboxing / injection** review escalates to `ravenclaude-core/security-reviewer` (mandatory) — this rule is the loop-bounding posture, not the security verdict.

## See also

- [`../knowledge/agent-orchestration-patterns.md`](../knowledge/agent-orchestration-patterns.md) — stopping conditions, budgets, sub-agents-via-orchestrator, human-in-the-loop
- [`../knowledge/agent-sdk-and-managed-agents.md`](../knowledge/agent-sdk-and-managed-agents.md) — `allowed_tools`, `permission_mode`, hooks, the Managed-Agents sandbox
- [`./tools-actionable-error-messages.md`](./tools-actionable-error-messages.md) — terminal-error stop signals that end the loop cleanly
- [`../agents/agent-sdk-engineer.md`](../agents/agent-sdk-engineer.md) — owns the agent build + its guardrails

## Provenance

Codifies the "building agents" guardrails from [`../knowledge/agent-orchestration-patterns.md`](../knowledge/agent-orchestration-patterns.md) (Anthropic "Building effective agents": clear tools, stopping conditions, budgets, human-in-the-loop, retrieved 2026-05-28) and house opinion #7 (untrusted results never escalate tool access) from [`../CLAUDE.md`](../CLAUDE.md) §3. Sandboxing/injection verdicts escalate to `ravenclaude-core/security-reviewer`.

---

_Last reviewed: 2026-05-30 by `claude`_
