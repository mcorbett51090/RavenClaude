# Agent System Design Doc — <system name>

> Fill this out with the `agentic-systems-architect` **before** building. If §1 concludes "not an agent," stop here and build the workflow/single-call instead — that is a successful outcome, not a failure.

## 1. Triage — does this even need an agent?

- **Goal (what "done" means):**
- **Is the control flow knowable in advance?** (can you flowchart it?) → yes/no
- **Verdict:** single call / workflow / **agent** — one-line reason from the gate.
- **If not an agent:** describe the cheaper pattern to build instead, then stop.

## 2. Topology (agents only)

- **Single-agent or multi-agent?** (default single) — if multi, the named reason:
- **Topology:** single-with-tools / orchestrator-worker / sequential pipeline / parallel fan-out + synthesizer
- **Shared-state design:**
- **Failure blast radius:**

## 3. Tools / capabilities

| Tool | Purpose | Params (typed) | Read/Write | Blast radius |
|---|---|---|---|---|
|  |  |  |  |  |

- **Tool count:** — (kept small enough for reliable selection?)

## 4. Context & memory

- **In-window each turn:**
- **Summarized/compacted:**
- **External memory/retrieval:**
- **Short-term scratchpad shape:**
- **Long-term store (if any) — write/read/staleness rules:**
- **Per-turn token budget:**

## 5. Framework & deployment

- **Framework:** (LangGraph / OpenAI Agents SDK / CrewAI / AutoGen / Claude Agent SDK / plain loop)
- **Why (requirements → framework):**
- **Lock-in / escape hatch:**
- **Deployment target:**
- **Volatile facts (dated + [verify-at-use]):**

## 6. Budget & guardrails

- **Per-run token/cost ceiling:**
- **Step / tool-call cap:**
- **Latency target (mean / p95):**
- **Guardrail tier:** read-only / write-with-human-gate
- **Human-in-the-loop checkpoints (irreversible actions):**
- **Tool allowlist / input-output validation:**

## 7. Success criteria & eval bar

- **What must the eval harness prove before this ships?** (task-completion / trajectory / tool-use thresholds; cost & latency ceilings)
