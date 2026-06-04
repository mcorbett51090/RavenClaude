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


## Decision Tree: Mock, stub, fake, or real dependency?

Match the test double to what you're actually verifying — the wrong double is either a brittle test or a false pass.

```mermaid
graph TD
  A[A dependency in the test] --> B{Is exercising THIS dependency the point of the test?}
  B -- Yes --> C[Use the real thing - or a high-fidelity ephemeral one Testcontainers]
  B -- No --> D{Do you need to assert HOW it was called?}
  D -- Yes --> E[Mock: verify the interaction/contract]
  D -- No --> F{Need realistic behavior/state, just faster?}
  F -- Yes --> G[Fake: in-memory working implementation]
  F -- No --> H{Just need a canned return to proceed?}
  H -- Yes --> I[Stub: fixed responses, no behavior]
```

_Over-mocking tests your mocks, not your code. Mock at the boundary you own; prefer a fake or real dep over a wall of stubs._

## Decision Tree: Unit, integration, or contract for a seam?

A boundary between components or services needs the cheapest test that actually protects the agreement across it.

```mermaid
graph TD
  A[A seam to protect] --> B{Is it a boundary between two deployable services?}
  B -- No, in-process modules --> C{Pure logic with no I/O?}
  C -- Yes --> D[Unit test]
  C -- No --> E[Integration test: real wiring, in-process]
  B -- Yes --> F{Do both sides live in repos you control?}
  F -- Yes --> G[Contract test: consumer-driven, verified in provider CI -> api-engineering]
  F -- No, external/third-party --> H{Can you pin a recorded contract?}
  H -- Yes --> G
  H -- No --> I[Thin integration test against a virtualized boundary]
```

_Don't spin up both services for what a contract test catches faster. Push each assertion to the cheapest level that protects the agreement._

## Decision Tree: Quarantine, fix, or delete a flaky test?

A flaky test is broken; decide its fate by its value, not by inertia.

```mermaid
graph TD
  A[A test fails intermittently] --> B{Does it guard a critical, high-value behavior?}
  B -- No --> C{Is anyone willing to own it?}
  C -- No --> D[Delete it: a test nobody will fix protects nothing]
  C -- Yes --> E[Quarantine with owner + deadline]
  B -- Yes --> F{Root cause known and fixable now?}
  F -- Yes --> G[Fix determinism now: condition waits / isolation / fake clock]
  F -- No --> E
  E --> H{Deadline reached unfixed?}
  H -- Yes --> I[Re-decide: fix or delete - the lane is not a graveyard]
```

_Quarantine restores signal; it is not a verdict. At the deadline a test gets fixed or deleted with a reason — never left to rot._

## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| Playwright | GA, broad adoption | Auto-wait, trace viewer, parallelism built-in |
| Cypress | GA | Component + E2E; watch for app-domain limits |
| Mutation testing (Stryker/PIT/mutmut) | mature per-language | Measures test quality, not just coverage |
| Service virtualization / WireMock | mature | Stub third-party boundaries for determinism |
| Testcontainers | GA | Ephemeral containerized deps; local==CI |
| Coverage gating in CI | standard | Use as a floor; pair with mutation on critical paths |
