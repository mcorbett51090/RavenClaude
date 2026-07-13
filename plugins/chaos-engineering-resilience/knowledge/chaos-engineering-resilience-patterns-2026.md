# Knowledge — Chaos-engineering & resilience patterns (2026)

> **Last reviewed:** 2026-07-13 · **Confidence:** High on the durable concepts (the resilience-pattern catalog, the principles of chaos, the experiment loop, the maturity gate, the anti-patterns); **Medium on the dated tooling snapshot — fault-injection product names, features, and managed-chaos-service capabilities are volatile and carry retrieval dates below; do NOT assert exact current features without re-verifying.**
> The reference the two agents read when designing resilience and running experiments: the resilience-pattern catalog, the principles of chaos, the fault-injection taxonomy, a dated tooling snapshot, and the anti-patterns that make chaos dangerous instead of useful.

The team's discipline: **resilience is designed in, not tested in; no chaos without steady-state observability; every experiment is a hypothesis with the smallest blast radius and an abort condition; and every volatile tool/feature claim carries a retrieval date.**

---

## The resilience-pattern catalog

The patterns a system is *designed* with so a dependency's failure is contained, absorbed, or degraded — not propagated. (Chosen per Decision Tree C; each carries its own failure mode to defend.)

| Pattern | What it does | Design notes |
|---|---|---|
| **Timeout** | Bounds how long a remote call may wait | Every remote call gets a real deadline; an unset timeout is infinite. Tune to the dependency's healthy p99, not a round number. |
| **Retry + backoff + jitter + budget** | Re-attempts a transient failure | **Idempotent calls only.** Exponential backoff spreads load; **jitter** de-synchronizes the herd; a **retry budget** caps the amplification. Missing any of the three → a self-inflicted DDoS. |
| **Circuit breaker** | Stops calling a failing dependency after a threshold, gives it time to recover | Closed → open → half-open. Pair with a **fallback** — an open breaker with nothing behind it just fails faster. Tune thresholds to avoid flapping. |
| **Bulkhead** | Isolates resource pools so one dependency's exhaustion can't starve others | Per-dependency (or per-tenant) thread/connection pools. Size them: too small throttles healthy traffic, too large defeats the isolation. |
| **Load shedding / rate limiting** | Drops or rejects work when overloaded, protecting core capacity | Prioritize — shed low-value work first; return a clear signal (429) so callers back off. |
| **Graceful degradation / fallback** | Serves a reduced experience when a dependency is down | Cached, default, or queued responses; a partial page beats a blank one. The fallback path must itself be tested — a stale fallback that misleads is its own failure. |
| **Idempotency** | Makes repeated operations safe (so retries/redelivery don't double-charge) | Strong idempotency keys; guard the side effects, not just the request. Prerequisite for safe retries and at-least-once messaging. |
| **Backpressure** | Signals upstream to slow down instead of unbounded buffering | Bounded queues with a shed path; propagate the pressure rather than blowing memory. |
| **Redundancy & failover** | Survives instance/zone/region loss | Multi-AZ (cheap, common) vs multi-region (expensive, for region loss); active-active vs active-passive failover. Tie to explicit RTO/RPO. |

> **The design order:** start from the FMEA (the named failure mode), pick the pattern that defends it, place it at the right boundary, and defend the pattern's own failure mode. Then prove it with a chaos experiment.

---

## The principles of chaos engineering

The discipline's guardrails — an experiment that violates these is either theater or an outage:

1. **Build a hypothesis around steady-state behavior.** Define the measurable "healthy" (a business/system metric), then hypothesize it holds under the fault. No steady state → no experiment.
2. **Vary real-world events.** Inject faults that actually occur — dependency slowness, instance/zone loss, network partition, resource exhaustion — not contrived ones.
3. **Run experiments in production — carefully.** Prod is where real behavior lives, but only after it holds in staging, with the smallest scope and an automatic abort.
4. **Minimize the blast radius.** The smallest experiment that can disprove the hypothesis. Contain it; widen only when it holds small.
5. **Automate to run continuously.** A one-time experiment is a point-in-time proof; continuous experiments catch regressions as the system evolves. Automate *after* manual runs are proven safe.

---

## The fault-injection taxonomy

The kinds of fault an experiment can inject (pick the one that tests the hypothesis — Decision Tree B):

| Fault type | Injects | Tests |
|---|---|---|
| **Latency** | Added delay on a dependency call | Timeouts, circuit breakers, timeout budgets, user-facing degradation |
| **Error** | Forced error responses (5xx, exceptions) | Retries, fallbacks, error handling, breaker thresholds |
| **Resource exhaustion** | CPU/memory/disk/connection-pool/file-descriptor pressure | Bulkheads, load shedding, autoscaling, backpressure |
| **Dependency outage** | A dependency made fully unavailable | Fallbacks, graceful degradation, circuit breakers |
| **Network partition** | Split/blackhole between components | Consistency handling, failover, quorum behavior, split-brain defenses |
| **Zone / region failure** | An entire AZ/region made unreachable | Multi-AZ/region redundancy, failover, RTO/RPO, DNS/traffic shifting |

> The **experiment loop** wrapping any injection: steady-state → hypothesis → smallest blast radius → inject (under load) → observe (correlate to the injection window) → abort-or-learn → remediate. See `../skills/run-chaos-experiment/SKILL.md`.

---

## Fault-injection & chaos tooling snapshot (dated — volatile, re-verify before quoting)

> **Named generically with a retrieval date. Do NOT assert exact current features, pricing, or availability — these change; re-verify with `ravenclaude-core/deep-researcher` before a commitment.**

- **Open-source chaos platforms** — Kubernetes-native chaos tooling (e.g. the Chaos Mesh and LitmusChaos projects) and general-purpose fault injectors exist for injecting latency/error/resource/network faults, often as CRDs or agents. _(Retrieved 2026-07-13 — feature sets evolve; verify against current project docs.)_
- **Managed / cloud chaos services** — major cloud providers offer managed fault-injection services (e.g. AWS Fault Injection Service and equivalents) that inject faults against cloud resources with built-in stop conditions. _(Retrieved 2026-07-13 — capabilities and regional availability change; verify.)_
- **Commercial chaos platforms** — commercial offerings in the Gremlin lineage provide a catalog of attacks with blast-radius controls and a halt button. _(Retrieved 2026-07-13 — verify current features.)_
- **Resilience libraries** — the resilience4j / Polly / Hystrix lineage provides in-process timeout/retry/circuit-breaker/bulkhead/rate-limiter primitives; service meshes (Envoy-based) provide timeout/retry/outlier-detection at the network layer. _(Retrieved 2026-07-13 — library defaults and semantics vary by version; read the current docs before relying on a default.)_
- **Steady-state observability (prerequisite, not this team)** — metrics/traces/SLO tooling is what makes an experiment readable; it is owned by `observability-sre`. Without it, none of the above is safe to run.

> **Volatile:** every product name, feature, default, and availability claim above is a 2026-07 snapshot. Treat it as orientation, not authority — re-verify before a board, client, or production commitment.

---

## Anti-patterns the agents flag

- **Running chaos with immature observability** — you can't tell an experiment from an outage; you're just breaking prod with extra steps. The maturity gate blocks this.
- **"Let's kill a box and see what happens"** — no steady state, no hypothesis, no blast-radius limit, no abort. That's gambling, not chaos engineering.
- **An experiment with no abort condition** — an outage with paperwork. The automatic halt is defined *before* the fault is injected.
- **Region-first / prod-first blast radius** — widening before it holds small. Staging → one cell → one region, earned each round.
- **Retries without backoff + jitter + a budget** — a self-inflicted DDoS that turns a blip into an outage; and retrying a *slow* or non-idempotent dependency on the hot path.
- **A circuit breaker with no fallback** — it just fails faster; the user still sees an error.
- **Timeouts left unset** — an infinite wait that exhausts the thread pool and cascades.
- **Testing the pattern idle** — proving a breaker holds at 2 RPS tells you nothing about 2000 RPS; inject under realistic load.
- **"Nothing broke" as a pass** — an uncorrelated green dashboard proves nothing; correlate the steady-state metric to the injection window.
- **Chaos as a substitute for design** — resilience is designed in, not tested in. Injecting faults into a system with no patterns just discovers an outage you already owned.
- **Game days that skip the debrief/backlog** — theater. Every finding becomes a ranked, owned remediation item.
- **Quoting a chaos tool's feature, a library default, or a managed-service capability with no retrieval date.**

---

## Provenance

- The resilience-pattern catalog, the principles of chaos, the experiment loop, the maturity gate, and the fault-injection taxonomy are consensus practice across the chaos-engineering and resilience literature (Principles of Chaos Engineering; Basiri et al., "Chaos Engineering"; Nygard, *Release It!*; the Hystrix/resilience4j/Polly pattern lineage), reviewed 2026-07-13 — **High confidence** on the durable concepts.
- The tooling/service snapshot is a **2026-07 snapshot**; product names, features, defaults, pricing, and availability are volatile and carry the retrieval dates above — re-verify with `ravenclaude-core/deep-researcher` before pinning in a deliverable or a production commitment.
