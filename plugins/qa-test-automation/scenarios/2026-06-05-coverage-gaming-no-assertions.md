---
scenario_id: 2026-06-05-coverage-gaming-no-assertions
contributed_at: 2026-06-05
plugin: qa-test-automation
product: generic
product_version: "unknown"
scope: likely-general
tags: [coverage, mutation-testing, coverage-gaming, assertions, test-quality, ci-gating]
confidence: high
reviewed: false
---

## Problem

A team enforced an **85% line-coverage gate** in CI and hit it — the dashboard was green, leadership was reassured. Then a refund bug shipped: a sign was inverted in the refund calculation and **no test failed**, even though the refund module reported 92% line coverage. Investigation found the tests *executed* the refund code (so it counted as "covered") but **asserted almost nothing about the result** — `expect(refund).toBeDefined()` and a pile of calls with no meaningful checks. The coverage number measured *which lines ran*, not *whether a wrong answer would be caught*. The gate had trained people to write coverage-satisfying tests, not defect-catching ones.

## Constraints context

- The 85% gate was a hard merge-blocker, so engineers under deadline wrote the cheapest tests that moved the number — call the function, assert it didn't throw. This is **coverage-gaming**, and the gate incentivized it.
- Line coverage cannot distinguish "executed and verified" from "executed and ignored" — a test with zero assertions can still report 100% coverage of the code it runs.
- Raising the gate to 95% was on the table and would have made it *worse* — more pressure, more assertion-free tests.

## Attempts

- Tried: raising the coverage threshold 85% → 95%. Rejected in review — it doubles down on the metric that's being gamed; higher line coverage with no assertions is *more* false confidence, not less. Goodhart's law: the measure had become the target and stopped being a good measure.
- Tried: a manual review rule "every test must assert something." Unenforceable at scale and easy to satisfy trivially (`toBeDefined`), so it didn't restore real signal.
- Tried (the move that worked): added **mutation testing** (Stryker for JS here; PIT/mutmut are the JVM/Python equivalents) on the critical modules (refund, pricing, auth). Mutation testing deliberately introduces bugs — flips a sign, swaps `<` for `<=`, removes a line — and checks whether **a test fails**. A *surviving mutant* is a defect class the suite can't catch. The refund module's mutation score was **~30%** despite 92% line coverage — quantitative proof the tests didn't actually verify behavior. The team kept line coverage as a *floor* (don't ship untested code) but moved the *quality* bar to mutation score on the critical paths, and back-filled real assertions where mutants survived.

## Resolution

**Coverage % is a floor, not a goal — and line coverage measures execution, not verification.** 100% line coverage with no assertions tests nothing. The anti-pattern is making a line-coverage number the *quality* target: it's trivially gamed by assertion-free tests and gives false confidence that ships real bugs. **Mutation testing grades the tests** — it's the only metric here that answers "would a wrong answer actually be caught?"

**Action for the next engineer:** keep line/branch coverage as a *floor* to catch wholly-untested code, but never treat the number as proof of quality. On critical paths (money, auth, anything irreversible), add **mutation testing** (Stryker / PIT / mutmut) and track the **mutation score** — a high line-coverage / low mutation-score module is the signature of coverage-gaming and tells you exactly where assertions are missing. Cross-reference: [`coverage-is-a-floor-not-a-goal`](../best-practices/coverage-is-a-floor-not-a-goal.md), [`mutation-testing-grades-the-tests`](../best-practices/mutation-testing-grades-the-tests.md), [`assert-exactly-what-you-mean`](../best-practices/assert-exactly-what-you-mean.md).
