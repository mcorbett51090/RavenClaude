---
name: triage-agentic-approach
description: "Decide whether a task should be an agent at all — and if so, single-agent vs multi-agent, the orchestration topology, and the framework — by traversing the agentic decision tree (agent-vs-workflow gate → single-vs-multi → topology → framework), returning a go/no-go verdict that defaults to 'a fixed workflow or a single LLM call wins' unless the control flow is genuinely unknowable in advance. Reach for this when the user asks 'should we build an agent for this?', 'do we need multiple agents?', 'LangGraph or CrewAI or the OpenAI/Claude Agents SDK?', or 'is this an agent or just a workflow?'. Used by `agentic-systems-architect` (primary)."
---

# Skill: triage-agentic-approach

> **Invoked by:** `agentic-systems-architect` (primary). Also consulted by `agent-implementation-engineer` when a build reveals the task doesn't actually need the agentic machinery it was scoped with and should be re-triaged.
>
> **When to invoke:** "should we build an agent for this?"; "is this an agent or a workflow?"; "do we need multiple agents?"; "single agent with more tools, or a swarm?"; "which agent framework?"; any "how should we approach this agentically?" question.
>
> **Output:** a go/no-go verdict (defaulting to "a workflow or single call wins") + IF an agent survives: single-vs-multi + topology + framework + the cost/latency budget and guardrail level — every volatile framework/model fact dated and marked verify-at-use.

## Procedure

1. **Restate the task in the tree's terms.** Capture: the **goal** (what "done" means), whether the **steps are knowable in advance** (can you flowchart them?), whether the **step count is bounded**, what **tools/systems** it must touch and their **blast radius** (read-only vs writes to the real world), and the **cost/latency tolerance**.
2. **Run the agent-vs-not gate FIRST — this is the whole point.** The decisive question: **is the control flow knowable before runtime?**
   - **Yes, one shot** → a **single LLM call** with the right context (retrieval, examples, structured output). Stop here.
   - **Yes, multiple known steps** → a **workflow** (prompt chaining / routing / parallelization / orchestrator with *fixed* stages). Deterministic, debuggable, cheap. Stop here.
   - **No — the path genuinely varies per input and can't be enumerated** → an **agent** (LLM directs its own tool calls over an unknown number of steps). Only now proceed.
   - Default bias: **not an agent.** "It would be flexible/cool" is not a reason; unpredictable, variable-step tool use is.
3. **If an agent survives, decide single vs multi-agent.** Default to **one agent with a good tool set**. Justify each additional agent with a concrete reason: genuinely **parallel independent subtasks**, context that a **single window can't hold**, or a **hard trust/permission boundary**. No reason → single agent.
4. **Choose the topology (multi-agent only).** Orchestrator-worker / sequential pipeline / parallel fan-out + synthesizer. Name the **shared-state design** and the **failure blast radius**.
5. **Select the framework from the requirements.** Map: loop control, statefulness/checkpointing, streaming, multi-provider, human-in-the-loop, deployment target → LangGraph / OpenAI Agents SDK / CrewAI / AutoGen / Claude Agent SDK / plain SDK loop. Name the **lock-in** and the **escape hatch**; date every version-volatile capability.
6. **Set the budget and guardrail level.** A per-run **token/cost ceiling**, a **step/tool-call cap**, a **latency target**, and a **guardrail tier** sized to blast radius (read-only → light; real-world writes → human-in-the-loop on the irreversible step).

## Output format

- **Verdict:** single call / workflow / agent — with the one-line reason from the gate.
- **If agent:** single vs multi (+ topology), framework (+ lock-in/escape hatch), budget (tokens/steps/latency), guardrail tier.
- **If not an agent:** the concrete cheaper pattern to build instead, and what it would look like.
- **Volatile facts** (framework APIs, model IDs, context windows, pricing): each dated + `[verify-at-use]`.

## Guardrails

- **Default to not-an-agent.** The burden of proof is on the agent, not the workflow.
- **Never recommend multi-agent without a named reason** from step 3.
- **Never assert a framework capability from memory** — this landscape changes monthly; date it or verify it.
