# Changelog — performance-engineering

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

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
