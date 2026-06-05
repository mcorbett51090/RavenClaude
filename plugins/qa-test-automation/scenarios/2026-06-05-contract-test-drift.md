---
scenario_id: 2026-06-05-contract-test-drift
contributed_at: 2026-06-05
plugin: qa-test-automation
product: generic
product_version: "unknown"
scope: likely-general
tags: [contract-test, pact, provider-verification, api-seam, integration, ci-gating]
confidence: medium
reviewed: false
---

## Problem

Two teams shared an HTTP seam: a checkout service (consumer) called an inventory service (provider). Both had green test suites, both deployed independently — and a provider release that renamed a JSON field (`available_qty` → `availableQuantity`) shipped to prod and **broke checkout at runtime** despite every test passing. The consumer's tests mocked the provider with the *old* shape; the provider's tests verified its *new* shape; nothing tested the **agreement between them**. Each side was green against its own private fiction of the other.

## Constraints context

- Separate repos, separate CI, separate deploy cadences — exactly the setup where a shared integration test is impractical and a contract test earns its keep.
- The consumer used hand-written mocks that nobody updated when the provider changed; the mock was a **stale snapshot of an assumption**, not a verified contract.
- A full spin-up-both-services integration test existed but ran nightly, was flaky, and caught this 14 hours too late (after the prod break).
- This is a **seam** the qa-test-automation plugin explicitly hands to `api-engineering` for the Pact/contract-testing craft — but the *decision to use a contract test here at all* is the test-level question this plugin owns.

## Attempts

- Tried: making the consumer's mocks "more thorough." Rejected — a richer hand-written mock is still a unilateral guess; it cannot detect a provider change because nothing re-verifies it against the real provider. More mock fidelity, same blind spot.
- Tried: promoting the nightly both-services integration test to a per-PR blocking gate. Too slow and too flaky for the merge gate (the [blocking-vs-non-blocking tree](../knowledge/qa-test-automation-decision-trees.md) sent it to a non-blocking job), and it still wouldn't fire on the *consumer's* PR — only on a deploy where both happened to be present.
- Tried (the move that worked): a **consumer-driven contract test** (Pact). The consumer publishes a pact (the exact request/response shape it depends on); the **provider's CI verifies every consumer's pact before it can deploy**. The field rename now fails the *provider's* build with "consumer checkout expects `available_qty`" — the break is caught on the side that caused it, before it ships, in seconds. Contract authoring + the broker wiring routed to `api-engineering/api-testing-engineer`; this plugin owned the call that a contract test (not a fatter mock, not a heavier integration test) was the right level.

## Resolution

**Contract-test the service seams — and verify the contract in the *provider's* CI, not just the consumer's.** A mock that isn't re-verified against the real provider is drift waiting to ship; two independently-green suites prove nothing about the agreement *between* them. The anti-pattern is treating a hand-written mock as if it were a contract — it's a private assumption that silently rots when the other side changes.

**Action for the next engineer:** when a boundary sits between two independently-deployed services, traverse the [test-level-selection tree](../knowledge/qa-test-automation-decision-trees.md) — a service-to-service seam routes to a **contract test**, not a fatter mock or a spin-up-both integration test. The load-bearing detail: the contract must be **verified in the provider's pipeline** so a breaking change fails the side that made it. The contract-testing mechanics (Pact, the broker, can-i-deploy) are owned by [`api-engineering/api-testing-engineer`](../../api-engineering/CLAUDE.md) — hand off the *how*, but make the *test-level call* here. Cross-reference: [`contract-test-the-service-seams`](../best-practices/contract-test-the-service-seams.md).
