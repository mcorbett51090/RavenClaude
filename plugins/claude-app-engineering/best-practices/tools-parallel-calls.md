# Request parallel tool calls when tasks are independent

**Status:** Pattern
**Domain:** Tool use / latency
**Applies to:** `claude-app-engineering`

---

## Why this exists

Claude can emit multiple `tool_use` blocks in a single response when tasks are
independent, running them concurrently and cutting round-trip latency by the
depth of the dependency chain. Teams that don't express this capability in their
tool schemas or system prompt get a sequential execution of N inherently-parallel
ops — a preventable latency tax that compounds in agentic loops.

## How to apply

1. In your system prompt, state: "You may call multiple tools in one response when
   their inputs do not depend on each other."
2. Execute all `tool_use` blocks with ids from a single assistant turn in parallel
   (fan-out via `asyncio.gather`, `Promise.all`, etc.) and return all `tool_result`
   blocks in a **single** user turn.
3. Never fire the next Messages API call until you have returned every result from
   the current tool batch.

```python
import asyncio, anthropic

async def run_tools(tool_calls):
    return await asyncio.gather(*[dispatch(tc) for tc in tool_calls])

# In the loop:
tool_calls = [b for b in response.content if b.type == "tool_use"]
results = asyncio.run(run_tools(tool_calls))
tool_results = [
    {"type": "tool_result", "tool_use_id": tc.id, "content": r}
    for tc, r in zip(tool_calls, results)
]
```

**Do:**
- Fan out all tool calls from a single assistant turn before returning any result.
- Return all results in one `user` turn so the model sees a complete state update.
- Signal parallelism eligibility in your schema/prompt for tools like `search`,
  `read_file`, `call_api` that have no shared state.

**Don't:**
- Return tool results one-by-one with separate API calls (one result per turn is
  fine if only one call was made; it is wasteful when many were).
- Assume all models parallelise by default — explicitly invite it.
- Force parallel execution when the second tool's input depends on the first
  tool's output.

## Edge cases / when the rule does NOT apply

- When tool B reads the output of tool A, they must be sequential.
- Stateful tools that mutate shared data (e.g. two writes to the same record)
  should be serialised even if the model emits them together.
- Some latency-insensitive batch pipelines (Batch API jobs) don't need the
  in-loop optimisation.

## See also

- [`../agents/agent-sdk-engineer.md`](../agents/agent-sdk-engineer.md) — owns the Messages loop + Agent SDK
- [`./tools-design-as-a-contract.md`](./tools-design-as-a-contract.md) — the description signals parallelism eligibility
- [`./tool-idempotency-for-effects.md`](./tool-idempotency-for-effects.md) — effects need idempotency before they can safely parallelize

## Provenance

Codifies the parallelism pattern from the `tool-use-and-structured-output.md`
knowledge file (retrieved 2026-05-28) and Anthropic's tool-use documentation
(fan-out pattern for independent tool calls). Standard Claude API loop practice.

---

_Last reviewed: 2026-06-05 by `claude`_
