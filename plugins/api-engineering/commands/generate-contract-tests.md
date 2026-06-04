---
description: Generate contract tests and a mock from an API spec — consumer-driven contract tests (Pact/schema) that gate the provider's CI, a spec-driven mock (Prism/Postman) for parallel consumer dev, and a k6 load test asserted against an SLO.
argument-hint: "[path to the spec, or the consumer/provider pair to test]"
---

# Generate contract tests & a mock

You are running `/api-engineering:generate-contract-tests`. Build the test/mock setup for `$ARGUMENTS` following this plugin's `api-testing-engineer` discipline.

## When to use this

You want automated confidence that a change won't break a consumer, and a mock so consumers can build in parallel. For the design-time style gate, run `/api-engineering:lint-api-spec` first.

## Steps

1. **Pick the gate by risk** — traverse the test-type tree in [`../knowledge/api-testing-governance-decision-trees.md`](../knowledge/api-testing-governance-decision-trees.md): consumer-driven contract test (a known consumer could break), schema validation (drift), load (SLO), negative/fuzz (hostile input).
2. **Consumer-driven contract test** — the consumer publishes its expectations (Pact contract or schema assertions); the **provider's CI** verifies them and fails the build on a break, with a `can-i-deploy` gate. (`test-consumer-driven-contract-tests.md`)
3. **Mock from the contract** — generate a Prism or Postman mock straight from the spec so it stays honest; consumers point at it for parallel dev. The bundled **Postman MCP** can scaffold collections/specs/mocks — load its tools via `ToolSearch` first and treat generated artifacts as drafts. (`test-mock-from-the-contract.md`)
4. **Load test to an SLO** — a k6 script asserting a stated p95/rps + max-error-rate threshold, observing rate-limit and error-model behavior under load. (`test-load-test-to-an-slo.md`)
5. **Wire all gates into CI** with the failure modes each one catches.

## Guardrails

- "Our tests pass" ≠ "we didn't break anyone" — the contract test is consumer-owned for a reason.
- Don't hand-write a mock that duplicates the contract; generate it from the spec so it can't drift.
- A load test needs a stated SLO to be a gate, not a vanity benchmark.
- Never commit a real credential in a collection/test — inject from the environment and say so.
- Authorization-test design (proving a BOLA/BFLA negative 403s) co-owns with `api-security-engineer`; the verdict routes to `ravenclaude-core/security-reviewer`.
