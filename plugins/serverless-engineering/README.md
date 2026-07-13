# serverless-engineering

> The **provider-neutral serverless PATTERNS layer** for Claude Code — the team that answers *"is serverless the right shape for this workload, and if so, how do we build it so it starts fast, scales within limits, fails safely, and costs what we think?"* Two agents: the **serverless-architect** (event-driven decomposition, serverless-vs-container-vs-managed-service, sync/async, orchestration-vs-choreography, event contracts, the dual-write/outbox problem, serverless-friendly storage) and the **serverless-runtime-and-ops-engineer** (cold starts, concurrency & limits, idempotency, DLQ/poison, retries, per-invocation cost & the scale crossover, tracing, local emulation).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## What it does

| You ask | It returns |
|---|---|
| "Should this be serverless, containers, or a managed service?" | A decision-tree-driven call scoped by throughput profile, latency budget, run duration, and statefulness — with the workload profile where serverless **loses** named, and the flip conditions |
| "Decompose this workflow into functions and events." | An event-driven decomposition (function/event boundaries, sync/async per interaction) designed around events + contracts — **not** a synchronous call graph (no distributed monolith) |
| "State machine or event bus for this multi-step process?" | An orchestration-vs-choreography recommendation driven by whether a visible end-to-end state / rollback (saga) is needed, with the coupling/observability trade-off named |
| "Can our RDBMS sit behind these functions?" | A storage call that respects connection-pool limits under high concurrency (managed/NoSQL vs pooled RDBMS + proxy), plus an outbox/transactional-event fix for dual-write |
| "Our functions are slow on the first hit — fix cold starts." | A cold-start playbook: causes named, the provisioned/warm-concurrency vs package-slimming trade-off modeled against the latency budget, and what **not** to over-provision |
| "This queue double-processes and retries forever — harden it." | Idempotency keys + exactly-once-**effect**, a DLQ + poison-message policy, and retry/visibility-timeout settings — turning an infinite-retry outage risk into a bounded, observable failure path |
| "Is serverless actually cheaper, or do we cross over at scale?" | A per-invocation cost model (invocations × duration × memory + requests + data) with the steady-vs-spiky crossover where always-on containers get cheaper, plus a quota/concurrency headroom check |
| "We're getting throttled under load — plan our concurrency." | A concurrency & quota plan: account/region limits, reserved/provisioned concurrency, throttle-and-retry behavior, and downstream (RDBMS connection) protection |

**Two rules it never breaks:** *every async handler is idempotent* (delivery is at-least-once — exactly-once **effect** via a key + dedup store) and *every queue has a DLQ + poison-message plan* (no DLQ is an infinite-retry outage). And one stance underneath both: *serverless is a trade, not a default* — the workload profile where it loses is named out loud.

## What's inside

- **2 agents** — `serverless-architect` (the design side: decomposition, serverless-vs-not, sync/async, orchestration-vs-choreography, event contracts, dual-write/outbox, serverless-friendly storage) and `serverless-runtime-and-ops-engineer` (the runtime + ops side: cold starts, concurrency & limits, idempotency, DLQ/poison, retries, per-invocation cost & the crossover, tracing, local emulation).
- **3 skills** — `design-event-driven-architecture`, `harden-serverless-runtime`, `model-serverless-cost-and-scale`.
- **2 knowledge files** — a Mermaid serverless decision tree (serverless-vs-container-vs-managed-service, orchestration-vs-choreography, sync/async + idempotency/DLQ gate, cost crossover) and a 2026 serverless-patterns reference (event-driven patterns, the cold-start playbook, idempotency & exactly-once-effect, the per-invocation cost model, anti-patterns; provider numbers kept generic with retrieval dates).
- **2 templates** — a serverless architecture decision record (ADR) and a per-function readiness checklist.

## Where it sits among the platform/cloud plugins

```
aws-cloud / gcp-cloud / azure-cloud  →  provider-specific IaC & service specifics   ("the actual Lambda/Function resource, IAM, VPC, DLQ")
data-streaming-engineering           →  the streaming PLATFORM                       ("Kafka/Kinesis topics, partitions, stream processing")
devops-cicd                          →  the deploy PIPELINE                          ("CI/CD, canary, IaC apply")
backend-engineering                  →  the serverful ALTERNATIVE                    ("long-running services, stateful backends")
observability-sre                    →  tracing / SLOs as a DISCIPLINE               ("the platform + the SLO math")
serverless-engineering (HERE)        →  provider-neutral serverless PATTERNS         ("should this be serverless, and how does the event-driven design + runtime actually work?")
```

This plugin decides the **pattern** and **consumes** those layers rather than replacing them: it names the provider resource `aws-cloud`/`gcp-cloud`/`azure-cloud` wires, the stream `data-streaming-engineering` runs, and the pipeline `devops-cicd` deploys — while owning the provider-neutral serverless work (fit, decomposition, cold start, concurrency, idempotency, DLQ, cost crossover) that none of them cover.

## Domain stance

Provider-neutral and trade-off-first: serverless is a **trade, not a default** — the fit criteria (throughput / latency / duration / statefulness), event-driven decomposition around contracts (never a distributed monolith), orchestration (state machine / saga) vs choreography (event bus), at-least-once delivery → **idempotency + exactly-once-effect**, the **DLQ + poison-message** discipline, the outbox for dual-write, the **cold-start playbook** (slim before you provision), and the **per-invocation cost model + the steady-vs-spiky crossover**. Fluent across the FaaS platforms as options, not defaults — and every provider concurrency cap, timeout, limit, or price is treated as **volatile**, kept generic with a retrieval date, and re-verified before a commitment.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install serverless-engineering@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
