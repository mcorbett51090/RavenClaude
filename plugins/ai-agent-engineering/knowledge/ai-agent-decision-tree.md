# AI Agent Decision Tree

> **Retrieval date:** 2026-07-16. The framework/model/API landscape here changes monthly — treat every named capability, model ID, context window, and price as `[verify-at-use]` and re-check before you commit to it in a build.
>
> **How to use:** traverse top-to-bottom. Stop at the first leaf that fits — the bias is always toward the **simpler, cheaper, more deterministic** option. Do not skip the first gate; it is where most "agent" projects should end.

## Gate 0 — Is the control flow knowable in advance?

This is the decisive question. Everything else is downstream of it.

- **Can you draw the steps as a flowchart before runtime?** → It is **not an agent**. Go to §A (single call) or §B (workflow).
- **Does the path genuinely vary per input, over an unknown number of steps, such that you cannot enumerate it ahead of time?** → It may be an **agent**. Go to §C.

> The trap: teams reach for "agent" because it sounds flexible. Flexibility you don't need is cost, latency, and non-determinism you do pay for. The burden of proof is on the agent.

## §A — Single LLM call

Use when the task is **one shot**: classify, extract, summarize, rewrite, answer-from-context, generate structured output.

- Give it the right context (retrieval, few-shot examples, a clear schema for the output).
- No loop, no tools-directing-tools, no state. Cheapest, most reliable, most debuggable.
- **If a single call with good context works, you are done. Ship it.**

## §B — Workflow (known steps, LLM in fixed slots)

Use when there are **multiple steps but you know them in advance**. The LLM fills fixed slots; *your code* owns the control flow.

Common workflow patterns:

| Pattern | When |
|---|---|
| **Prompt chaining** | Output of step N feeds step N+1, in a known order (draft → critique → revise). |
| **Routing** | Classify the input, then dispatch to one of several known handlers. |
| **Parallelization** | Independent sub-questions answered concurrently, then aggregated. |
| **Orchestrator (fixed stages)** | A lead step plans a *bounded, known* set of sub-steps and merges results. |

Workflows keep determinism, debuggability, and predictable cost. **Prefer a workflow over an agent whenever the steps are enumerable.**

## §C — Agent (LLM directs its own tool use over an unknown number of steps)

Only reach here if Gate 0 sent you here. Now decide the shape.

### C1 — Single-agent vs multi-agent

**Default: a single agent with a good tool set.** It is more debuggable, cheaper, and lower-latency than a swarm.

Reach for **multi-agent** only with a concrete, named reason:

- **Genuinely parallel independent subtasks** (research 5 topics at once, then synthesize).
- **Context a single window can't hold** (separation of concerns forced by size).
- **A hard trust/permission boundary** between roles (one agent may write, another may only read).

No named reason → **single agent.** Every extra agent multiplies coordination cost, token spend, and failure surface.

### C2 — Topology (multi-agent only)

| Topology | Shape | Watch for |
|---|---|---|
| **Orchestrator–worker** | A lead agent delegates to specialist workers and integrates results. | Lead becomes a bottleneck; workers duplicate work. |
| **Sequential pipeline** | Each agent refines the previous one's output. | Error compounds down the chain. |
| **Parallel fan-out + synthesizer** | Independent workers run concurrently; a synthesizer merges. | Merge quality; wasted work if workers overlap. |

Always name the **shared-state design** (how agents see each other's work) and the **failure blast radius** (what breaks if one worker fails).

### C3 — Framework selection

Map requirements → framework. **Know what a plain SDK loop looks like** so you can name what a framework buys and what it locks in.

| Need | Leans toward |
|---|---|
| Maximum control over the loop, explicit state graph, checkpointing | **LangGraph** or a **plain SDK loop** |
| Lightweight provider-native agent loop, hosted tool-use | **OpenAI Agents SDK** / **Claude Agent SDK** |
| Role-based multi-agent collaboration out of the box | **CrewAI** / **AutoGen** |
| Full control, minimal deps, no lock-in | **Plain SDK loop** (build the ~50-line loop yourself) |

For each candidate, state the **lock-in** (how hard to leave) and the **escape hatch** (can you drop to raw SDK calls?). Date every version-volatile capability claim.

### C4 — Budget & guardrails (before any code)

- **Per-run token/cost ceiling** and a **step/tool-call cap** — an unbounded loop is a cost incident.
- **Latency target** and the plan to hit it (early exits, cheaper models for sub-steps, safe parallel tool calls).
- **Guardrail tier sized to blast radius:**
  - Read-only exploration → light (validate outputs, cap steps).
  - Writes to the real world (send/pay/delete/prod) → **human-in-the-loop confirmation on the irreversible step**, tool allowlists, input/output validation.

## Boundary — what this plugin is NOT

- **Retrieval/RAG pipeline** (chunking, embeddings, vector DB, reranking) → `ai-rag-engineering`. (A retrieval *tool* the agent calls can be built here; the pipeline behind it belongs there.)
- **Single-call prompt/context craft** (no loop, no tools directing tools) → `prompt-engineering`.
- **General LLM eval harnesses** (non-agent: quality of a single model/prompt) → `llm-evaluation-engineering`. (Agent-specific trajectory/tool-use/task-completion evals live here.)
- **Claude-specific product apps** (building an end-user Claude app) → `claude-app-engineering`.
- **Which coding model/tool to use** → `ai-coding-model-guidance`.
- **Real-time voice agents** → `conversational-ai-voice-engineering`.
- **Classical MLOps / training pipelines** → `ml-engineering`.
