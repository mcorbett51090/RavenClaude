---
scenario_id: 2026-06-05-ice-cream-cone-slow-suite
contributed_at: 2026-06-05
plugin: qa-test-automation
product: generic
product_version: "unknown"
scope: likely-general
tags: [test-pyramid, ice-cream-cone, e2e, slow-suite, feedback-loop, parallelization]
confidence: high
reviewed: false
---

## Problem

A web team's CI suite took **47 minutes** and the team had stopped trusting it — PRs sat waiting, people merged on a green-ish "looks fine," and the suite still missed a class of validation bugs. Inventory: ~120 Selenium/Cypress E2E tests, ~40 integration tests, ~90 unit tests. The shape was an **ice-cream cone** (fat E2E layer on a thin unit base) — the exact inversion of the pyramid. Most of those 120 E2E tests were re-verifying form-validation and pricing-math logic *through the browser* — a 30-second full-stack round trip to assert something a 5ms unit test could have caught.

## Constraints context

- The E2E layer was where defects were *first written as tests* because "that's how QA validated it manually," so the suite calcified around the manual process, not the cheapest level.
- Shared CI runners; the E2E tier couldn't be naively parallelized because many tests mutated a shared seeded database (cross-test state coupling — also the #1 flake source here).
- Leadership read "we have 250 tests" as strong coverage; the *shape* of those 250 was the actual problem, and nobody was measuring level distribution.
- Re-platforming the E2E framework was floated as the fix ("Cypress is slow, switch to Playwright") — a tooling answer to a pyramid-shape problem.

## Attempts

- Tried: switching E2E from Cypress to Playwright for raw speed. Helped ~15% on wall-clock but did nothing about the root cause — 120 browser tests is 120 browser tests; a faster cone is still a cone. Rejected as the *primary* fix.
- Tried: just sharding the E2E tier across more runners. Blocked by the shared-database coupling — parallel shards corrupted each other's data. Sharding had to wait on test-data isolation, so it wasn't a standalone fix either.
- Tried (the move that worked): (1) measured the pyramid ratio first (unit:integration:e2e ≈ 90:40:120 — inverted) so the problem was *visible* and arguable to leadership, not a vibe. (2) Triaged the 120 E2E by *what defect each actually protects*: ~70 were asserting pure logic (validation rules, pricing/tax math, date handling) reachable at the unit level — those were **pushed down** to fast unit tests and the browser test deleted. (3) The ~50 genuine cross-system journeys stayed E2E but were cut to a short **critical-journey list** (checkout, login, payment) and given **per-test factory data + isolation** so they could finally be sharded. Result: ~90→160 unit, ~50 E2E, suite ≈ 9 minutes, and the validation-bug class started getting caught pre-merge.

## Resolution

**Respect the pyramid: push each assertion to the cheapest level that can catch the defect.** The fix wasn't a faster E2E framework — it was *moving 70 logic checks out of the browser entirely* and keeping E2E for the few genuine end-to-end journeys. The anti-pattern is the **ice-cream cone**: a fat slow E2E layer re-testing logic, which is slow, flaky (shared state), and expensive, while the cheap unit base stays thin. Tooling speed is a rounding error next to test-level distribution.

**Action for the next engineer:** before re-platforming or buying more runners, **measure the level distribution** (unit:integration:e2e) — an inverted ratio is the diagnosis. For each slow E2E test ask "what is the cheapest level that catches *this* defect?" via the [test-level-selection tree](../knowledge/qa-test-automation-decision-trees.md); a logic bug caught through the browser is a test that belongs at the unit level. Only after isolating test data can the residual E2E tier be sharded. Cross-reference: [`respect-the-test-pyramid`](../best-practices/respect-the-test-pyramid.md), [`e2e-critical-journey-list-is-short`](../best-practices/e2e-critical-journey-list-is-short.md), [`shard-and-parallelize-for-fast-feedback`](../best-practices/shard-and-parallelize-for-fast-feedback.md), and the `pyramid_ratio` mode of [`scripts/qa_suite_metrics.py`](../scripts/qa_suite_metrics.py).
