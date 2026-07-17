# ai-agent-engineering

> The **agent-systems layer** for Claude Code — the team that answers *"what is the simplest agent topology that works, and how do we make it reliable, observable, evaluated, and within budget?"* and builds the answer. Two agents: the **agentic-systems-architect** (decides the topology, framework/runtime, tool boundary, memory/state, and the guardrail & eval strategy + cost/latency budget) and the **agent-implementation-engineer** (wires the tools & control-flow, adds retries/timeouts/idempotency, instruments tracing, and builds the eval harness).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

> **Volatile substrate.** LLM/model, agent-framework, and pricing specifics move fast — model names, tool-calling APIs, framework APIs, context windows, and token prices carry a retrieval date — verify at use before pinning a model, a price, or an API in a design or a bill estimate.

## What it does

| You ask | It returns |
|---|---|
| "Should this be a single agent or multi-agent — and which orchestration pattern?" | A topology recommendation (single-agent/ReAct → planner-executor → multi-agent → workflow/graph) grounded in the decision tree, with the conditions that would flip it |
| "Roll our own or use LangGraph / an agent SDK?" | A framework/runtime recommendation (roll-your-own vs graph runtime vs agent SDK — provider-neutral) tied to the topology, control-flow, and observability needs |
| "Where's the tool boundary, and how do we design the function-call contracts?" | A tool catalog with narrow, typed, single-responsibility contracts (schemas, validation, idempotency) — and what stays deterministic code, not a tool |
| "What's our memory / context / state strategy?" | A memory strategy (scratchpad / running-summary / vector recall) and a per-turn context-assembly plan budgeted to the window |
| "What guardrails do we need, and what's the eval + cost/latency budget?" | A guardrail catalog (input/output validation, tool-permission scoping, human-in-the-loop, injection defense), an eval-tier plan, and a stated tokens/call · calls/task · p50/p95 budget |
| "Wire up these tools and the control-flow, with retries and idempotency." | An orchestration implementation: the loop/graph, typed tool contracts, retries/timeouts/idempotency, failure handling, and prompt-assembly plumbing |
| "Build the eval harness and a regression gate." | Offline eval sets, a calibrated LLM-as-judge, a CI regression gate, guardrail tests, online monitoring, and a red-team pass |

**Two rules it never breaks:** *the simplest topology that works* (reach for multi-agent only when a single agent provably can't; a fixed graph beats a free-roaming agent when the steps are known), and *an agent without an eval harness is a demo, not a system* (offline sets + a calibrated judge + a regression gate before "it works").

## What's inside

- **2 agents** — `agentic-systems-architect` (decides the topology, framework/runtime, tool boundary & contracts, memory/context/state strategy, and the guardrail & eval strategy + cost/latency budget) and `agent-implementation-engineer` (implements the control-flow, typed tool contracts, retries/timeouts/idempotency & failure handling, tracing/observability, prompt-assembly plumbing, and the eval harness — offline sets, LLM-as-judge, regression gates, guardrail tests, online monitoring, red-team).
- **3 skills** — `design-agent-architecture`, `build-agent-orchestration-and-tools`, `harden-and-evaluate-agent`.
- **2 knowledge files** — a Mermaid agent-engineering decision tree (topology choice, tool-vs-code boundary, memory strategy, guardrail placement, eval-tier + trade-off tables) and a 2026 agent-patterns reference (orchestration topologies, tool/function-call design, memory & context, failure handling, guardrails, tracing/observability, the eval harness, cost & latency, and a dated framework/model/tooling map).
- **2 templates** — an agent architecture design doc and an agent eval & guardrail plan.

## Where it sits in the AI/LLM stack

```
ai-agent-engineering (HERE)   →  the RUNNING AGENT SYSTEM        ("what topology; make it reliable, observable, evaluated, budgeted")
ai-rag-engineering            →  retrieval / RAG                 ("the index the agent calls as a tool")
prompt-engineering            →  the prompt & context craft      ("the wording the agent assembles")
llm-evaluation-engineering    →  eval methodology as a discipline ("the eval science the harness consumes")
observability-sre             →  run the service on-call         ("the platform the agent runs on")
backend-engineering           →  the surrounding service         ("the APIs/queues/datastores around it")
```

This plugin is the **agent-systems layer**: it *composes* prompts, retrieval, tools, and evals into a running production agent, and stays clear of the *retrieval index* (`ai-rag-engineering`), the *prompt wording* (`prompt-engineering`), and the *eval science* (`llm-evaluation-engineering`).

## Domain stance

Concept-first (the simplest topology that works, single-agent/ReAct → planner-executor → multi-agent → workflow/graph, tool-boundary-as-API-contract, every-tool-call-can-fail with retries/timeouts/idempotency, guardrails-and-tracing-as-architecture, context-is-a-budget, determinism-where-you-can, and no-system-without-an-eval-harness), fluent across **orchestration topologies** (ReAct, planner/executor, multi-agent, graph/workflow runtimes like **LangGraph**), **tool/function-calling** and **MCP** tool design, **memory & context** management (scratchpad / summary / vector recall), **failure handling** (retry/backoff/jitter, timeouts, idempotency keys), **guardrails & safety** (input/output validation, tool-permission scoping, human-in-the-loop, prompt-injection defense), **tracing/observability** (per-step spans: tokens, latency, cost, decision), **cost & latency budgets**, and the **agent-eval harness** (offline sets, LLM-as-judge, regression gates, online monitoring, red-team). Model names, tool-calling / framework APIs, context windows, and token prices carry retrieval dates — re-verify before pinning in a design or a bill estimate.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install ai-agent-engineering@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
