# Knowledge — Serverless engineering patterns (2026)

> **Last reviewed:** 2026-07-13 · **Confidence:** High on the durable concepts (event-driven patterns, the cold-start playbook, idempotency & exactly-once-effect, the DLQ/poison discipline, the per-invocation cost model, and the anti-patterns); **Medium on any provider-specific quantity — concurrency caps, timeouts, package-size limits, memory ranges, and per-invocation prices are volatile, provider-specific, and are deliberately kept generic below; every such claim carries a retrieval date and routes to research before it's pinned.**
> The reference the two agents read when designing and hardening serverless workloads: the event-driven patterns, the cold-start playbook, idempotency & exactly-once-effect, the cost model, and the anti-patterns to design around.

The team's discipline: **serverless is a trade, not a default; design around events and contracts, not a sync call graph; every async handler is idempotent with a DLQ; cold start and cost are design parameters, not surprises; keep every provider number generic with a retrieval date.**

---

## Event-driven patterns

The vocabulary the architect decomposes with. Each solves a specific failure of naive function-to-function calls.

| Pattern | What it is | When to reach for it |
|---|---|---|
| **Fan-out / fan-in** | One event triggers many parallel handlers (fan-out); results aggregate (fan-in) | Parallelizable work — image variants, per-record processing, scatter-gather |
| **Saga** | A long-lived transaction as a sequence of local steps, each with a **compensation** (undo) | Distributed transactions with no 2-phase commit — order → charge → reserve → ship, refund on failure |
| **Outbox / transactional event** | Write the state change **and** the outbound event in **one local transaction** (to an outbox table), then relay the event | The **dual-write** fix — a DB write and an event emit that must not drift under partial failure |
| **Claim-check** | Store a large payload in object storage, pass only a **reference** through the bus | Payloads larger than the bus/message size limit; keeping the event small |
| **Event-carried state transfer** | The event carries the state a consumer needs, so it doesn't call back to the source | Reducing synchronous coupling / callbacks; consumer autonomy (at the cost of larger events + eventual consistency) |
| **Event sourcing** (heavier) | Persist the sequence of state-changing events as the source of truth | Full audit history, temporal queries, rebuildable state — adopt deliberately, it's a big commitment |

> **The design rule:** coupling should live in **events with schemas**, not in a synchronous call graph. When you find functions calling functions calling functions, you've built a **distributed monolith** — redraw around a bus (choreography) or a workflow (orchestration).

---

## The cold-start playbook

A cold start is the latency of a runtime being initialized before it can serve — a **design parameter you budget**, not a surprise.

**Causes (roughly in order of impact):**
1. **Init / bootstrap code** — work done at module load / outside the handler (SDK clients, config fetch, large imports). The biggest lever you control.
2. **Package / dependency size** — a bigger artifact takes longer to fetch and initialize; trim dependencies and dead code.
3. **VPC / network attach** — attaching to a private network can add setup latency (provider-specific; historically an ENI cost — _re-verify current behavior, retrieved 2026-07-13_).
4. **Language runtime** — interpreted/JIT runtimes and heavy frameworks generally start slower than lean/compiled ones (generic tendency, not an absolute — measure yours).
5. **Memory/CPU allocation** — more memory often means more CPU and faster init (provider-dependent) — rightsizing can *reduce* cold start, not just cost.

**The fix ladder (cheapest first):**
1. **Slim the package + defer init** — lazy-load SDK clients, drop unused deps, move work out of the module top-level. Do this first; it's free and often enough.
2. **Rightsize memory** — sometimes more memory = faster init and *lower* total cost.
3. **Provisioned / warm concurrency** — keep a floor of pre-initialized instances **only when the tail latency budget demands it**. It's an **always-on cost** — over-provisioning erases the serverless savings. Cap it to the measured floor.
4. **Reconsider the shape** — if you can't meet the tail after all of the above, the workload may belong in an always-on container (Tree A).

> **The trap:** reaching for provisioned concurrency first. Slim + measure first; provision only the floor the SLO needs.

---

## Idempotency & exactly-once-effect

The single most important runtime property of an async handler.

- **Delivery is at-least-once.** Queues, streams, and event buses can and will redeliver — network partitions, visibility-timeout expiry, retries. "Exactly-once delivery" is largely a myth in distributed systems.
- **Design for exactly-once *effect*.** A redelivered message must produce **no additional side effect** — a no-op. That is the achievable, correct goal.
- **The mechanism:** an **idempotency key** (message id, a business key like order-id, or a client-supplied token) + a **dedup store** (a record of processed keys with a TTL). On each invocation: check the key → if seen, no-op; if new, do the work and record the key (ideally in the same transaction as the effect).
- **Visibility timeout ≥ handler max duration** — otherwise the message becomes visible again and redelivers **mid-processing**, which itself causes double-processing.
- **Natural idempotency** — prefer operations that are inherently idempotent (upsert by key, set-to-value) over non-idempotent ones (increment, append) where you can.

> **The house rule:** every async handler is idempotent or it is a data-corruption bug waiting to happen. Double-charges, duplicate rows, and double-sent emails are all the same missing key.

---

## Failure handling: DLQ, poison messages, retries

- **Poison message** — a message that fails every time (malformed, references deleted data, hits a permanent bug). Without a limit it retries **forever**, burning invocations and blocking the queue.
- **DLQ (dead-letter queue)** — after **max-receive / max-retry** attempts, route the message to a dead-letter target instead of retrying. Name **who inspects the DLQ** and the **replay/redrive** path — a DLQ nobody watches is a silent data-loss queue.
- **Retry + backoff** — bound the retries; use **exponential backoff (with jitter)**. Unbounded retry against a struggling downstream is a self-inflicted DDoS that turns a blip into an outage.
- **Partial-batch failure** — for batch triggers (stream/queue batches), report *which* records failed so only those retry, not the whole batch (provider-specific mechanism — _retrieved 2026-07-13_).

> **The house rule:** a queue with no DLQ + no poison-message plan is an infinite-retry outage. It's not optional.

---

## The per-invocation cost model

- **The model (generic — unit prices are volatile):**
  `cost ≈ invocations × (duration × memory-price) + invocations × request-price + data-transfer + downstream cost + any provisioned/warm-concurrency floor.`
- **Duration × memory is the usual dominant term** — this is why slimming and rightsizing cut cost, not just latency.
- **Provisioned/warm concurrency is an always-on line item** — it looks like a container's flat cost. Counting it is what keeps "provision to fix cold start" honest.
- **The crossover:** serverless wins on **spiky/bursty/low-duty-cycle** traffic (you pay ~nothing at idle). **Steady, high-throughput** traffic keeps functions near-continuously executing → an **always-on container/instance at high utilization is cheaper per request**. Compute peak-RPS × duration = sustained concurrency, and compare the per-invocation total to the flat instance cost.
- **"Serverless is cheaper" is regime-dependent** — true at low/spiky volume, false at high steady volume. Model it; never ship it as a slogan. (Full branch: [`serverless-engineering-decision-tree.md`](serverless-engineering-decision-tree.md) Tree D.)

---

## Concurrency, limits, and quotas

- **Account/region concurrency is a shared, throttleable limit** — all functions in the scope draw from it; exhausting it throttles the rest. Know the number (_provider-specific, re-verify — retrieved 2026-07-13_) and the quota-increase path.
- **Reserved concurrency** — carve out a guaranteed slice for a critical path (and, inversely, **cap** a function so it can't starve the account or storm a downstream).
- **Provisioned/warm concurrency** — pre-initialized instances for cold-start-sensitive paths (cost above).
- **Downstream is the real ceiling** — a function fronting a connection-pooled RDBMS is bounded by the **pool**, not the account limit. Cap function concurrency to the pool, or use a connection proxy / a managed store. Scale-to-thousands + a fixed pool = a **connection storm**.

---

## Observability & local testing in ephemeral runtimes

- **Distributed tracing is mandatory** — a request is now N functions across queues/buses. Propagate a **correlation/trace id** through every event and log line so you can reconstruct a request end-to-end. You cannot attach a debugger to a function that lived 200ms.
- **Structured logs + metrics** — log with the correlation id; emit custom metrics (duration, cold-start rate, DLQ depth, throttle count).
- **Local emulation / testing** — an emulator or a functions framework for the inner loop, contract tests on event schemas, and a staging path that exercises the real triggers. Don't rely on "deploy and see."
- Tracing/SLOs as a *platform discipline* → `observability-sre`; this team wires the per-function/per-event trace.

---

## Anti-patterns the agents flag

| Anti-pattern | Why it hurts | The fix |
|---|---|---|
| **Distributed monolith / lambda pinball** | Functions calling functions synchronously — a slow/failed step blocks the caller; worse coupling than the monolith it replaced | Design around events + contracts (bus or workflow), not a sync call graph |
| **Dual-write** | Writing to the DB and emitting an event as two independent operations — they drift under partial failure | **Outbox / transactional event** |
| **RDBMS connection storm** | A pooled RDBMS behind thousands of concurrent invocations exhausts connections | Connection proxy/pooler, capped concurrency, or a managed/serverless store |
| **Non-idempotent async handler** | At-least-once delivery + no dedup = double-charge / duplicate rows | Idempotency key + dedup store (exactly-once effect) |
| **Queue with no DLQ** | A poison message retries forever — outage + runaway bill | DLQ + max-receive + a named owner + replay path |
| **Provision-first for cold start** | Warm capacity billed 24/7 erases the serverless cost advantage | Slim + rightsize first; provision only the SLO floor |
| **"Serverless is cheaper" as a slogan** | False at high steady throughput | Model the per-invocation cost + crossover |
| **Serverless for a long-running/streaming job** | Times out; fights the platform | Container/serverful (Tree A) |
| **Visibility timeout < handler duration** | Redelivery mid-processing → double-processing | Set visibility timeout ≥ max handler duration |

---

## 2026 landscape (dated — generic, re-verify before quoting)

- **FaaS platforms** exist across the major clouds (function-as-a-service with event triggers, per-invocation billing, managed scaling) and in container-native/edge variants; **exact limits — concurrency caps, max timeout, package-size, memory range — differ by provider/region and change.** _(Retrieved 2026-07-13; keep generic, route specifics to `aws-cloud`/`gcp-cloud`/`azure-cloud` or research.)_
- **Managed workflow/orchestration services** (state-machine/step-oriented) and **managed event buses / queues / pub-sub** are broadly available and are the default substrate for orchestration and choreography respectively. _(Retrieved 2026-07-13.)_
- **Cold-start mitigations** (provisioned/warm concurrency, snapshot-restore-style fast-init, lightweight runtimes) continue to evolve — the *playbook order* above is durable; the specific feature names/behaviors are volatile. _(Retrieved 2026-07-13.)_
- **Connection-proxy/pooler** services for RDBMS-behind-functions exist across providers — the pattern is durable, the product specifics are not. _(Retrieved 2026-07-13.)_

> **Volatile:** every provider quantity in this doc (concurrency, timeout, package/memory limits, prices, feature names) is a 2026-07 snapshot kept deliberately generic. Re-verify with `ravenclaude-core/deep-researcher` before pinning any number in a deliverable.

---

## Provenance

- Durable concepts (event-driven patterns — fan-out, saga, outbox, claim-check, event-carried state transfer; the cold-start playbook; at-least-once → idempotency/exactly-once-effect; the DLQ/poison discipline; the per-invocation cost model + steady-vs-spiky crossover; the anti-patterns) are consensus practice across the serverless/event-driven-architecture and enterprise-integration-patterns literature and cloud well-architected guidance, reviewed 2026-07-13 — **High confidence**.
- All **provider-specific quantities** (concurrency caps, timeouts, package/memory limits, per-invocation prices, feature names) are a **2026-07 snapshot kept generic**; they are volatile and carry retrieval dates — re-verify with `ravenclaude-core/deep-researcher` before a board or client commitment.
