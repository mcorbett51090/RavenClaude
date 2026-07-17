# Agent architecture design doc — <agent / system name>

> The design artifact captured when setting an agent's architecture. Pairs with
> [`agent-eval-and-guardrail-plan.md`](agent-eval-and-guardrail-plan.md) (the eval & guardrail side of the same agent).
> **Volatile substrate.** Model names, token prices, context windows, and framework/tool-calling APIs carry a retrieval date — verify at use before pinning.

**Owner:** <name> · **Date:** <YYYY-MM-DD> · **Status:** draft / approved · **Review cadence:** <per topology/model change>

## 1. Task scope (scope before you name a shape)
- **What the agent does:** <one-paragraph task>
- **Determinism of steps:** <known sequence / open-ended>
- **Step count & parallelism:** <few / many · any real parallelism?>
- **Error tolerance & blast radius:** <can a wrong action be undone? worst-case action?>
- **Latency SLO:** <p50 / p95 target>
- **Cost ceiling:** <$ or tokens per task>

## 2. Topology (the simplest that works)
- **Chosen topology:** <single-agent/ReAct · planner-executor · multi-agent · workflow/graph>
- **Why this shape:** <the scope facts that drive it>
- **Why NOT the simpler shape:** <what forces the step up the ladder>
- **Why NOT the more complex shape:** <why not multi-agent, if not>

## 3. Framework / runtime (provider-neutral)
- **Chosen runtime:** <roll-your-own · graph runtime (e.g. LangGraph) · agent SDK>
- **Why:** <control-flow / state / checkpoints / human-in-the-loop / observability needs>
- **Volatile:** <framework API — retrieved <date>>

## 4. Tool catalog & contracts
| Tool | Responsibility | Read / side-effecting | Schema (params → return) | Idempotency | Permission scope | Timeout / retry |
|---|---|---|---|---|---|---|
| <lookup_x> | <one thing> | read | <(id: str) → X> | n/a | <scoped to caller> | <10s / 3x backoff> |
| <do_y> | <one thing> | side-effecting | <(…, idempotency_key) → Y> | <key required> | <least privilege> | <10s / retry w/ key> |
- **What stays deterministic code (not a tool):** <parsing / routing / arithmetic / validation>
- **Tool count sane for selection?** <yes — N tools · no → consolidate/split>

## 5. Memory / context / state
- **Memory strategy:** <scratchpad · running-summary · vector recall (retrieval → ai-rag-engineering)>
- **Per-turn context assembly (pruned to window):** <system + relevant memory + retrieved context + recent tool results>
- **Growth bound:** <how memory is kept bounded>

## 6. Guardrails (designed in, up front)
- **Input validation:** <schema-check · scope to authenticated caller>
- **Prompt-injection defense:** <tool/retrieved text = data, not instructions · delimited/labelled>
- **Tool-permission scoping:** <least privilege per tool>
- **Human-in-the-loop:** <which irreversible/high-blast actions pause for approval>
- **Output validation:** <bounds / format / policy check before it acts>

## 7. Cost / latency budget
- **Tokens/call:** <target> · **Calls/task:** <target> · **p50 / p95 latency:** <target>
- **Model tier:** <default model · escalation step → stronger model>
- **Levers if over budget:** <cheaper-model routing · cache · prune context · deterministic steps · parallelize>

## 8. Failure modes
| Failure | Detection | Handling |
|---|---|---|
| <tool timeout> | <span latency> | <timeout + retry / degrade> |
| <runaway loop> | <loop-cap> | <max-steps terminate + trace> |
| <injection via tool text> | <guardrail test> | <treat as data / reject> |

## 9. Flip conditions (what would change the topology/strategy)
- <e.g. task gains 3 separable roles with parallel work → multi-agent earns its cost>
- <e.g. steps become fully known → drop to a workflow>
- <e.g. tool latency dominates → parallelize the fan-out>

## Seams (not this team)
- **Retrieval / RAG (the index):** ai-rag-engineering
- **The prompt / context text craft:** prompt-engineering
- **The eval methodology / science:** llm-evaluation-engineering
- **Deploy / scale / on-call:** observability-sre
- **The surrounding service (APIs/queues/datastores):** backend-engineering

## Open questions / risks
- <list>

**Sign-off:** <tech lead / staff eng> · <date> · *Volatile model/framework/pricing specifics verified at use (<retrieval date>).*
