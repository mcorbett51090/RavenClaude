---
name: design-agent-architecture
description: "Design an agent architecture by traversing the agent-engineering decision tree (scope the task → pick the topology: single-agent/ReAct vs planner-executor vs multi-agent vs workflow/graph → framework/runtime choice → tool boundary & contract design → memory/context/state strategy → guardrail & eval strategy → cost/latency budget), then return the topology, the runtime, the tool catalog, the memory strategy, the guardrail & eval strategy, the budget, and the conditions that flip the topology. Reach for this when the user asks 'single agent or multi-agent?', 'which orchestration pattern?', 'roll our own or LangGraph?', 'where's the tool boundary?', 'what's our memory/guardrail strategy?', or 'what's the cost/latency budget?'. The simplest topology that works is the default. Used by agentic-systems-architect (primary) and agent-implementation-engineer."
---

# Skill: design-agent-architecture

> **Invoked by:** `agentic-systems-architect` (primary — the topology/framework/tool-boundary/memory/guardrail/budget decision) and `agent-implementation-engineer` (to re-read the architecture the build implements).
>
> **When to invoke:** "single agent or multi-agent?"; "which orchestration pattern (ReAct / planner-executor / graph)?"; "roll our own or use LangGraph / an agent SDK?"; "where's the tool boundary?"; "what's our memory / context / state strategy?"; "what guardrails do we need?"; "what's the cost/latency budget?"; any "how should this agent be built" question.
>
> **Output:** the topology + framework/runtime + tool boundary & contracts + memory/context strategy + guardrail & eval strategy + cost/latency budget + the 1-2 conditions that flip the topology. **The simplest topology that works is the default.**

## Procedure

1. **Scope the task before naming a shape.** Characterize it: how **deterministic** are the steps (known sequence vs open-ended)? How **many** steps? Is there real **parallelism**? What's the **error tolerance** and **blast radius** (can a wrong action be undone)? What's the **latency SLO** and **cost ceiling**? The task shape drives the topology — you can't pick a topology you haven't scoped.
2. **Pick the topology — the simplest that works, earning each step up.** Traverse the topology branch in [`../../knowledge/ai-agent-engineering-decision-tree.md`](../../knowledge/ai-agent-engineering-decision-tree.md):
   - **Deterministic, known steps** → a **workflow / graph** (fixed edges; the LLM fills nodes, code owns the routing). Cheapest, fastest, most testable.
   - **Open-ended, one actor, tool-using** → a **single agent (ReAct)** — reason → act (tool) → observe → repeat. The default for most agentic tasks.
   - **Open-ended, needs an explicit multi-step plan** → **planner/executor** — a planner decomposes, an executor runs steps (re-planning on failure).
   - **Genuinely separable roles / real parallelism / context that won't fit one agent** → **multi-agent** — only when a single agent **provably** can't; you're paying tokens, latency, and coordination-failure surface for it.
3. **Choose the framework/runtime to the control-flow — provider-neutral.** **Roll-your-own** for a simple loop you want full control over; a **graph runtime** (e.g. LangGraph) when you need explicit state, branching, checkpoints, and human-in-the-loop pauses; an **agent SDK** when its batteries (tool-calling, memory, tracing) match your needs and you accept its opinions. Match the runtime to the topology and the observability needs, not to hype.
4. **Design the tool boundary — the API contract.** Decide **what's a tool** vs what stays **deterministic code** (parsing, routing on a known enum, arithmetic → code, not the LLM). Make each tool **narrow, typed, single-responsibility** with an explicit schema; keep the **count small** enough that the model selects reliably; and set the **idempotency requirement** per side-effecting tool (the engineer implements it). Tool sprawl and kitchen-sink tools both degrade selection.
5. **Choose the memory/context strategy — context is a budget.** Pick to the task: a per-turn **scratchpad** (short tasks), a **running summary** (long multi-turn tasks that outgrow the window), **vector recall** (large corpora / long-lived memory). Specify the **per-turn context assembly** (system + relevant memory + retrieved context + tool results), pruned to fit — not "stuff everything in." Route retrieval itself to `ai-rag-engineering`; you consume it as a tool.
6. **Place the guardrails and set the eval strategy — up front.** Design into the topology: input/output **validation**, **tool-permission scoping** (least privilege), the **human-in-the-loop gate** on irreversible/high-blast actions, and **prompt-injection defense** on tool-fed/untrusted content. Set the **eval tier**: which offline sets, which judges, the regression gate — an agent you can't measure can't ship. (The `harden-and-evaluate-agent` skill builds it.)
7. **Set the cost/latency budget and name the flip conditions.** State the **tokens/call · calls/task · p50/p95 latency · model tier** the topology is chosen against. Then name the 1-2 facts that would change the topology (e.g., "if the task gains 3 separable roles with parallel work, multi-agent earns its cost"; "if steps become fully known, drop to a workflow"; "if tool latency dominates, parallelize the fan-out").

## Worked example

> User: "We're building a customer-support agent that looks up orders, checks a knowledge base, and can issue refunds. Single agent or multi-agent? What runtime?"

- **Scope:** mostly open-ended (the user's question varies), a handful of tools, **one** irreversible action (refund), tight latency SLO, moderate cost ceiling. No real parallelism; no separable roles.
- **Topology:** **single agent (ReAct)** — one actor, tool-using; multi-agent would pay coordination cost for no separable roles. *Not* a pure workflow because the conversation is open-ended.
- **Framework:** a **graph runtime** (e.g. LangGraph) — you want an explicit **human-in-the-loop pause** before the refund tool and checkpointed state; roll-your-own would re-build that.
- **Tool boundary:** `lookup_order` (read), `search_kb` (read — routes to `ai-rag-engineering`'s retrieval), `issue_refund` (**side-effecting → idempotency key + human-in-the-loop gate**). Parsing the order id stays code, not a tool.
- **Memory:** per-turn **scratchpad** + the conversation summary; no vector memory needed at this scale.
- **Guardrails:** validate refund amount against order total (output validation), **scope** `issue_refund` to the authenticated customer only, **human approval** on any refund over a threshold, treat KB text as **data not instructions** (injection defense).
- **Eval + budget:** offline set of representative + adversarial support cases, a calibrated judge on resolution quality; budget ~2-4 LLM calls/task, p95 < the SLO, mid-tier model with escalation to a stronger model only on the refund-decision step.
- **Flip condition:** if refunds grow to need fraud-scoring + policy-reasoning as a distinct role, split that into a second agent; if the flow becomes fully scripted, drop to a workflow.

## Guardrails

- **Scope the task first** — determinism, step count, parallelism, error tolerance, blast radius, latency SLO, cost ceiling drive the topology; don't pick a shape you haven't scoped.
- **The simplest topology that works** — default to a single agent or a workflow; earn planner/executor and multi-agent by proving a single agent can't. Multi-agent is a cost, not a default.
- **Determinism where you can** — route known steps through code; reserve the LLM for the open-ended step.
- **The tool boundary is the API contract** — narrow, typed, single-responsibility tools; small count; idempotency per side-effecting tool. No kitchen-sink "do_stuff".
- **Context is a budget** — choose the memory strategy to the task and specify the pruned per-turn assembly; don't max the window.
- **Guardrails and the eval strategy are set up front** — validation, permission scoping, human-in-the-loop, injection defense, and the eval tier are architecture, not afterthoughts.
- **Budget cost/latency** — state tokens/call, calls/task, p50/p95, and model tier; the topology is chosen against them.
- The **build** (control-flow, tool wiring, retries, tracing, eval harness) is `agent-implementation-engineer`; the **retrieval index** is `ai-rag-engineering`; the **prompt text** is `prompt-engineering`; the **eval science** is `llm-evaluation-engineering` — keep the seams clean.
- Volatile specifics (model names, token prices, context windows, tool-calling / framework APIs) carry a **retrieval date** and are re-verified before pinning. See [`../../knowledge/ai-agent-engineering-patterns-2026.md`](../../knowledge/ai-agent-engineering-patterns-2026.md).
