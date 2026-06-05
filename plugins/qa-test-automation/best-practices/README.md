# qa-test-automation — best-practice docs

Named, citable rules for the `qa-test-automation` plugin's specialists. Each file is **one rule**.

---

## Index

_22 rules._

| Doc | Status | Use when |
|---|---|---|
| [`a-flaky-test-is-a-broken-test.md`](./a-flaky-test-is-a-broken-test.md) | Absolute rule | Any intermittently-failing test appears in CI |
| [`automate-accessibility-and-visual-where-it-earns-it.md`](./automate-accessibility-and-visual-where-it-earns-it.md) | Pattern | Adding automated accessibility or visual checks |
| [`shard-and-parallelize-for-fast-feedback.md`](./shard-and-parallelize-for-fast-feedback.md) | Pattern | Test suite runtime exceeds the team's feedback tolerance |
| [`respect-the-test-pyramid.md`](./respect-the-test-pyramid.md) | Absolute rule | Reviewing the ratio of unit / integration / E2E tests |
| [`quarantine-is-a-deadline-not-a-graveyard.md`](./quarantine-is-a-deadline-not-a-graveyard.md) | Absolute rule | Moving a flaky test to quarantine |
| [`coverage-is-a-floor-not-a-goal.md`](./coverage-is-a-floor-not-a-goal.md) | Absolute rule | Interpreting coverage reports |
| [`contract-test-the-service-seams.md`](./contract-test-the-service-seams.md) | Pattern | Testing a boundary between two deployed services |
| [`decide-explicitly-what-not-to-test.md`](./decide-explicitly-what-not-to-test.md) | Pattern | Planning or reviewing a test strategy |
| [`determinism-or-its-not-a-test.md`](./determinism-or-its-not-a-test.md) | Absolute rule | Writing any test that touches time, network, or randomness |
| [`isolate-test-data.md`](./isolate-test-data.md) | Absolute rule | Writing any test that reads from or writes to a data store |
| [`test-behavior-not-implementation.md`](./test-behavior-not-implementation.md) | Absolute rule | Writing or reviewing any test |
| [`mutation-testing-grades-the-tests.md`](./mutation-testing-grades-the-tests.md) | Pattern | Evaluating whether tests actually catch defects |
| [`page-objects-own-selectors.md`](./page-objects-own-selectors.md) | Pattern | Structuring E2E test code |
| [`test-ids-over-css-selectors.md`](./test-ids-over-css-selectors.md) | Absolute rule | Writing selectors in any E2E test |
| [`ephemeral-environments-for-integration-tests.md`](./ephemeral-environments-for-integration-tests.md) | Absolute rule | Setting up integration test infrastructure |
| [`risk-based-test-prioritization.md`](./risk-based-test-prioritization.md) | Pattern | Allocating test effort across a product |
| [`test-data-factories-not-fixtures.md`](./test-data-factories-not-fixtures.md) | Pattern | Managing test data for integration or E2E tests |
| [`assert-exactly-what-you-mean.md`](./assert-exactly-what-you-mean.md) | Pattern | Writing or reviewing test assertions |
| [`e2e-critical-journey-list-is-short.md`](./e2e-critical-journey-list-is-short.md) | Pattern | Deciding whether to add a new E2E test |
| [`track-test-ownership-in-code.md`](./track-test-ownership-in-code.md) | Pattern | Adding or auditing tests in CI |
| [`performance-budget-test-for-regressions.md`](./performance-budget-test-for-regressions.md) | Pattern | Protecting key paths from performance regression |
| [`visual-regression-is-a-separate-gate.md`](./visual-regression-is-a-separate-gate.md) | Pattern | Adding visual regression tests to CI |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — plugin team constitution.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs.
