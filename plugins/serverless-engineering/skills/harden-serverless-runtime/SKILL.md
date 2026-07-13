---
name: harden-serverless-runtime
description: "Harden a serverless function/pipeline for the runtime & ops realities — cold starts (causes, the provisioned/warm-concurrency vs package-slimming trade-off against the latency budget, and what NOT to over-provision), concurrency & account/region limits & throttling with downstream (RDBMS) protection, idempotency keys + exactly-once-EFFECT (delivery is at-least-once), DLQ + poison-message policy, and retry/backoff/visibility-timeout so a queue is never an infinite-retry outage. Reach for this on 'fix our cold starts', 'this queue double-processes / retries forever', or 'we're getting throttled — plan our concurrency'. Driven by `serverless-runtime-and-ops-engineer` (primary)."
---

# Skill: harden-serverless-runtime

> **Invoked by:** `serverless-runtime-and-ops-engineer` (primary). The idempotency/DLQ/cold-start constraints usually arrive as requirements from `design-event-driven-architecture`.
>
> **When to invoke:** "Fix our cold starts"; "this queue double-processes / retries forever / poisons"; "we're getting throttled — plan concurrency/quotas"; "make this async handler safe to retry"; any move on the runtime/failure behavior of a function.
>
> **Output:** a hardening plan — cold-start posture + concurrency/quota plan + idempotency design + DLQ/poison policy + retry/visibility settings + observability — captured in the function readiness checklist.

## Procedure

1. **Frame the function and its budget.** Trigger (sync API / queue / stream / schedule), language/runtime, package size, downstream dependencies (DB, third-party API), traffic profile (steady vs spiky), and the **latency budget** (does the tail matter?). This decides how hard each lever is worth pulling.
2. **Diagnose and budget cold start** via [`../../knowledge/serverless-engineering-patterns-2026.md`](../../knowledge/serverless-engineering-patterns-2026.md) (cold-start playbook). Name the causes — init/bootstrap code, package/dependency size, VPC/ENI attach, language runtime (interpreted vs compiled), lazy-load opportunities. **Slim the package and defer init first**; reach for provisioned/warm concurrency **only** when the tail latency budget demands it — and cap it, because over-provisioning warm capacity deletes the serverless cost advantage (hand the cost impact to [`model-serverless-cost-and-scale`](../model-serverless-cost-and-scale/SKILL.md)).
3. **Design idempotency — exactly-once EFFECT, not delivery.** Delivery is **at-least-once**; pick an idempotency key (message id, business key, or a client-supplied token), a dedup store (a short-TTL record of processed keys), and make a redelivered message a **no-op**. This is mandatory for every async/queue/stream handler — without it, a retry corrupts data.
4. **Give every queue a DLQ + poison-message plan** via [`../../knowledge/serverless-engineering-decision-tree.md`](../../knowledge/serverless-engineering-decision-tree.md) Tree C. Set **max-receive/redrive** so a message that fails N times routes to a **dead-letter queue** instead of retrying forever; name who inspects the DLQ and the replay path. A queue with no DLQ + no max-receive is an infinite-retry outage.
5. **Set retries, backoff, and visibility timeout on purpose.** Visibility timeout **≥ the handler's max duration** (or the message redelivers mid-flight and double-processes); bound the retry count; use exponential backoff. Unbounded retry against a failing downstream is a self-inflicted DDoS.
6. **Plan the concurrency envelope and protect the downstream.** Know the **account/region concurrency limit** (a shared, throttleable quota); **reserve** concurrency for the critical path; and **cap** concurrency in front of a connection-pooled RDBMS so scale-out doesn't become a connection storm. State the quota headroom and the throttle-and-retry behavior.
7. **Make the ephemeral runtime observable and testable.** Distributed tracing across the event hops (a request is now N functions), a **correlation id** propagated through every event, structured logs, and a **local-emulation/test** story. Capture the whole posture in [`../../templates/serverless-function-readiness-checklist.md`](../../templates/serverless-function-readiness-checklist.md).
8. **State the seams and flip conditions.** The deploy pipeline → `devops-cicd`; tracing/SLOs as a discipline → `observability-sre`; provider knobs (the actual concurrency/timeout/DLQ resource) → `aws-cloud`/`gcp-cloud`/`azure-cloud`. Name the 1-2 facts (traffic profile shifts, latency budget tightens) that would change the plan.

## Worked example

> User: "Our SQS-triggered Lambda charges customers. Sometimes a customer gets charged twice, and last week one bad message retried for hours and ran up our bill. The function also feels slow on the first hit in the morning. Fix it."

- **Double-charge = missing idempotency.** SQS is **at-least-once** — a redelivered message re-runs the charge. Add an **idempotency key** (the order id or a payment token), a **dedup store** (record charged keys with a TTL), and make a repeat a no-op. This is the root cause, not a fluke.
- **"Retried for hours + ran up the bill" = no DLQ / no max-receive.** Set **maxReceiveCount** (e.g. small N) with a **dead-letter queue**; a poison message goes to the DLQ after N attempts instead of retrying forever. Add a **correlation id** so you can find what poisoned it, and a named owner + replay path for the DLQ.
- **Visibility timeout check:** confirm the SQS visibility timeout **≥ the Lambda max duration** — if the function can run 60s but the timeout is 30s, SQS redelivers mid-charge, which *also* causes double-processing. Set it above the handler's max.
- **Slow first hit = cold start.** Diagnose: package size, VPC attach, init code. **Slim the package + lazy-init the payment SDK first.** Only if the morning-latency SLO still misses, add **provisioned concurrency** on a small floor — and model the cost so warm capacity doesn't erase the savings (→ `model-serverless-cost-and-scale`).
- **Concurrency:** if the charge path also hits a Postgres ledger, **reserve/cap** concurrency so a spike doesn't storm the connection pool.
- **Seams:** the actual SQS redrive-policy + reserved-concurrency IaC → the provider cloud plugin; the deploy → `devops-cicd`.

## Guardrails

- **Every async/queue/stream handler is idempotent** — exactly-once *effect* via an idempotency key + dedup store. Assuming exactly-once delivery is the bug.
- **No queue ships without a DLQ + max-receive/redrive** — an infinite-retry loop is an outage and a runaway bill.
- **Visibility timeout ≥ handler max duration**, always — a shorter timeout is a redelivery/double-process bug.
- **Bound retries + backoff** — unbounded retry against a failing downstream is a self-inflicted DDoS.
- **Slim before you provision** — over-provisioning warm/provisioned concurrency deletes the serverless cost story; match the cold-start fix to the latency budget, don't gold-plate it.
- **Cap concurrency in front of a pooled RDBMS** — scale-to-thousands + a connection pool = a connection storm.
- **Ephemeral runtimes need a correlation id + distributed trace** — you can't attach a debugger to a 200ms function.
- Keep provider limits/prices **generic with a retrieval date** — concurrency caps, timeouts, and per-GB-second costs are volatile; route exact numbers to `ravenclaude-core/deep-researcher`.
