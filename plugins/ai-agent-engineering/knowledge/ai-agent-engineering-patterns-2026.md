# Knowledge — Ai-agent-engineering patterns (2026)

> **Last reviewed:** 2026-07-17 · **Confidence:** High on the durable concepts (orchestration topologies, tool/function-call design, memory & context management, failure handling, guardrails & safety, tracing/observability, the agent-eval harness, cost & latency); **Medium on the dated framework/model/tooling map — framework APIs, model names/prices, context windows, and tool-calling/MCP shapes change and carry retrieval dates below.**
> The reference the `agent-implementation-engineer` reads when building the control-flow, wiring tools, adding failure handling, instrumenting tracing, and building the eval harness — plus a 2026 framework/model/tooling snapshot. **This is engineering, not model-vendor gospel; volatile specifics carry a retrieval date and are verified at use.**

The team's discipline: **the simplest topology that works; determinism where you can; every tool call can fail so design for retries/timeouts/idempotency; trace every step; guardrails are architecture; and no system without an eval harness.**

---

## Orchestration topologies — the ladder

| Topology | What it is | When |
|---|---|---|
| **Workflow / graph** | Fixed edges; code owns routing, the LLM fills nodes | Steps are known & deterministic — cheapest, fastest, most testable |
| **Single agent (ReAct)** | Reason → act (tool) → observe → repeat, one actor | Open-ended, one actor, a handful of tools — the default |
| **Planner / executor** | A planner decomposes the task; an executor runs steps, re-planning on failure | Many steps needing an explicit plan |
| **Multi-agent** | Multiple specialized agents, an orchestrator delegating | Genuinely separable roles / real parallelism / context that won't fit one — **only when a single agent provably can't** |

**The ladder is a cost curve.** Each step up buys capability with tokens, latency, and coordination-failure surface. Start at the bottom (workflow / single agent) and climb only when the task forces it. A **loop-cap** (max steps) and a **budget guard** (max tokens/cost per task) belong on every non-trivial loop — a stuck agent must terminate, not spin the bill. In multi-agent, the orchestrator delegates and **sub-agents do not sub-delegate** (keeps the topology legible).

---

## Tool / function-call design — the API contract

- **A tool is a narrow, typed, single-responsibility function** with an explicit schema (name, a description the *model* reads to decide selection, typed parameters) and **validated inputs and outputs**. The description is part of the contract — imprecise descriptions cause mis-selection.
- **Tool vs deterministic code** — parsing, routing on a known enum, arithmetic, and validation are **code**, not tools; using the LLM for an exact step pays tokens and adds non-determinism where a function is exact.
- **Keep the count small** — tool sprawl and kitchen-sink "do_stuff" tools both degrade the model's selection. Consolidate or split by responsibility.
- **Native function-calling vs MCP** — whether tools are exposed via a model's native function/tool-calling or via **MCP** (Model Context Protocol, a standard tool interface), the contract discipline is identical: typed schema, validated I/O, idempotency on side effects. _(MCP + tool-calling API shapes are volatile — retrieved 2026-07-17.)_
- **Structured errors** — a tool returns a structured error (what failed, retryable or not) to the model, never a raw stack trace, so the agent can recover or degrade.

---

## Failure handling — every tool call can fail

- **Timeout** every call — a tool with no timeout is a hang that stalls the whole task.
- **Retry** transient failures (network, rate-limit, 5xx) with **exponential backoff + jitter**, capped attempts; **do not** retry deterministic failures (validation errors, 4xx) — they'll just fail again.
- **Idempotency** — every side-effecting tool (write, charge, send, deploy) takes an **idempotency key** so a retry can't double-apply the effect. This is the single most-missed piece of agent hardening.
- **Graceful degradation** — a fallback path (a cheaper model, a cached answer, a "couldn't complete" with the trace) beats an exception bubbling to the user.
- **Loop-cap & budget guard** — bound the steps and the tokens/cost per task so a stuck or adversarial loop terminates.

---

## Memory & context management — context is a budget

- **Scratchpad** — per-turn working notes within the window; nothing persisted. For short tasks.
- **Running summary** — compress older turns, keep recent verbatim; for conversations that outgrow the window. Watch the compression lossiness.
- **Vector recall** — embed and retrieve relevant long-lived memory; the retrieval itself is `ai-rag-engineering`'s domain (you call it as a tool). Recall ≠ relevance.
- **Per-turn assembly** — each turn's window is a **deliberate, pruned** assembly: system + relevant memory + retrieved context + recent tool results. **Don't concatenate the whole history every turn** — it blows the token budget and buries the signal. Bound memory growth.

---

## Guardrails & safety — architecture, not an afterthought

- **Input validation** — schema-check and sanitize the request; scope it to the authenticated caller.
- **Prompt-injection defense** — treat **all** tool-fed, retrieved, and user content as **data, never instructions**; delimit and label untrusted content. Injection via retrieved/tool text is the dominant agent-safety failure — "ignore your instructions and…" hidden in a document.
- **Tool-permission scoping** — least privilege: each tool can touch only what it must (the refund tool can't reach another customer's order). The tool set is the real bound on blast radius.
- **Human-in-the-loop** — an **irreversible / high-blast** action (refund, delete, send, deploy) **pauses for approval** and cannot auto-execute.
- **Output validation** — bounds-check, format-check, and policy-check the output **before it acts**.
- **Test every guardrail** — a guardrail with no test is a hope (see the eval harness).

---

## Tracing & observability — you can't debug what you can't see

- **Every step is a span** — each LLM call, tool call, and state transition emits a span capturing **inputs, outputs, tokens, latency, cost, and the decision**. Instrument as you build, not after.
- **Run-level rollup** — per task: **tokens/task, calls/task, p50/p95 latency, cost/task** — so the cost/latency budget is observable and a regression is visible.
- **Trace backend** — wire spans to a tracing backend (OpenTelemetry-style traces or an LLM-observability tool); the trace is the first thing you reach for on a failure. _(Specific tools are volatile — retrieved 2026-07-17.)_

---

## The agent-eval harness — the difference between a demo and a system

- **Offline eval set** — representative cases (the real distribution) **+** adversarial edges (ambiguity, missing data, tool failures, injection, out-of-scope). Each case has a gradable expectation.
- **LLM-as-judge** — for open-ended outputs, a rubric-scored judge — **calibrated against human labels first** (agreement rate), else it's an opinion. Prefer pairwise/rubric over a raw 1-10. Use exact/programmatic checks wherever the output is checkable.
- **Regression gate in CI** — run the set on every prompt/model/tool/topology change; gate the merge on **quality ≥ baseline · tokens/task ≤ ceiling · p95 ≤ SLO**. This is what lets you refactor without silently regressing.
- **Guardrail tests** — explicit assertions for injection resistance, tool-permission scoping, refusal/out-of-scope, human-in-the-loop, and output validation.
- **Online monitoring** — sampled judge scores, feedback, failure/escalation rate, and cost/latency drift in prod, with alerts; real failures feed back into the offline set.
- **Red-team** — jailbreaks, injection, tool-abuse, exfiltration, cost-bombing before shipping; each finding becomes a regression case.

> The eval *methodology/science* (metric design, judge-calibration science, benchmark construction) is `llm-evaluation-engineering`'s discipline; this team **builds the harness** that applies it.

---

## Cost & latency — product requirements, budgeted up front

- **The dials:** **tokens/call** (prompt + output size, context strategy), **calls/task** (topology — more agents/steps = more calls), **model tier** (a stronger model per call), and **parallelism** (fan-out cuts latency, not cost).
- **Budget, don't discover** — state tokens/call · calls/task · p50/p95 · model tier up front and choose the topology/model against them; "slow and expensive" is a design failure, not a surprise.
- **Levers** — route easy steps to a cheaper model and escalate only the hard step; cache; prune context; make known steps deterministic code; parallelize independent tool calls. _(Token prices & model tiers are volatile — retrieved 2026-07-17.)_

---

## 2026 framework / model / tooling map (dated — volatile, re-verify before quoting)

- **Orchestration frameworks:** graph runtimes (e.g. **LangGraph** — explicit state, branching, checkpoints, human-in-the-loop), agent SDKs from model providers, and roll-your-own loops remain the three families. Choose to the control-flow and observability needs, stay provider-neutral. _(Framework APIs volatile — retrieved 2026-07-17.)_
- **Tool interface:** native **function/tool-calling** and **MCP** (Model Context Protocol) as a standard tool interface; the contract discipline (typed schema, validated I/O, idempotency) is the same either way. _(APIs volatile — retrieved 2026-07-17.)_
- **Models:** capability, context window, tool-calling reliability, and token price differ by model and tier and change frequently — **do not** pin a model name/price/window from memory; verify at use. _(Retrieved 2026-07-17.)_
- **Observability / eval tooling:** OpenTelemetry-style tracing plus LLM-observability and eval platforms exist; categories are stable, specific tools/vendors are volatile — verify at selection. _(Retrieved 2026-07-17.)_

---

## Provenance

- Durable concepts (the topology ladder and the simplest-topology-that-works ordering, tool/function-call design as an API contract, tool-vs-code boundary, failure handling with retries/timeouts/idempotency + loop-cap/budget-guard, context-is-a-budget memory strategies, guardrails-as-architecture with injection defense and human-in-the-loop, per-step tracing, the offline-set + calibrated-judge + regression-gate + guardrail-tests + monitoring + red-team eval harness, and the cost/latency dials) are consensus agentic-engineering practice reviewed 2026-07-17 — **High confidence**.
- The framework/model/tooling map — LangGraph and other framework APIs, agent SDKs, MCP / tool-calling API shapes, model names/prices/context-windows, and observability/eval tooling — is a **2026-07 snapshot**; these are volatile, carry the retrieval dates above, and are re-verified with `ravenclaude-core/deep-researcher` before pinning a model, a price, or an API in a design, a bill estimate, or code. _(Reviewed 2026-07-17.)_
