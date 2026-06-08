# Changelog — performance-engineering

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

## 0.2.0 — 2026-06-08

Depth pass — no behavioral change to the agents, skills, commands, or hook; this release deepens the
knowledge, evidence, and tooling around them.

- **Best-practices 8 → 12** — added `name-the-objective-latency-or-throughput`, `prove-the-bottleneck-hand-off-the-fix`,
  `reproducible-or-it-didnt-happen`, and a split-out `target-needs-a-workload`, bringing the atomic rule set to 12.
- **Decision trees 3 → 5** — the knowledge bank's `performance-engineering-decision-trees.md` now carries five Mermaid
  trees: which-test-type (load/stress/soak/spike), open- vs closed-workload model, bottleneck triage (USE/RED → profile →
  capacity), is-this-a-real-regression-and-does-it-gate, and who-owns-the-fix routing. The dated 2026 capability map
  (`[verify-at-build]`) is retained.
- **Capacity calculator** — new `scripts/perf_calc.py` (stdlib-only): `littles-law` (solve `L = λ·W` for the omitted term),
  `capacity` (target RPS + latency + headroom → required concurrency + instance count below the knee), and `percentiles`
  (latency samples → p50/p90/p95/p99 + min/max/mean via nearest-rank). Decision-support, not a data source.
- **Scenarios bank 2 → 5** — added `the-leak-only-showed-after-six-hours` (soak/leak), `the-spike-broke-what-steady-load-didnt`
  (spike/elasticity), and `planned-to-the-knee-with-no-headroom` (capacity/Little's-law) (all `reviewed: false`), each
  corroborating named best-practices.

## 0.1.0 — 2026-06-08

Initial release. The system-performance and capacity-engineering layer, distinct from frontend Core Web Vitals
and observability-sre SLOs.

- **3 agents** — `performance-architect` (performance budgets/NFRs, workload modeling, SLO-linked targets, test-type
  selection), `load-testing-engineer` (load/stress/soak/spike testing with k6/Gatling/Locust/JMeter, open- vs
  closed-model workload, ramping + think time, test data, coordinated-omission avoidance), `profiling-and-capacity-engineer`
  (CPU/memory/IO profiling, flame graphs, USE/RED bottleneck triage, capacity planning + headroom via Little's law,
  regression detection). Each carries the full scenario-authoring frontmatter.
- **3 skills** — `performance-test-strategy`, `load-test-design`, `profiling-and-bottleneck-triage`.
- **Knowledge bank** — `performance-engineering-decision-trees.md`: Mermaid trees (which-test-type, open- vs
  closed-workload-model, bottleneck-triage) + a dated 2026 capability map (`[verify-at-build]`).
- **8 best-practices**, **3 commands** (`design-performance-test`, `run-load-test`, `triage-bottleneck`),
  **2 templates** (performance test plan, capacity-and-bottleneck report), **1 advisory hook**
  (`check-performance-engineering-anti-patterns.sh`; `PERF_STRICT=1` to make it blocking), and a **scenarios bank** (2 field notes).
- Seams: web Core Web Vitals → `frontend-engineering`; SLO/error-budget → `observability-sre`; query tuning →
  `database-engineering`; resilience → `backend-engineering`; autoscaling → `cloud-native-kubernetes`. Requires `ravenclaude-core@>=0.7.0`.
