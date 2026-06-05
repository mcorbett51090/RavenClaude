---
name: flaky-test-triage
description: "Structured procedure for detecting, classifying, and eliminating flaky tests — covers quarantine mechanics, root-cause patterns (timing, state, network, ordering), and the fix or delete decision."
---

# Flaky Test Triage

## When to Use This

A test passes sometimes and fails sometimes with no code change. Use this skill to move from "just re-run it" (which normalizes the flakiness) to a quarantined, owned, time-bounded remediation.

## Step 1 — Confirm It Is Truly Flaky

Run the test 10× in isolation (no parallelism, clean state each time):

```shell
# Playwright example
npx playwright test <test-file> --repeat-each=10

# Jest example
npx jest <test-file> --testNamePattern "<test-name>" --forceExit
```

If it fails in isolation, it's not a flake — it's a real regression. Treat it as a bug.

If it only fails when run with the full suite, it is an **ordering/state pollution** flake (see classification below).

## Step 2 — Classify the Root Cause

| Pattern | Observable | Typical cause |
|---|---|---|
| **Timing** | Fails with "element not found" / "timeout" / "assertion on async value" | Fixed `sleep`; polling without a condition; race between UI render and assertion |
| **State pollution** | Fails after specific other tests; passes in isolation | Shared database rows; global singletons; missing teardown |
| **Network/external** | Fails with connection errors; highly environment-dependent | Real HTTP call to staging/prod; uncontrolled third-party API |
| **Order-dependent** | Fails only in full-suite run, order varies | Test A leaves dirty state; Test B depends on Test A's setup |
| **Resource contention** | Fails only in parallel runs; passes serially | Port conflicts; file-system races; shared fixtures with mutation |
| **Environment-sensitive** | Fails only in CI, passes locally | Different timezone/locale; different clock skew; different file-system case sensitivity |

## Step 3 — Quarantine Immediately

While investigating, quarantine so the failing test doesn't pollute the suite's signal:

```typescript
// Playwright
test.fixme('should submit order', async ({ page }) => { ... });
// add a tracking comment: owner, issue link, removal deadline

// Jest
test.skip('should submit order', () => { ... });
// or use jest-circus's fixme plugin

// pytest
@pytest.mark.skip(reason="flaky: timing issue, owner: @alice, deadline: 2026-06-19, issue: #1234")
```

**Quarantine rules:**
- One named owner per flaky test.
- A deadline: fix or delete within 2 sprint cycles (≈ 4 weeks).
- Linked to a tracking issue.
- Never leave it quarantined without a date — the graveyard grows.

## Step 4 — Fix by Root Cause

**Timing:**
```typescript
// Wrong
await page.click('#submit');
await page.waitForTimeout(2000);

// Right
await page.click('#submit');
await page.waitForSelector('[data-testid="confirmation"]', { state: 'visible' });
```

**State pollution:**
- Add `beforeEach`/`afterEach` teardown that resets all shared state.
- Use test-scoped database transactions that roll back after each test (if your ORM supports it).
- Inject unique identifiers (UUIDs) per test run to namespace shared resources.

**Network/external:**
- Replace real HTTP calls with a test double (MSW for browsers/Node; WireMock for Java; `responses` for Python requests).
- If you must hit real endpoints, run those tests in a separate suite tagged `[integration]` and exclude them from the fast gate.

**Order-dependent:**
- Run the suite with `--randomize` to surface ordering dependencies.
- Identify the "dirty" test with bisect: `pytest --randomly-seed=<seed>`.
- Add explicit teardown to the dirty test; never rely on test ordering.

## Step 5 — Fix or Delete Decision

| Situation | Decision |
|---|---|
| Test covers real behavior; fix is clear | Fix |
| Test covers real behavior; fix takes > 1 sprint | Quarantine with owner + deadline, keep in backlog |
| Test duplicates coverage of a more stable test | Delete |
| Test covers behavior no longer in the product | Delete |
| Test has been quarantined > 2 sprint cycles with no owner | Delete (the behavior it tested should be covered elsewhere or added back properly) |

**Never leave a quarantined test without a deletion date.**

## Pitfalls

- Re-running in CI without tracking — every re-run that passes trains the team to ignore red and hides real regressions behind "it'll probably pass next run."
- Adding `sleep` to fix a timing flake — it makes the test slower and often still flaky under load; wait on observable state instead.
- Fixing the flake without removing the `fixme` annotation — the test runs but is forever marked broken.
- Quarantining without an owner — the test accumulates in the skip list and coverage silently drops.

## See Also

- [`../../agents/test-infrastructure-engineer.md`](../../agents/test-infrastructure-engineer.md) — flaky-test detection and quarantine infrastructure
- [`../../agents/e2e-automation-engineer.md`](../../agents/e2e-automation-engineer.md) — resilient selectors and wait-on-condition patterns
