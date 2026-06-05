# Prioritize tests by the risk of the behavior they protect

**Status:** Pattern
**Domain:** Test strategy
**Applies to:** `qa-test-automation`

---

## Why this exists

Writing tests in proportion to code complexity or file size produces a test suite that covers the implementation uniformly — but defects don't distribute uniformly. A trivial CRUD endpoint with low user traffic gets the same test investment as a payment flow with high blast radius and complex business rules. Risk-based prioritization allocates test effort where the cost of a missed defect is highest, and consciously trades test coverage for test impact.

## How to apply

Score behaviors on two axes: **probability of defect** (complexity, change frequency, external dependencies) and **impact of failure** (revenue, user-facing, data loss, regulatory). High × high = invest heavily; low × low = test lightly or not at all.

| Behavior | Defect probability | Failure impact | Test depth |
|---|---|---|---|
| Payment processing | High (complex logic) | Critical (revenue, compliance) | Unit + integration + E2E + chaos |
| User login | Medium (third-party auth) | High (all users) | Unit + integration + E2E |
| User profile display | Low (read-only) | Low (cosmetic) | Unit only |
| Admin CSV export | Low | Low (internal tool) | Smoke test |
| Health check endpoint | Very low | N/A (infra) | None — it's a constant |

```python
# Risk matrix in code: annotate tests with risk level for reporting
import pytest

@pytest.mark.risk(level="critical", domain="payment")
def test_payment_processes_with_valid_card():
    ...

@pytest.mark.risk(level="low", domain="display")
def test_profile_renders_username():
    ...
```

**Do:**
- Run risk-based prioritization during test strategy planning, not after the fact.
- Review the risk matrix quarterly — a feature that was low-risk at launch may become high-risk as adoption grows.
- Use mutation testing (see `mutation-testing-grades-the-tests.md`) on the highest-risk code to verify that tests actually catch defects.
- Communicate the "we chose not to test this deeply" decisions explicitly so they can be revisited.

**Don't:**
- Treat 100% line coverage as the proxy for risk coverage — a trivially-tested critical path is worse than a well-tested partial path.
- Use risk scores as an excuse to skip E2E tests on critical journeys; risk-based means prioritized, not eliminated.
- Let the risk matrix go stale — a payment flow refactored last quarter may have a different defect probability today.

## Edge cases / when the rule does NOT apply

Regulatory contexts (PCI-DSS, HIPAA, FDA 21 CFR Part 11) may mandate specific test coverage levels independent of risk scoring. Risk-based prioritization still applies within those bounds to allocate the effort not mandated by compliance.

## See also

- [`../agents/test-strategy-architect.md`](../agents/test-strategy-architect.md) — owns risk-based test prioritization and the test strategy document.
- [`./decide-explicitly-what-not-to-test.md`](./decide-explicitly-what-not-to-test.md) — risk-based prioritization is the framework for explicit decisions about what to skip.

## Provenance

Codifies risk-based testing (RBT) methodology from James Bach and Michael Bolton's "Rapid Software Testing" and the ISTQB risk-based test management techniques.

---

_Last reviewed: 2026-06-05 by `claude`_
