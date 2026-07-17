---
name: build-agent-orchestration-and-tools
description: "Build and harden the agent's runtime by traversing the build discipline (implement the control-flow: loop/graph with a loop-cap & budget guard → typed tool/function-call contracts with input/output validation → failure handling: timeouts, retry with backoff+jitter, idempotency keys → memory store & the per-turn context assembly → prompt-assembly plumbing → per-step tracing: tokens, latency, cost, decision), then return the built control-flow, the tool contracts, the failure-handling layer, the memory/context plumbing, and the tracing. Reach for this when the user asks 'wire up these tools and the control-flow', 'add retries/timeouts/idempotency', 'build the planner/executor loop', or 'instrument tracing/observability'. Used by agent-implementation-engineer (primary) and agentic-systems-architect (to sanity-check buildability)."
---

# Skill: build-agent-orchestration-and-tools

> **Invoked by:** `agent-implementation-engineer` (primary — the control-flow, tool wiring, failure handling, memory, and tracing build) and `agentic-systems-architect` (to sanity-check the chosen topology/tool boundary is buildable).
>
> **When to invoke:** "wire up these tools and the control-flow"; "build the ReAct loop / planner-executor / graph"; "design the function-call contracts"; "add retries / timeouts / idempotency / failure handling"; "build the memory store"; "instrument tracing/observability"; any "make the agent actually run and be debuggable" task.
>
> **Output:** the implemented control-flow (loop/graph, loop-cap, budget guard) + the typed tool contracts (validation, timeout, retry, idempotency) + the memory/context plumbing + the per-step tracing — built to the architect's architecture.

## Procedure

1. **Implement the control-flow to the topology — and cap it.** Build what the architect chose: a **ReAct loop** (reason → act → observe → repeat), a **planner/executor** (plan → run steps → re-plan on failure), or a **workflow/graph** (fixed edges, code owns routing). Put a **loop-cap** (max steps) and a **budget guard** (max tokens/cost per task) on it up front — a stuck agent must terminate, not spin the bill. Read [`../../knowledge/ai-agent-engineering-patterns-2026.md`](../../knowledge/ai-agent-engineering-patterns-2026.md) for the orchestration mechanics.
2. **Build each tool as a typed, validated contract.** A tool is a **narrow, single-responsibility** function with an **explicit schema** (name, description the model reads, typed parameters). **Validate the inputs** before executing and **validate the outputs** before returning them to the model. Keep the tool description precise — it's how the model decides to call it. Whether you expose tools via native function-calling or **MCP**, the contract discipline is the same.
3. **Assume every tool call fails — build the failure-handling layer.**
   - **Timeout** every call — a tool with no timeout is a hang that stalls the whole task.
   - **Retry** transient failures (network, rate-limit, 5xx) with **exponential backoff + jitter**, capped attempts; do **not** retry deterministic failures (validation, 4xx).
   - Make side-effecting tools **idempotent** — an **idempotency key** so a retry doesn't double-write / double-charge / double-send.
   - Return a **structured error** to the model (what failed, whether it's retryable), not a raw stack trace — so the agent can recover or degrade gracefully.
4. **Build the memory store and the per-turn context assembly — to the budget.** Implement the memory strategy the architect chose (**scratchpad** / **running summary** / **vector recall**) with **bounded growth**. Assemble the window each turn deliberately — system + relevant memory + retrieved context + recent tool results — **pruned to fit**; don't concatenate the entire history every turn. The retrieval itself is `ai-rag-engineering`'s tool; you call it and place its results.
5. **Wire the prompt-assembly plumbing.** Assemble the prompt from parts (system, memory, tools spec, context, the turn) — the *wording* is `prompt-engineering`'s craft; you own the **plumbing** that assembles it deterministically and keeps it within the token budget.
6. **Instrument tracing as you build — every step is a span.** Emit a **span** for every LLM call, tool call, and state transition, capturing **inputs, outputs, tokens, latency, cost, and the decision**. Roll up **per run** (tokens/task, calls/task, p50/p95 latency, cost/task) and wire it to a trace backend. Instrument as you build, not after — an un-traced failure is un-diagnosable, and the cost/latency budget is unobservable without it.
7. **Prove it runs and hand off to hardening.** Exercise the happy path and a failure path (a tool timeout, a validation reject, a retry) and confirm the loop-cap and budget guard fire. Then hand to [`harden-and-evaluate-agent`](../harden-and-evaluate-agent/SKILL.md) for the eval harness, guardrail tests, and red-team — building it is not the same as proving it's correct or safe.

## Worked example

> User: "Wire up our support agent's three tools (lookup_order, search_kb, issue_refund) in a ReAct loop with proper failure handling and tracing."

- **Control-flow:** a **ReAct loop** with a **loop-cap of 8 steps** and a **budget guard of 20K tokens / $X per task**; on cap-hit it returns a "couldn't complete" with the trace, not an infinite spin.
- **Tool contracts:** `lookup_order(order_id: str)` → validated order-id format; `search_kb(query: str)` → calls the retrieval tool; `issue_refund(order_id: str, amount: Money, idempotency_key: str)` → **validates `amount ≤ order total`**, requires the key.
- **Failure handling:** 10s timeout on each; retry `lookup_order`/`search_kb` on 5xx/timeout with backoff+jitter (3 attempts); `issue_refund` retried **only** with the same **idempotency key** so a retry can't double-refund; a validation failure returns a structured error the model can act on, no retry.
- **Memory:** running conversation summary + a per-turn scratchpad; window assembled as system + summary + tools + last-N tool results, pruned to the budget.
- **Tracing:** each LLM/tool call is a span (tokens, latency, cost, decision); a run rollup reports 3.2 calls/task, p95 4.1s, $0.03/task — so the architect's budget is checkable.
- **Hand-off:** to `harden-and-evaluate-agent` for the offline eval set, the injection test on `search_kb` results, and the human-in-the-loop test on `issue_refund`.

## Guardrails

- **Cap the loop and the budget** — a max-steps loop-cap and a max-tokens/cost budget guard are mandatory; a stuck agent must terminate.
- **Every tool is a typed, validated contract** — explicit schema, validated inputs and outputs, narrow single responsibility; a precise description drives model selection.
- **Every tool call assumes failure** — timeout always; retry transient (backoff + jitter, capped), never retry deterministic failures; **idempotency key on every side-effecting tool**; structured errors back to the model.
- **Context is a budget** — bounded memory growth and a pruned per-turn assembly; never concatenate the whole history each turn.
- **Trace as you build** — per-step spans (tokens/latency/cost/decision) + a run rollup; instrumentation is part of the build, not a follow-up.
- **Building ≠ proving** — hand off to `harden-and-evaluate-agent` for the eval harness, guardrail tests, and red-team.
- The **topology / tool boundary** is the `agentic-systems-architect`'s call — kick a topology gap back up, don't invent one mid-build; the **retrieval tool internals** are `ai-rag-engineering`; the **prompt wording** is `prompt-engineering`.
- Volatile specifics (model names, token prices, context windows, tool-calling / framework / MCP APIs) carry a **retrieval date** and are re-verified before pinning in code. See [`../../knowledge/ai-agent-engineering-patterns-2026.md`](../../knowledge/ai-agent-engineering-patterns-2026.md).
