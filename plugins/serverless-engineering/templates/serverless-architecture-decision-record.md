# Serverless architecture decision record — <workload / service name>

> An ADR for a serverless / event-driven design. Order matters:
> **workload profile → serverless-vs-not → decomposition → orchestration model → event contracts → failure & idempotency → cost → flip conditions.**
> Serverless is a **trade, not a default** — name the profile where it wins and where it would lose.
> Pairs with [`serverless-function-readiness-checklist.md`](serverless-function-readiness-checklist.md) (per-function hardening).

**Owner:** <architect> · **Date:** <YYYY-MM-DD> · **Status:** proposed / accepted / superseded · **Decision-tree ref:** [`../knowledge/serverless-engineering-decision-tree.md`](../knowledge/serverless-engineering-decision-tree.md)

## 1. Workload profile
- **Throughput:** <steady high-throughput | spiky/bursty | low-volume — and the shape (peaks/troughs)>
- **Latency budget:** <does the tail matter? target p50/p99 · sync or tolerant?>
- **Run duration per unit of work:** <ms · seconds · minutes+ (long-running?)>
- **Statefulness:** <stateless | session/stateful | streaming>
- **Data model:** <managed/NoSQL | connection-pooled RDBMS | object store>

## 2. Serverless-vs-not decision (Tree A)
- **Choice:** serverless functions | container/serverful | managed service
- **Why (decision-tree leaf):** <duration/throughput/latency/statefulness → leaf>
- **Where serverless would LOSE here:** <the profile that would flip it — steady-high / long-running / tight-tail / pooled-RDBMS — stated even if we chose serverless>
- **Cost basis:** <summary from model-serverless-cost-and-scale — spiky→serverless / steady→crossover>

## 3. Decomposition (functions & events)
- **Functions/components:** <list · one responsibility each>
- **Events:** <the events emitted/consumed · the boundaries>
- **Sync vs async per interaction (Tree C):** <which caller waits (sync, pays cold-start tail) · which is async through a queue/bus>
- **Distributed-monolith check:** <confirm coupling lives in events/contracts, NOT a sync function-to-function call graph>

## 4. Orchestration model (Tree B)
- **Model:** orchestration (state machine / workflow / saga) | choreography (event bus / pub-sub)
- **Why:** <need visible end-to-end state + compensation/rollback → orchestration; loose fan-out → choreography>
- **Trade-off named:** <coupling to orchestrator vs no single view of the flow>

## 5. Event contracts
| Event | Producer | Consumers | Schema / key fields | Versioning stance |
|---|---|---|---|---|
| <OrderPlaced> | <api> | <charge, inventory> | <schema ref> | <additive / registry> |

## 6. Storage & consistency
- **Store choice:** <managed/NoSQL | RDBMS + connection proxy | object store> · **why vs connection-pool limits**
- **Dual-write strategy:** <outbox / transactional event — never two independent writes>
- **Consistency model:** <strong | eventual — and where>

## 7. Failure & idempotency strategy
- **Async handlers requiring idempotency:** <list · idempotency key · dedup store>
- **DLQ + poison plan:** <max-receive · dead-letter target · owner · replay path>
- **Retry/visibility:** <bounded retry + backoff · visibility timeout ≥ handler duration>
- **Cold-start posture:** <budget · slim/init · provisioned floor IF the tail demands — detail in the readiness checklist>

## 8. Cost estimate
- **Per-invocation model:** <invocations × duration × memory + requests + data + downstream (+ provisioned floor)>
- **Regime:** <spiky → serverless wins | steady-high → past crossover, container cheaper>
- **Crossover point:** <the throughput/utilization where the shape flips>

## 9. Flip conditions
- <The 1-2 facts that would change this decision — traffic 10×'s and goes steady · latency budget tightens · run duration grows · volume makes the cost crossover flip.>

## Seams (not this ADR)
- **Provider-specific IaC & service config:** aws-cloud / gcp-cloud / azure-cloud
- **The streaming platform (Kafka/Kinesis):** data-streaming-engineering
- **The serverful alternative:** backend-engineering
- **The deploy pipeline:** devops-cicd
- **Tracing / SLOs:** observability-sre

**Sign-off:** <reviewer> · <date>
