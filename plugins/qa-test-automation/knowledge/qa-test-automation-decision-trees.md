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

## Decision Tree: Should this test be in the blocking merge gate?

**When this applies:** adding a new test type (visual, performance, accessibility, load) or a new test suite and deciding whether it should block the PR merge or run as a non-blocking informational job.

**Last verified:** 2026-06-05 against CI/CD best practices and Playwright/GitHub Actions documentation.

```mermaid
flowchart TD
    START[A new test or suite to add to CI] --> Q1{Does a failure mean the code is unshippable?}
    Q1 -->|yes, always| BLOCK[Blocking required check]
    Q1 -->|sometimes| Q2{Is the false-positive rate controlled and low?}
    Q2 -->|yes, stable signal| BLOCK
    Q2 -->|no, frequent false positives| Q3{Can we fix the flakiness before adding it?}
    Q3 -->|yes, fixable now| BLOCK
    Q3 -->|no, structural flakiness| NON_BLOCK[Non-blocking informational job - must pass before deploy]
    Q1 -->|no, informational only| NON_BLOCK
    NON_BLOCK --> REVIEW[Flag failures for human review - not auto-approved]
```

**Rationale per leaf:**
- *Blocking required check* — tests that reliably signal unshippable code belong in the gate; false positives destroy trust.
- *Non-blocking informational* — tests that often false-positive (visual diffs, performance on shared runners) should inform, not block; they are reviewed, not ignored.

**Tradeoffs summary:**

| Method | Cost / time | Blast radius | Approval gate? | Use when |
|---|---|---|---|---|
| Blocking | High if flaky | Blocks all PRs | Auto - CI | Functional, stable, critical |
| Non-blocking | No PR block | Reviewed per PR | Human review | Visual, perf, or structurally flaky |

## Decision Tree: Test double selection — mock, stub, spy, or real dependency?

**When this applies:** writing a unit or integration test that has a dependency on an external system, database, time, or another module. Choosing the wrong test double produces brittle tests or false passes.

**Last verified:** 2026-06-05 against Gerard Meszaros "xUnit Test Patterns" and Playwright/Jest test double patterns.

```mermaid
flowchart TD
    START[A dependency in a test] --> Q1{Is the dependency the subject under test?}
    Q1 -->|yes, testing the integration| REAL[Use the real dep or a high-fidelity container via Testcontainers]
    Q1 -->|no, it is infrastructure| Q2{Do you need to verify HOW it was called?}
    Q2 -->|yes, assert call arguments or order| MOCK[Mock - verify the interaction]
    Q2 -->|no| Q3{Does the test need realistic behavior or stateful responses?}
    Q3 -->|yes, e.g. in-memory DB or queue| FAKE[Fake - working implementation without I/O]
    Q3 -->|no, just a canned return value| Q4{Are you checking branching on the return value?}
    Q4 -->|yes| STUB[Stub - fixed canned response]
    Q4 -->|no| SPY[Spy - real call but observed]
```

**Rationale per leaf:**
- *Real / Testcontainers* — when the integration itself is the point; a mock of the DB is not a test of the DB interaction.
- *Mock* — when you need to assert the dependency was called correctly (e.g., the right API method was called with the right args).
- *Fake* — when you need stateful behavior (insert, query, delete working together) without I/O cost.
- *Stub* — when you just need a predictable return value to exercise a branch.
- *Spy* — when you want to observe calls on a real implementation without replacing it.

**Tradeoffs summary:**

| Method | Cost / time | Blast radius | Approval gate? | Use when |
|---|---|---|---|---|
| Real dep / Testcontainers | Slow startup | High - tests real integration | None | Integration point is the subject |
| Fake | Fast, stateful | Low - in-process | None | Need stateful behavior without I/O |
| Mock | Fast | Low | None | Must verify interaction contract |
| Stub | Fastest | Lowest | None | Just need a canned return value |

## Decision Tree: E2E test failure — fix, quarantine, or delete?

**When this applies:** an E2E test is failing in CI and the team must decide the immediate response.

**Last verified:** 2026-06-05 against qa-test-automation plugin house opinions and general flaky-test management practice.

```mermaid
flowchart TD
    START[An E2E test is failing] --> Q1{Does it fail consistently - not flaky?}
    Q1 -->|yes, consistent failure| Q2{Does it catch a real product defect?}
    Q2 -->|yes| FIX_PRODUCT[Fix the product defect - the test did its job]
    Q2 -->|no, test is wrong| FIX_TEST[Fix the test - false failure]
    Q1 -->|no, intermittent| Q3{Is it on the critical-journey list?}
    Q3 -->|yes| Q4{Root cause identifiable and fixable within 1 sprint?}
    Q4 -->|yes| FIX_DETERMINISM[Fix determinism - condition wait, isolation, fake clock]
    Q4 -->|no| QUARANTINE[Quarantine with owner and deadline - max 2 sprints]
    Q3 -->|no, not critical| Q5{Is anyone willing to own the fix?}
    Q5 -->|yes| QUARANTINE
    Q5 -->|no| DELETE[Delete - an unmaintained test protects nothing]
    QUARANTINE --> DEADLINE{Deadline reached?}
    DEADLINE -->|fixed| RESTORE[Restore to suite]
    DEADLINE -->|still flaky| DELETE
```

**Rationale per leaf:**
- *Fix the product defect* — the test passed its purpose; celebrate and fix the product.
- *Fix the test* — false failures erode suite trust; fix immediately.
- *Fix determinism* — a fixable flaky critical test gets a real fix, not a quarantine.
- *Quarantine with owner* — a flaky critical test that can't be immediately fixed stays visible and owned, not silently ignored.
- *Delete* — an unowned, non-critical flaky test is better gone than ignored; it trains engineers to dismiss red CI.

**Tradeoffs summary:**

| Method | Cost / time | Blast radius | Approval gate? | Use when |
|---|---|---|---|---|
| Fix product | Product work | Removes real defect | Yes - code review | Consistent failure on correct test |
| Fix test | Test work | Restores signal | Test review | False failure |
| Fix determinism | Sprint capacity | Restores critical signal | Test review | Flaky critical journey |
| Quarantine | Low - tracked | Reduces noise | Owner + deadline | Flaky, owner assigned |
| Delete | Minimal | Removes dead signal | PR review | No owner, non-critical |
