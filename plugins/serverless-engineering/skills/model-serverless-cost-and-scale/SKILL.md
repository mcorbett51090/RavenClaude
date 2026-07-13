---
name: model-serverless-cost-and-scale
description: "Model serverless cost and scale — a per-invocation cost model (invocations × duration × memory + requests + data-transfer + downstream), the serverless-vs-container crossover point where steady high-throughput makes always-on cheaper (and 'serverless is cheaper' stops being true at scale), and concurrency/quota/limit planning (account/region caps, reserved/provisioned concurrency, throttle headroom). Reach for this on 'is serverless actually cheaper here?', 'where do we cross over to containers?', or 'plan our concurrency/quota headroom'. Driven by `serverless-runtime-and-ops-engineer` (primary), consulted by `serverless-architect` for the cost side of the serverless-vs-not call."
---

# Skill: model-serverless-cost-and-scale

> **Invoked by:** `serverless-runtime-and-ops-engineer` (primary). Consulted by `serverless-architect` for the cost crossover that decides the serverless-vs-container-vs-managed-service call, and by `harden-serverless-runtime` for the cost impact of provisioned/warm concurrency.
>
> **When to invoke:** "Is serverless actually cheaper than a container here?"; "where's the crossover point at scale?"; "model our per-invocation cost"; "plan our concurrency/quota headroom"; any cost/scale question on a serverless design.
>
> **Output:** a per-invocation cost model + the steady-vs-spiky crossover point (where always-on containers get cheaper) + a concurrency/quota headroom plan, with the assumptions and flip conditions stated.

## Procedure

1. **Frame the traffic and the unit of work.** Requests per second/day (and the *shape* — steady vs spiky/bursty vs near-zero-then-peak), the per-invocation duration, the memory/CPU allocation, and the downstream cost per call (DB, third-party API, data transfer). Cost is driven by the *shape*, not just the total.
2. **Build the per-invocation cost model** using [`../../knowledge/serverless-engineering-patterns-2026.md`](../../knowledge/serverless-engineering-patterns-2026.md). The generic model: `cost ≈ invocations × (duration × memory-price) + invocations × request-price + data-transfer + downstream`. Keep the *unit prices generic* (they're volatile — retrieval date or route to research); the **structure** of the model is what matters. Add the fixed cost of any **provisioned/warm concurrency** floor (it's always-on, so it looks like a container line item).
3. **Compute the serverless-vs-container crossover** via [`../../knowledge/serverless-engineering-decision-tree.md`](../../knowledge/serverless-engineering-decision-tree.md) Tree D. Serverless wins on **spiky/bursty/low-duty-cycle** traffic (you pay ~nothing at idle). A **steady, high-throughput** load keeps functions warm-equivalent 24/7 — at which point an always-on container/instance (flat hourly cost, high utilization) gets **cheaper per request**. Find the utilization/throughput level where the two lines cross and state it as the crossover.
4. **Sanity-check the "serverless is cheaper" claim.** At low/spiky volume it usually is; at high steady volume it usually isn't. Name *which regime this workload is in* — don't let "serverless is cheaper" ship as a slogan when the traffic is steady-high.
5. **Plan the concurrency & quota headroom.** Map peak RPS × duration → peak concurrent executions; compare to the **account/region concurrency limit**; decide **reserved** concurrency for critical paths and whether a **provisioned** floor is justified (cost from step 2). Leave throttle headroom and name the quota-increase path.
6. **Protect the downstream in the scale math.** If the function fronts a connection-pooled RDBMS, the concurrency cap is set by the *pool*, not the account limit — factor that ceiling in (and route the design fix to `harden-serverless-runtime`).
7. **State assumptions, seams, and flip conditions.** Record the traffic and price assumptions in [`../../templates/serverless-architecture-decision-record.md`](../../templates/serverless-architecture-decision-record.md); route exact provider prices to `ravenclaude-core/deep-researcher`; name the flip conditions (traffic doubles and goes steady, duration grows, memory rightsizes) that move the crossover.

## Worked example

> User: "We're told serverless will be cheaper than our two always-on containers. The function runs 300ms, 512MB, and we do about 200 requests/second all day, every day. Is that right?"

- **Traffic shape is the tell:** 200 rps *all day, every day* is **steady high-throughput**, not spiky — the regime where serverless is *least* likely to win.
- **Concurrency:** 200 rps × 0.3s ≈ **~60 concurrent executions** sustained, 24/7. That's effectively ~60 always-warm function-equivalents around the clock — you're paying per-invocation for near-100% duty cycle.
- **Per-invocation model:** ~200 × 86,400 ≈ **17.3M invocations/day**, each 300ms × 512MB, plus request + data cost. Build the model with generic unit prices (flag them volatile), then compare to the flat cost of the two containers at high utilization.
- **Crossover call (Tree D):** at this steady, high duty cycle the always-on containers are almost certainly **cheaper per request** — this workload is *past* the crossover. Serverless would win if the traffic were spiky (big peaks, near-zero troughs), because you'd stop paying at idle; it isn't.
- **Recommendation:** keep the containers (or a rightsized instance) for this steady load; reserve serverless for the spiky/bursty edges. Model the exact numbers before committing.
- **Flip condition:** if the traffic becomes spiky (e.g. a batch/seasonal pattern with long idle troughs), re-run the model — the crossover moves toward serverless.

## Guardrails

- **Never ship "serverless is cheaper" as a slogan** — name the traffic regime (spiky → serverless; steady high-throughput → container) and model the crossover for *this* workload.
- **Cost = per invocation** — invocations × duration × memory + requests + data-transfer + downstream; a provisioned/warm floor is an always-on line item, count it.
- **Model the crossover before scale makes serverless expensive** — the "serverless gets expensive at scale" point is real and predictable.
- **Concurrency math is peak RPS × duration** — compare to the account/region limit, plan reserved/provisioned, leave throttle headroom.
- **The RDBMS pool, not the account limit, may be the real concurrency ceiling** — factor it in (fix → `harden-serverless-runtime`).
- **Unit prices are volatile** — keep the model *structure* fixed and generic, carry a retrieval date, and route exact provider prices to `ravenclaude-core/deep-researcher`. See [`../../knowledge/serverless-engineering-patterns-2026.md`](../../knowledge/serverless-engineering-patterns-2026.md).
