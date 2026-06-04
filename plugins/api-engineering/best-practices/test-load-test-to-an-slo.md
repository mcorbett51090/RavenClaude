# Load-test to an SLO, not to a number

**Status:** Pattern — a load test without a stated objective is a benchmark, not a gate.

**Domain:** API testing / performance

**Applies to:** `api-engineering`

---

## Why this exists

"We did 10,000 requests per second" means nothing without a target and a latency/error bound. A load test should answer a yes/no question — *does the API meet its service-level objective under expected load?* — so the result gates a release. State the SLO first (p95 latency, throughput, max error rate), then run **k6** (or equivalent) against it, and observe how rate limits and the error model behave under stress, not just the average.

## How to apply

Define the SLO, script the load, assert pass/fail on the objective.

```js
// k6 — assert against an SLO, not a vanity number
import http from "k6/http";
export const options = {
  scenarios: { ramp: { executor: "ramping-vus", stages: [
    { duration: "2m", target: 500 }, { duration: "5m", target: 500 } ] } },
  thresholds: {
    http_req_duration: ["p(95)<200"], // SLO: p95 under 200ms
    http_req_failed: ["rate<0.01"], // SLO: <1% errors
  },
};
export default function () { http.get("https://api.example.com/orders?limit=20"); }
```

**Do:**
- Write the SLO down before the test; fail CI/the release if a threshold is breached.
- Test at and beyond expected peak; confirm `429`/`Retry-After` and Problem Details behave correctly under throttle.

**Don't:**
- Report raw throughput with no objective; load-test only the happy path; ignore error-rate and tail latency (p95/p99).

## Edge cases / when the rule does NOT apply

Early-stage internal APIs may not have a formal SLO yet — set a provisional one rather than skipping the gate. Soak (endurance) and spike tests answer different questions (leaks, autoscaling) than a steady-load SLO test; pick the profile to the risk.

## See also

- [`./secure-limit-resource-consumption.md`](./secure-limit-resource-consumption.md)
- [`./operate-rate-limit-and-advertise-it.md`](./operate-rate-limit-and-advertise-it.md)
- [k6](https://grafana.com/docs/k6/latest/) — authoritative `[verify-at-build]`

## Provenance

Grounded in SLO-driven load testing (k6). Tool capabilities verified before quoting. Retrieved/verified 2026-06-04.

---

_Last reviewed: 2026-06-04 by `claude`_
