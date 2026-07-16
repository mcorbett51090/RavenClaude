# AI Agent Patterns (2026)

> **Retrieval date:** 2026-07-16. Model IDs, context-window sizes, tool-call formats, framework APIs, and pricing all move monthly — every such fact below is `[verify-at-use]`. This doc is engineering judgment about *patterns*, which age slowly; the *specifics* age fast.

## The core invariant

**An agent is an LLM in a loop with tools.** The LLM is the unreliable component: it will call tools with wrong arguments, hallucinate values, loop without progress, and drift from the goal on long runs. Good agent engineering is not about a smarter prompt — it is about **containing that unreliability** with structure, caps, and observation. Every pattern below serves that end.

## The minimal loop

```
state = init(task)
for step in range(MAX_STEPS):          # a hard cap is not optional
    plan = model(state)                # what to do next (may be a tool call)
    if plan.is_final: return plan.answer
    if plan.tool.irreversible:         # send / pay / delete / write-prod
        await human_confirm(plan)      # human-in-the-loop gate
    result = run_tool(plan.tool,       # with timeout + bounded retry
                      timeout=T, retries=R)
    state = update(state, result)      # summarize/compact to fit the budget
    trace(step, plan, result, tokens)  # observe everything
raise StepCapExceeded                  # terminate, don't bill forever
```

Everything hard about agents is in the details of that loop, not its shape.

## Tool design — the agent's interface to the world

- **Tool schema is prompt engineering with a type system.** Ambiguous names and unhelpful errors cause more failures than a weak model.
- **Keep the tool count small.** Too many tools is the most common cause of wrong selection. If the model confuses two tools, merge or disambiguate them.
- **Errors must teach recovery.** `"start_date must be YYYY-MM-DD, got '3rd'"` lets the model self-correct next iteration; `"invalid input"` wastes the iteration.
- **Return summaries or IDs, not raw blobs.** A large tool result dumped into context is a top cause of overflow and drift — return a summary + a handle to fetch detail on demand.
- **Bound each tool's blast radius.** Read-only tools are cheap to trust; write tools get a confirmation gate.

## Context & memory — the window is a budget

- **Decide per turn** what stays in-window (current task, recent results, running plan), what gets **summarized/compacted** (old turns, long outputs), and what moves to **external memory/retrieval**.
- **Two memory tiers:** short-term scratchpad (working state for the current task) vs long-term store (facts queried across runs). Add long-term memory only when cross-run recall is genuinely required.
- **The failure modes are symmetric:** dump-everything → overflow and drift; summarize-too-hard → lose the thread. Tune the balance and set a per-turn token budget.

## Planning & reflection

- **Plan-then-act** (draw a plan, then execute steps) and **ReAct-style interleaving** (reason → act → observe) both work; the win is making the plan *explicit* so it's inspectable and correctable.
- **Reflection/self-critique** (the agent reviews its own output before finalizing) improves quality on open-ended tasks but costs tokens and latency — apply it where the task warrants, not everywhere.
- **More steps is not more capability.** A right answer via a 40-step random walk is a latent failure; a coherent 4-step trajectory is the goal.

## Multi-agent — use sparingly

- Coordinate through an **explicit shared state**, not implicit assumption. Each agent should know what it can see of the others' work.
- **Error compounds** down a pipeline and **work duplicates** in fan-out — the synthesizer and the dedup logic are where multi-agent quality is won or lost.
- The coordination overhead is real: multi-agent multiplies token spend and failure surface. Justify every agent.

## Guardrails & safety

- **Human-in-the-loop on every irreversible/high-blast action** (send, pay, delete, write-to-prod). Read-only agents need little; write-capable agents need a gate on the write.
- **Tool allowlists** and **input/output validation** bound what the loop can do even when the model misbehaves.
- **Prompt injection is a live threat** for agents that read untrusted content (web pages, emails, documents): untrusted text can try to hijack the agent's tool use. Treat retrieved/tool-returned content as data, not instructions; keep the high-blast tools behind a human gate so a hijack can't act unsupervised.

## Evaluation — a demo is not a result

- **Score three dimensions:** task-completion (goal achieved?), trajectory (sane path?), tool-use (right tools, right args, recovered from errors?).
- **Offline against fixtures first.** Mock the tools so the eval is deterministic, free, and fast; catch regressions before spending on live calls.
- **Report cost and latency (mean + p95) next to quality.** A correct agent that's too slow or too expensive is not shippable.
- **Freeze a task set and grow it from production failures** — every new failure mode becomes a permanent regression fixture.

## Cost & latency

- Agentic loops silently multiply token spend and wall-clock vs a single call. Cap steps, use cheaper models for sub-steps where quality allows, and parallelize independent tool calls when it's safe.
- Instrument token cost per step from run one — you cannot optimize what you don't measure.

## Framework landscape (patterns, not endorsements — `[verify-at-use]`)

- **LangGraph** — explicit state-graph control, checkpointing; leans toward teams that want to own the loop's structure.
- **OpenAI Agents SDK / Claude Agent SDK** — provider-native agent loops with hosted tool-use; lighter to start, provider-shaped.
- **CrewAI / AutoGen** — role-based multi-agent collaboration out of the box; convenient for multi-role, heavier abstraction.
- **Plain SDK loop** — ~50 lines, zero lock-in, full control; the baseline every framework should be measured against.

Whatever you pick, know what the plain loop would look like — that's how you tell what the framework buys you and what it costs you.
