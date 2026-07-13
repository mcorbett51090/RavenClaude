---
name: design-event-driven-architecture
description: "Decompose a workload into functions and events for a serverless/event-driven design — the serverless-vs-container-vs-managed-service call (and where serverless is the WRONG choice: steady high-throughput, long-running, tight-latency, pooled-RDBMS), sync-vs-async boundaries per interaction, orchestration (state machine/saga) vs choreography (event bus), the event schemas & contracts, serverless-friendly storage vs a connection-pool-hostile RDBMS, and the dual-write/outbox fix — designed around events and contracts so it never becomes a distributed monolith (lambda pinball). Reach for this on 'serverless vs containers vs managed service?', 'decompose this into functions/events', 'state machine vs event bus?', or 'can our RDBMS sit behind these functions?'. Driven by `serverless-architect` (primary)."
---

# Skill: design-event-driven-architecture

> **Invoked by:** `serverless-architect` (primary). Also consulted by `serverless-runtime-and-ops-engineer` for the decomposition/contract context that sets the idempotency and failure requirements.
>
> **When to invoke:** "Should this be serverless, containers, or a managed service?"; "decompose this workflow into functions and events"; "orchestration or choreography — state machine or event bus?"; "sync or async here?"; "can our RDBMS sit behind these functions?"; any move on the event-driven design.
>
> **Output:** a serverless-vs-not call + an event-driven decomposition (function/event boundaries, sync/async, orchestration/choreography) + event contracts + a storage & dual-write strategy, each with the trade-off named and the flip conditions stated — captured in the architecture decision record.

## Procedure

1. **Frame the workload and the goal.** Throughput profile (steady vs spiky/bursty), latency budget (tail matters), run duration (ms/seconds vs minutes+), statefulness, data model, and team capacity. This sets what shape the workload can even take.
2. **Make the serverless-vs-container-vs-managed-service call** via [`../../knowledge/serverless-engineering-decision-tree.md`](../../knowledge/serverless-engineering-decision-tree.md) Tree A: spiky/bursty + short + stateless + event-triggered → **serverless functions**; steady high-throughput or long-running or tight-tail-latency → **containers/serverful** (serverless *loses* here — say so); "does a managed service already do this?" (queue, stream, workflow, auth) → **managed service, no function at all**. Name the workload profile where serverless would lose; consult [`model-serverless-cost-and-scale`](../model-serverless-cost-and-scale/SKILL.md) for the cost crossover.
3. **Decompose around events, not a call graph.** Draw function/event boundaries so coupling lives in *events with schemas*, not synchronous function-to-function calls. If the design is functions calling functions calling functions, you've drawn a **distributed monolith (lambda pinball)** — redraw it around an event bus or a workflow.
4. **Make the sync-vs-async call per interaction** via Tree C: a caller that must wait for a result → **sync** (and it pays the cold-start tax on the tail — flag it for the runtime engineer); fire-and-forget, fan-out, long work, or buffering a spike → **async** through a queue/bus. **Every async path is idempotent** — record that as a hard constraint for `harden-serverless-runtime`.
5. **Choose orchestration vs choreography** via Tree B: need a visible end-to-end state, compensation/rollback, or a saga across steps? → **orchestration** (state machine/workflow) — one place owns the flow, easier to observe, more coupling to the orchestrator. Loose fan-out, independent reactions, low coupling? → **choreography** (event bus) — services react to events, harder to trace end-to-end. Name the observability/coupling trade-off.
6. **Define the event contracts.** Each event gets a schema, an owner, and a versioning/compatibility stance (additive/back-compatible changes; a schema registry or documented contract). Events are your API now — treat them like one.
7. **Choose serverless-friendly storage and kill dual-write.** A function scaling to thousands of concurrent invocations in front of a connection-pooled RDBMS is a connection storm → prefer managed/serverless stores (NoSQL, HTTP-API'd) or a connection proxy/pooler, and name the trade-off. Where a step must write state *and* emit an event, use an **outbox / transactional event** — never two independent writes (that's the dual-write bug). Capture the design in [`../../templates/serverless-architecture-decision-record.md`](../../templates/serverless-architecture-decision-record.md).
8. **State the seams and flip conditions.** Provider IaC → `aws-cloud`/`gcp-cloud`/`azure-cloud`; the streaming platform → `data-streaming-engineering`; the serverful alternative → `backend-engineering`; runtime/ops hardening → `serverless-runtime-and-ops-engineer`. Name the 1-2 facts (traffic goes steady and 10×'s, latency budget tightens, run duration grows) that would flip the shape.

## Worked example

> User: "We're building order processing: an API takes an order, we charge payment, reserve inventory, and email the customer. Someone said 'just make it all Lambdas.' Traffic is spiky — big at lunch and dinner, near-zero overnight. We have a Postgres DB. How should this actually be shaped?"

- **Workload profile:** spiky/bursty (lunch/dinner peaks, near-zero overnight), short steps, event-shaped, existing Postgres. Spiky + short + event-driven → serverless *fits the runtime* (Tree A) — you don't pay for the idle overnight.
- **Don't make it "all Lambdas" calling each other** — charge → reserve → email as a synchronous Lambda chain is **lambda pinball** (a distributed monolith): one slow step blocks the caller, one failure orphans state.
- **Decompose around events + a workflow.** The `POST /order` API is **sync** (the caller waits for an accept/reject) and should be fast — validate + persist + emit `OrderPlaced`, return. The rest (charge, reserve, email) is **async**.
- **Orchestration, not choreography, here** (Tree B): payment→inventory→email needs a **visible end-to-end state and compensation** (refund if inventory fails after charge) → a **state machine / saga**, not a loose event fan-out. You need to see where an order is and roll back cleanly.
- **Idempotency is mandatory** on charge and reserve (at-least-once delivery would double-charge) → hard constraint handed to `harden-serverless-runtime`.
- **Storage:** Postgres behind thousands of concurrent invocations at peak is a connection storm → put a **connection proxy/pooler** in front, or move hot paths to a managed store; and the `persist order + emit OrderPlaced` step uses an **outbox** so the DB write and the event can't drift.
- **Seams:** the actual Step Functions/Workflow + Postgres proxy IaC → `aws-cloud`/`gcp-cloud`/`azure-cloud`; cost model at peak → `model-serverless-cost-and-scale`.
- **Flip condition:** if order volume becomes steady-high 24/7, re-run Tree A — the always-on container crossover may beat per-invocation pricing.

## Guardrails

- Never reflex "serverless-first" or "just make it all Lambdas" — traverse Tree A and **name the workload profile where serverless loses** (steady high-throughput, long-running, tight-tail-latency, pooled-RDBMS).
- Design around **events and contracts**, never a synchronous function-to-function call graph — the distributed monolith / lambda pinball is the failure mode you exist to prevent.
- **Every async handler is idempotent** — record it as a hard constraint for the runtime engineer; a design that assumes exactly-once delivery is wrong.
- Orchestration vs choreography is a **deliberate** call (visible-state/rollback → orchestration; loose fan-out → choreography) — name the observability/coupling trade-off, don't default.
- **Dual-write is a bug** — a step that writes state and emits an event uses an outbox/transactional event, never two independent writes.
- Don't put a **connection-pool-hungry RDBMS** behind a function that scales to thousands of concurrent invocations without a proxy/pooler or a store swap — the connection storm is predictable.
- Keep provider claims **generic** (concurrency caps, timeouts, prices are volatile) — route exact numbers to `ravenclaude-core/deep-researcher`. See [`../../knowledge/serverless-engineering-patterns-2026.md`](../../knowledge/serverless-engineering-patterns-2026.md).
