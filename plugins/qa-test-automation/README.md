# QA & Test Automation

The **qa-test-automation** plugin — building a test strategy that catches real defects cheaply — the test pyramid, deterministic E2E automation, test data and environments, coverage that means something, and flake control.

## Agents

- **`test-strategy-architect`** — The test strategy: which test level catches which defect class, the pyramid shape, what to test vs not, coverage philosophy (mutation over line %), and the risk-based prioritization
- **`e2e-automation-engineer`** — End-to-end and integration test authoring: Playwright/Cypress flows, resilient selectors (roles/test-ids over CSS/XPath), waiting on conditions not sleeps, page-object/fixture structure, and the critical-journey selection
- **`test-infrastructure-engineer`** — Test infrastructure: test data management (factories/seeding), ephemeral environments and service virtualization, flaky-test detection and quarantine, parallelization/sharding, and coverage/mutation reporting in CI

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install qa-test-automation@ravenclaude
```

## Seams

- **Consumer-driven contract tests between services** → `api-engineering/api-testing-engineer` owns Pact/contract testing; we own the broader pyramid and E2E.
- **Where tests run, sharding, required checks** → `devops-cicd/pipeline-engineer` (we define *what* to test; they wire *where* it runs).
- **The UI being tested (components, accessibility-in-code)** → `frontend-engineering`; selectors and testability are a shared concern.
- **Lightweight per-task QA / acceptance checks** → this plugin **deepens** `ravenclaude-core/tester-qa`; the litmus test is ad-hoc check → core, the test *strategy & automation* → here.
- **Load/performance testing of an API** → `api-engineering` (k6) and `observability-sre` (SLOs); functional E2E is ours.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`.
