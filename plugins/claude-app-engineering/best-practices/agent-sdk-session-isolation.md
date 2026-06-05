# Isolate sub-agent context at the session boundary

**Status:** Absolute rule
**Domain:** Claude Agent SDK / orchestration
**Applies to:** `claude-app-engineering`

---

## Why this exists

When an orchestrator spawns a sub-agent and passes the *entire* parent conversation history into its context, two silent failures occur: the sub-agent sees instructions, tool grants, and injected content that were intended for the parent only (privilege escalation through context), and the token cost of every sub-agent call grows unboundedly with conversation depth. The Agent SDK's session model exists precisely to give each worker a clean, scoped context — ignoring that model undermines both the security posture and the FinOps story in one move.

## How to apply

Each sub-agent receives a *purpose-built* context: the task description, the specific inputs it needs, and nothing else from the parent session. The orchestrator translates results back into the parent session — it does not let the sub-agent write directly to the shared state unless that write is the designed contract.

```python
# Orchestrator composes a scoped context for each worker
worker_input = {
    "task": "Summarize the contract clauses relevant to liability.",
    "document_excerpt": relevant_clauses,   # only the slice the worker needs
    # NOT: full_conversation_history, parent_tool_grants, system_prompt
}
worker_result = await sdk.run_agent("clause-summarizer", input=worker_input)
# Orchestrator absorbs and re-frames the result in its own session
```

**Do:**
- Construct a fresh, minimal context for every sub-agent call.
- Let the orchestrator own the state machine; workers return results, not session mutations.
- Cache the sub-agent's stable system prompt above the breakpoint separately from the orchestrator's own breakpoint.

**Don't:**
- Pass `messages` (the full parent thread) directly into a sub-agent's context.
- Let a sub-agent decide which tools the orchestrator may call next.
- Accumulate sub-agent context across turns without intentional pruning.

## Edge cases / when the rule does NOT apply

If the sub-agent *is* a stateful conversational partner (e.g., a long-running multi-turn specialist for a single user session), sharing limited prior turns is intentional — document the shared scope explicitly and audit what tool grants accompany it. Still never share the full parent thread.

## See also

- [`../agents/agent-sdk-engineer.md`](../agents/agent-sdk-engineer.md) — the agent that designs SDK sessions and sub-agent patterns
- [`./untrusted-content-stays-untrusted.md`](./untrusted-content-stays-untrusted.md) — injected content in a sub-agent context is untrusted by default

## Provenance

Codifies `claude-app-engineering/CLAUDE.md` §3 opinion #7 (untrusted content / tool-access escalation) extended to the sub-agent context boundary, plus the Agent SDK session model documented in [`knowledge/agent-sdk-and-managed-agents.md`](../knowledge/agent-sdk-and-managed-agents.md). Reinforced by the orchestration-patterns knowledge bank §context-isolation.

---

_Last reviewed: 2026-06-05 by `claude`_
