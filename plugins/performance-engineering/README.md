# Performance Engineering

The **performance-engineering** plugin — the system-performance and capacity craft: setting performance budgets, proving them under load, profiling to find the bottleneck, and planning capacity with real headroom — the throughput/latency/scalability layer of backend systems. Distinct from the browser's Core Web Vitals, the customer-facing SLO/error-budget, the slow SQL query, and the resilience pattern themselves.

## Agents

- **`performance-architect`** — Performance strategy and budgets: non-functional requirements (NFRs) as percentile-plus-load targets, the workload/traffic model (mix, arrival pattern, data shape), SLO-linked targets, and choosing *which* test type (load / stress / soak / spike) answers the question. Sets the number to hold and the conditions it holds at.
- **`load-testing-engineer`** — The test build: load, stress, soak, and spike scenarios in k6 / Gatling / Locust / JMeter, the open- vs closed-model workload choice, ramping and think time, realistic test data, and avoiding coordinated omission. Tool-neutral; builds the test that actually exercises the modeled workload.
- **`profiling-and-capacity-engineer`** — Bottleneck and capacity: CPU/memory/IO profiling, flame graphs, USE/RED triage to localize the constraint, capacity planning and headroom via Little's law, and regression detection against a committed baseline. Names where it breaks first and how big it must be.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install performance-engineering@ravenclaude
```

## Seams

- **The browser being slow (LCP, CLS, bundle size, render path)** → `frontend-engineering`; this team owns server-side/system throughput and latency, the client paint is theirs.
- **The customer SLO, error budget, and production alerting** → `observability-sre`; our NFR targets link to the SLO, they set and protect it.
- **Why one query is slow and what index it needs** → `database-engineering`; we prove the DB is the bottleneck, they tune the query.
- **Surviving a dependency failing — retries, bulkheads, circuit breakers, backpressure** → `backend-engineering`; we find the saturation point, they design the survival behavior.
- **Autoscaling config and node sizing** → `cloud-native-kubernetes` + the cloud plugins; we supply the capacity math and headroom target, they implement the HPA/instance plan.
- **De-identifying prod-derived test data and guarding load against shared/prod systems** → `data-governance-privacy` + `ravenclaude-core/security-reviewer`.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`. Designed to be installed alongside `observability-sre`, `database-engineering`, `backend-engineering`, and `cloud-native-kubernetes`.
