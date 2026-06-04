# QA & Test Automation — Decision Trees

_Decision trees + a dated capability map. Capability rows are `[verify-at-build]` — re-check against the vendor before quoting. Last reviewed: 2026-06-04._

Traverse before choosing a test level or chasing a flake.

## Decision Tree: Which test level for this defect?

Push the assertion to the cheapest level that can catch the defect.

```mermaid
graph TD
  A[A behaviour to protect] --> B{Pure logic / a function?}
  B -- Yes --> C[Unit test: fast, many]
  B -- No --> D{Interaction between components/services?}
  D -- Yes, within our code --> E[Integration test]
  D -- Yes, across a service boundary --> F[Contract test -> api-engineering]
  D -- No, a full user journey --> G{Is it a CRITICAL journey?}
  G -- Yes --> H[E2E test - keep these few]
  G -- No --> I[Cover at a lower level; don't add E2E]
```

_If you reach for E2E for a logic bug, you have an ice-cream-cone problem._

## Decision Tree: A test is flaky — triage

A flaky test is broken. Fix determinism or quarantine; never normalize re-running.

```mermaid
graph TD
  A[Intermittent failure] --> B{Uses a fixed sleep / timing?}
  B -- Yes --> C[Replace with condition-based wait]
  B -- No --> D{Shares mutable data/env with other tests?}
  D -- Yes --> E[Isolate: per-test factory data + ephemeral env]
  D -- No --> F{Depends on real network/time/randomness?}
  F -- Yes --> G[Stub boundary, fake clock, seed RNG]
  F -- No --> H{Order-dependent?}
  H -- Yes --> I[Remove ordering assumption]
  H -- No --> J[Quarantine + assign owner + investigate]
```


## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| Playwright | GA, broad adoption | Auto-wait, trace viewer, parallelism built-in |
| Cypress | GA | Component + E2E; watch for app-domain limits |
| Mutation testing (Stryker/PIT/mutmut) | mature per-language | Measures test quality, not just coverage |
| Service virtualization / WireMock | mature | Stub third-party boundaries for determinism |
| Testcontainers | GA | Ephemeral containerized deps; local==CI |
| Coverage gating in CI | standard | Use as a floor; pair with mutation on critical paths |
