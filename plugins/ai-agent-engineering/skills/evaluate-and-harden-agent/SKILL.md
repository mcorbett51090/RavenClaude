---
name: evaluate-and-harden-agent
description: "Evaluate an agent and harden its failure modes before it touches real traffic — an offline eval harness scored on task-completion, trajectory, and tool-use correctness against a fixed task set, plus loop hardening (step/tool-call caps, timeouts + retries, stop conditions, human-in-the-loop on irreversible actions) and tracing so every step/tool-call/token-cost is observable, with cost and latency reported alongside quality. Reach for this when the user asks 'how do I know this agent works?', 'set up agent evals', or 'the agent loops / does something dangerous'. Used by `agent-implementation-engineer` (primary)."
---

# Skill: evaluate-and-harden-agent

> **Invoked by:** `agent-implementation-engineer` (primary). Also consulted by `agentic-systems-architect` when a go/no-go needs an evidence bar defined before build.
>
> **When to invoke:** "how do I know this agent actually works?"; "set up evals for the agent"; "the agent loops forever / burns tokens"; "the agent did something irreversible it shouldn't have"; "it works in the demo but fails in the tail".
>
> **Output:** an offline agent-eval harness (task-completion + trajectory + tool-use, over a fixed task set) and a hardening plan (caps, timeouts/retries, stop conditions, human-in-the-loop, tracing) — with cost and latency reported next to quality.

## Procedure

1. **Build a fixed task set before scoring anything.** Collect representative tasks with known-good outcomes (start with real or realistic inputs, include the hard/tail cases, not just the happy path). This set is the regression harness — freeze it and grow it as failures surface.
2. **Score three dimensions, not one.**
   - **Task-completion:** did the agent achieve the goal? (the outcome, judged against the known-good result — exact-match, rubric, or LLM-judge as fits.)
   - **Trajectory:** did it take a *sane path*, or flail and get lucky? Check step count, redundant/looping calls, and whether the plan was coherent — a right answer via a 40-step random walk is a latent failure.
   - **Tool-use correctness:** right tools, right arguments, recovered from errors? Wrong-tool and bad-argument rates are the leading indicators of agent quality.
3. **Run it offline against fixtures/mocks first.** Mock the tools/systems so the eval is deterministic, free, and fast — catch regressions before spending on live calls. Only after offline is green do you evaluate against live dependencies.
4. **Report cost and latency alongside quality — always.** Per-task **token cost** and **wall-clock**, plus the distribution (the p95, not just the mean). A correct agent that costs $2 and takes 90s per run may be unshippable; the number needs a price tag.
5. **Harden the loop against its failure modes.**
   - **Caps:** a hard **step/tool-call limit** so a stuck agent stops instead of billing forever.
   - **Timeouts + retries:** per-tool timeout with bounded backoff; a hung tool must not hang the agent.
   - **Stop conditions:** explicit goal-reached / no-progress / cap-hit exits.
   - **Human-in-the-loop:** a confirmation gate on **every irreversible or high-blast action** (send, pay, delete, write-to-prod) — the loop pauses for approval.
   - **Tracing:** every step, tool call, argument, result, and token cost recorded, so any failure is replayable.
6. **Feed production back into the eval set.** Treat early live runs as data — every new failure mode becomes a fixture in the frozen task set, so the agent can't regress on it again.

## Output format

- **Eval harness:** the task set + the three scorers (task-completion / trajectory / tool-use) + offline-fixture setup.
- **Quality + cost/latency report:** per-dimension scores with token-cost and wall-clock (mean + p95).
- **Hardening plan:** caps, timeouts/retries, stop conditions, human-in-the-loop gates, tracing wiring.
- **Volatile facts** (model IDs, pricing, framework tracing APIs): dated + `[verify-at-use]`.

## Guardrails

- **A demo is not an eval** — score the tail on a frozen task set, not the happy path once.
- **A right answer via a bad trajectory is a latent failure** — always score the path, not just the outcome.
- **Never ship an agent with a real-world write and no human gate** on the irreversible step.
- **Never report quality without cost and latency** next to it.
