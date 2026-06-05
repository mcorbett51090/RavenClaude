# Every test has a named owner — ownership is tracked in code, not in memory

**Status:** Pattern
**Domain:** Test infrastructure / quality governance
**Applies to:** `qa-test-automation`

---

## Why this exists

When a test fails intermittently, "who owns this test?" is the first question and often has no fast answer. The failure gets ignored because there's no clear accountable party. Ownership tracked in code (as an annotation, a CODEOWNERS entry, or a metadata tag) means every failure routes to a person or team immediately, without a detective process. It also makes the test roster auditable: you can query "which tests have no owner?" and clean them up.

## How to apply

Annotate tests with ownership metadata at the test or suite level. Use CODEOWNERS for file-level ownership, and test metadata annotations for more granular ownership within a shared test file.

```typescript
// Playwright: ownership in the test file header and per-suite
import { test } from '@playwright/test';

// File-level: also add to .github/CODEOWNERS
// tests/checkout/checkout.spec.ts → @checkout-team

test.describe('Checkout: payment flow', {
  annotation: [
    { type: 'owner', description: 'checkout-team' },
    { type: 'risk', description: 'critical' },
    { type: 'jira', description: 'CHECKOUT-1234' },
  ]
}, () => {
  test('completes payment with valid card', async ({ page }) => {
    // ...
  });
});
```

```python
# pytest with custom markers for ownership
import pytest

@pytest.mark.owner("checkout-team")
@pytest.mark.risk("critical")
class TestCheckoutPayment:
    def test_completes_payment_with_valid_card(self, client):
        ...
```

```
# .github/CODEOWNERS — file-level ownership
tests/checkout/          @checkout-team
tests/auth/              @auth-team
tests/shared/            @test-infrastructure-team
```

**Do:**
- Enforce the ownership annotation in CI — fail on any test file missing an owner.
- Route flaky-test Slack/PagerDuty notifications to the team in the `owner` annotation.
- Review the ownership roster quarterly; teams that no longer exist need a handover.

**Don't:**
- Use a single "QA team" as the owner for all tests — that's no owner.
- Let CODEOWNERS drift out of date (bot reviews won't route correctly).
- Mark ownership as an email address that bounces when the person leaves.

## Edge cases / when the rule does NOT apply

Test infrastructure tests (testing the test framework itself, CI configuration tests) are owned by the test-infrastructure-engineer team — this is legitimate shared ownership because the scope is the framework, not a product domain.

## See also

- [`../agents/test-infrastructure-engineer.md`](../agents/test-infrastructure-engineer.md) — owns the tooling for tracking and enforcing test ownership.
- [`./quarantine-is-a-deadline-not-a-graveyard.md`](./quarantine-is-a-deadline-not-a-graveyard.md) — quarantine requires a named owner; without ownership, the quarantine is a graveyard.

## Provenance

Codifies the "you build it, you own it" operational model applied to test authoring, and the GitHub CODEOWNERS convention for automated review routing.

---

_Last reviewed: 2026-06-05 by `claude`_
