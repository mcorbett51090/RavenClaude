# Serverless function readiness checklist — <function name>

> Per-function production-readiness gate. A function does not ship until each box has a real answer — not a hopeful "should be fine."
> The two non-negotiables: **every async handler is idempotent**, and **every queue has a DLQ + poison-message plan**.
> Pairs with [`serverless-architecture-decision-record.md`](serverless-architecture-decision-record.md) (the design) · hardening ref: [`../knowledge/serverless-engineering-patterns-2026.md`](../knowledge/serverless-engineering-patterns-2026.md).

**Function:** <name> · **Trigger:** <sync API | queue | stream | schedule | event bus> · **Runtime:** <language/version> · **Owner:** <team> · **Status:** not-ready / ready

## Correctness & idempotency
- [ ] **Idempotent?** — <idempotency key (message id / business key / client token) + dedup store; a redelivered message is a no-op. REQUIRED for any async/queue/stream trigger — delivery is at-least-once.>
- [ ] **Effect is exactly-once** — <side effects (charge, write, email) can't double under retry.>
- [ ] **Natural idempotency preferred** — <upsert-by-key over increment/append where possible.>

## Concurrency & limits
- [ ] **Bounded concurrency?** — <reserved concurrency for the critical path; capped so it can't starve the account or storm a downstream.>
- [ ] **Account/region quota headroom** — <peak RPS × duration = sustained concurrency vs the limit; quota-increase path known.>
- [ ] **Downstream protected** — <if it fronts a pooled RDBMS, concurrency capped to the pool OR a connection proxy / managed store in place — no connection storm.>

## Failure handling
- [ ] **DLQ + poison plan?** — <dead-letter target + max-receive/redrive; a poison message stops retrying after N and lands in the DLQ. REQUIRED for every queue — no DLQ is an infinite-retry outage.>
- [ ] **DLQ has an owner + replay path** — <someone inspects it; a documented redrive.>
- [ ] **Retry/backoff bounded** — <bounded retries, exponential backoff + jitter; no unbounded retry against a failing downstream.>
- [ ] **Timeout/retry set** — <handler timeout set deliberately; **visibility timeout ≥ handler max duration** (a shorter one causes redelivery mid-flight).>
- [ ] **Partial-batch failure handled** — <for batch triggers, only failed records retry, not the whole batch.>

## Cold start & performance
- [ ] **Cold-start acceptable?** — <measured cold-start latency vs the budget. Slim package + deferred init done FIRST.>
- [ ] **Provisioned/warm concurrency justified** — <only if the tail SLO demands it; floor capped to the measured need — not over-provisioned (it erases the cost advantage).>
- [ ] **Memory rightsized** — <memory/CPU tuned for cost AND init speed.>

## Security & least privilege
- [ ] **Least-privilege?** — <the function's role grants only the resources it uses; no wildcard/admin.>
- [ ] **Secrets handled** — <secrets from a manager/parameter store, not baked into the package or env in plaintext.>

## Observability & testing
- [ ] **Traced?** — <distributed tracing + a correlation/trace id propagated through every event and log line.>
- [ ] **Structured logs + metrics** — <duration, cold-start rate, DLQ depth, throttle count.>
- [ ] **Local emulation / tests** — <inner-loop emulator, event-schema contract tests, a staging path exercising real triggers.>

## Cost
- [ ] **Cost-modeled?** — <per-invocation model built; regime known (spiky→serverless / steady-high→crossover); provisioned floor counted as an always-on line item.>

## Seams (not this checklist)
- **Provider-specific config (the actual concurrency/timeout/DLQ/proxy resource):** aws-cloud / gcp-cloud / azure-cloud
- **The deploy pipeline (CI/CD, canary, IaC apply):** devops-cicd
- **Tracing platform / SLOs:** observability-sre
- **The design / decomposition / event contracts:** serverless-architect

**Sign-off:** <reviewer> · <date>
