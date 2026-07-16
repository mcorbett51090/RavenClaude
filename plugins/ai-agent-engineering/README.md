# ai-agent-engineering

> The **agentic-systems software-engineering layer** for Claude Code — the team that answers *"does this even need an agent, and if so — single or multi-agent, which framework, how do we build it, and how do we know it works?"* and then builds, hardens, and evaluates the agent. Two agents: the **agentic-systems-architect** (triages the task — usually to *"a workflow or single call wins"* — then chooses single-vs-multi-agent, the topology, the framework, and the cost/latency/guardrail budget) and the **agent-implementation-engineer** (designs tools & context/memory, builds the loop with caps/timeouts/human-in-the-loop/tracing, and runs the offline agent-eval harness).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## The honest stance up front

**Most tasks people want to "make agentic" do not need an agent.** This team's #1 discipline is **triage**, and its default verdict is *"a fixed workflow or a single LLM call wins — don't build the agent."* An agent (an LLM directing its own tool use over an unknown number of steps) buys flexibility you pay for in non-determinism, cost, and latency — so the burden of proof is on the agent, and the decisive question is always *"is the control flow knowable in advance?"* The most valuable thing this plugin often delivers is talking a team *out* of an agent they don't need. The framework/model/API landscape also moves monthly, so every framework/model/pricing claim carries a **retrieval date + [verify-at-use]** — this is engineering judgment, not a benchmark.

## What it does

| You ask | It returns |
|---|---|
| "Should we build an agent for this?" | A go/no-go triage verdict — is the control flow knowable in advance? — usually *"build a workflow or a single call instead,"* said plainly, with the cheaper pattern spelled out |
| "Is this an agent or a workflow?" | The pattern (single call / prompt-chaining / routing / parallelization / agent) with the reason, defaulting to the most deterministic option that works |
| "Single agent or multi-agent?" | A topology decision defaulting to one agent with a good tool set — multi-agent only with a named reason (parallel subtasks / context too big / a hard trust boundary) |
| "LangGraph, CrewAI, the OpenAI/Claude Agents SDK?" | A framework recommendation tied to the requirements, with the lock-in and the escape hatch named, specifics marked verify-at-use |
| "Write / fix the agent's tools." | Tool schemas with unambiguous names, typed params, examples, and errors that teach recovery — with the tool count kept small enough for reliable selection |
| "The context overflows / the agent drifts." | A context strategy (in-window / summarized / external) and a memory design (short-term scratchpad vs long-term store) under a per-turn token budget |
| "Build the loop / how do I know it works?" | An instrumented loop (step caps, timeouts/retries, stop conditions, human-in-the-loop on irreversible actions) and an offline eval harness scoring task-completion + trajectory + tool-use, with cost & latency reported |

**Two rules it never breaks:** *triage first — a workflow or single call wins by default, and an agent must earn the non-determinism it costs*, and *a demo is not a result* (an agent isn't trusted until it's scored on task-completion + trajectory + tool-use, offline against a frozen task set, with cost and latency next to the quality).

## What's inside

- **2 agents** — `agentic-systems-architect` (triages the task, then chooses single-vs-multi-agent, topology, framework, and the cost/latency/guardrail budget) and `agent-implementation-engineer` (designs tools & context/memory, builds & hardens the loop, and runs the offline agent-eval harness).
- **3 skills** — `triage-agentic-approach`, `design-agent-tools-and-context`, `evaluate-and-harden-agent`.
- **2 knowledge files** — an agent decision tree (the agent-vs-not Gate 0 → single-call/workflow patterns → single-vs-multi → topology → framework, + budget/guardrail tiers) and a dated 2026 agent-patterns reference (the LLM-in-a-loop invariant, the minimal loop, tool design, context & memory, planning & reflection, multi-agent coordination, guardrails & prompt-injection, evaluation, cost/latency, and a framework-landscape snapshot).
- **2 templates** — an agent system design doc (the triage → design captured before building) and an agent eval plan (the frozen task set, scorers, hardening checklist, and cost/latency ceilings before trusting an agent).

## Where it sits in the stack

```
ai-agent-engineering (HERE)          →  BUILD the agent (LLM-in-a-loop-with-tools)   ("does it need an agent, which one, and does it work?")
ai-rag-engineering                   →  the retrieval/RAG pipeline behind a tool     ("chunking / embeddings / vector DB / reranking")
prompt-engineering                   →  single-call prompt/context craft (no loop)   ("the prompt inside one call")
llm-evaluation-engineering           →  general non-agent LLM eval harnesses         ("is this model/prompt good?")
claude-app-engineering               →  Claude-specific end-user product apps        ("the Claude product")
conversational-ai-voice-engineering  →  real-time voice agents                       ("voice / turn-taking / ASR / TTS")
```

This plugin is the **agentic-systems layer**: it decides whether a task even needs an agent and builds/hardens/evaluates the loop, and stays clear of the retrieval pipeline behind a tool (`ai-rag-engineering`), the single-call prompt craft (`prompt-engineering`), general non-agent eval harnesses (`llm-evaluation-engineering`), Claude-specific end-user apps (`claude-app-engineering`), and real-time voice (`conversational-ai-voice-engineering`).

## Domain stance

Concept-first (the agent-vs-workflow gate, single-vs-multi-agent, orchestration topologies, tool/function design, context-window & memory management, planning & reflection loops, guardrails & prompt-injection defense, and agent evaluation on task-completion + trajectory + tool-use), fluent across **LangGraph, the OpenAI Agents SDK, the Claude Agent SDK, CrewAI, AutoGen**, and the plain-SDK loop that every framework should be measured against. Because the framework/model/API landscape is volatile, every version carries a **retrieval date + [verify-at-use]** — re-verify before pinning in a client deliverable.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install ai-agent-engineering@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
